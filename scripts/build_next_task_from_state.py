#!/usr/bin/env python3
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from runtime.scheduling.next_task import build_next_task_from_state_dir
from runtime.scheduling.next_task import write_state_views

state_dir = root / '.agent' / 'state' / 'tasks'
next_state = root / '.agent' / 'state' / 'next-task.json'
next_view = root / '.agent' / 'NEXT_TASK.md'
input_file = root / '.agent' / 'state' / 'next-task-input.json'
tasks_view = root / 'TASKS.md'
task_view_dir = root / '.agent' / 'tasks'
resume_view_dir = root / '.agent' / 'resume'

build_next_task_from_state_dir(state_dir, next_state, next_view, input_file)
write_state_views(state_dir, task_view_dir, resume_view_dir, tasks_view)
print(f'OK: wrote {next_state}')
print(f'OK: wrote {next_view}')
