"""Runtime task harness implementation."""
import json
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from .registry import DEFAULTS, get_meta

MAX_CONCURRENT_WORKERS = 4
CONSISTENCY_CHECK_SCRIPT = 'check_state_view_consistency.py'


@dataclass
class TrackedStep:
    script_name: str
    args: list
    meta: dict
    state: str = 'queued'
    output: str = ''
    error: Optional[str] = None
    exit_code: Optional[int] = None
    duration_ms: int = 0
    truncated: bool = False

    @property
    def cmd(self) -> list:
        script_dir = Path(__file__).resolve().parents[2] / 'scripts'
        return ['python3', str(script_dir / f'{self.script_name}.py')] + self.args

    def to_dict(self) -> dict:
        return {
            'script': self.script_name,
            'state': self.state,
            'exit_code': self.exit_code,
            'duration_ms': self.duration_ms,
            'output_chars': len(self.output),
            'truncated': self.truncated,
            'error': self.error,
            'meta': {
                'read_only': self.meta.get('read_only', False),
                'concurrent_safe': self.meta.get('concurrent_safe', False),
                'timeout': self.meta.get('timeout', 15),
            },
        }


@dataclass
class HarnessResult:
    success: bool
    steps: list
    total_duration_ms: int = 0
    consistency_check_passed: Optional[bool] = None
    failed_step: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'success': self.success,
            'total_duration_ms': self.total_duration_ms,
            'step_count': len(self.steps),
            'failed_step': self.failed_step,
            'consistency_check_passed': self.consistency_check_passed,
            'steps': self.steps,
        }


def _execute_step_standalone(cmd: list, timeout: int, max_chars: int, cwd: str) -> dict:
    start = time.monotonic()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        elapsed = int((time.monotonic() - start) * 1000)
        output = result.stdout
        truncated = False
        if len(output) > max_chars:
            output = output[:max_chars] + f'\n... [truncated at {max_chars} chars]'
            truncated = True
        return {
            'state': 'completed' if result.returncode == 0 else 'error',
            'output': output,
            'error': result.stderr if result.returncode != 0 else None,
            'exit_code': result.returncode,
            'duration_ms': elapsed,
            'truncated': truncated,
        }
    except subprocess.TimeoutExpired:
        elapsed = int((time.monotonic() - start) * 1000)
        return {'state': 'timeout', 'output': '', 'error': f'timeout after {timeout}s', 'exit_code': -1, 'duration_ms': elapsed, 'truncated': False}
    except Exception as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        return {'state': 'error', 'output': '', 'error': str(exc), 'exit_code': -2, 'duration_ms': elapsed, 'truncated': False}


class TaskHarness:
    def __init__(self, task_id: str, project_root: Path, enable_consistency_check: bool = True):
        self.task_id = task_id
        self.root = project_root
        self.enable_consistency_check = enable_consistency_check
        self.steps: list[TrackedStep] = []

    def add(self, script_name: str, args: list, meta_override: Optional[dict] = None) -> 'TaskHarness':
        meta = get_meta(script_name)
        if meta_override:
            meta.update(meta_override)
        self.steps.append(TrackedStep(script_name=script_name, args=args, meta=meta))
        return self

    def execute_all(self) -> HarnessResult:
        overall_start = time.monotonic()
        all_success = True
        failed_step = None
        groups = self._partition_steps()
        for group in groups:
            if group['type'] == 'concurrent' and len(group['steps']) > 1:
                success = self._run_concurrent(group['steps'])
            else:
                success = True
                for step in group['steps']:
                    if not self._run_serial(step):
                        success = False
                        break
            if not success:
                all_success = False
                for step in group['steps']:
                    if step.state in ('error', 'timeout'):
                        failed_step = step.script_name
                        break
                break
        consistency_passed = None
        if self.enable_consistency_check and all_success:
            consistency_passed = self._post_consistency_check()
            if not consistency_passed:
                all_success = False
                failed_step = 'consistency_check'
        total_ms = int((time.monotonic() - overall_start) * 1000)
        result = HarnessResult(success=all_success, steps=[step.to_dict() for step in self.steps], total_duration_ms=total_ms, consistency_check_passed=consistency_passed, failed_step=failed_step)
        self._write_execution_log(result)
        return result

    def _partition_steps(self) -> list[dict]:
        groups = []
        current_batch = []
        for step in self.steps:
            if step.meta.get('read_only') and step.meta.get('concurrent_safe'):
                current_batch.append(step)
                if len(current_batch) >= MAX_CONCURRENT_WORKERS:
                    groups.append({'type': 'concurrent', 'steps': current_batch})
                    current_batch = []
            else:
                if current_batch:
                    groups.append({'type': 'concurrent', 'steps': current_batch})
                    current_batch = []
                groups.append({'type': 'serial', 'steps': [step]})
        if current_batch:
            groups.append({'type': 'concurrent', 'steps': current_batch})
        return groups

    def _run_serial(self, step: TrackedStep) -> bool:
        step.state = 'executing'
        result = _execute_step_standalone(step.cmd, step.meta.get('timeout', DEFAULTS['timeout']), step.meta.get('max_result_chars', DEFAULTS['max_result_chars']), str(self.root))
        step.state = result['state']
        step.output = result['output']
        step.error = result['error']
        step.exit_code = result['exit_code']
        step.duration_ms = result['duration_ms']
        step.truncated = result['truncated']
        return step.state == 'completed'

    def _run_concurrent(self, steps: list[TrackedStep]) -> bool:
        for step in steps:
            step.state = 'executing'
        all_success = True
        with ProcessPoolExecutor(max_workers=min(len(steps), MAX_CONCURRENT_WORKERS)) as pool:
            future_to_step = {
                pool.submit(_execute_step_standalone, step.cmd, step.meta.get('timeout', DEFAULTS['timeout']), step.meta.get('max_result_chars', DEFAULTS['max_result_chars']), str(self.root)): step
                for step in steps
            }
            for future in as_completed(future_to_step):
                step = future_to_step[future]
                try:
                    result = future.result()
                    step.state = result['state']
                    step.output = result['output']
                    step.error = result['error']
                    step.exit_code = result['exit_code']
                    step.duration_ms = result['duration_ms']
                    step.truncated = result['truncated']
                    if step.state != 'completed':
                        all_success = False
                        for sibling in future_to_step:
                            if not sibling.done():
                                sibling.cancel()
                except Exception as exc:
                    step.state = 'error'
                    step.error = str(exc)
                    all_success = False
        for step in steps:
            if step.state == 'executing':
                step.state = 'cancelled'
                step.error = 'cancelled by sibling abort'
        return all_success

    def _post_consistency_check(self) -> bool:
        script = self.root / 'scripts' / CONSISTENCY_CHECK_SCRIPT
        if not script.exists():
            return True
        try:
            result = subprocess.run(['python3', str(script)], capture_output=True, text=True, timeout=15, cwd=str(self.root))
            return result.returncode == 0
        except (subprocess.TimeoutExpired, Exception):
            return False

    def _write_execution_log(self, result: HarnessResult):
        log_dir = self.root / '.agent' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'harness_execution_log.jsonl'
        entry = {
            'timestamp': datetime.now().isoformat(timespec='seconds'),
            'taskId': self.task_id,
            'success': result.success,
            'total_duration_ms': result.total_duration_ms,
            'step_count': len(result.steps),
            'failed_step': result.failed_step,
            'consistency_check_passed': result.consistency_check_passed,
            'steps': result.steps,
        }
        with log_file.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + '\n')
