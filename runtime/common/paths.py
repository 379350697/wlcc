from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimePaths:
    root: Path

    @property
    def agent_dir(self) -> Path:
        return self.root / ".agent"

    @property
    def state_dir(self) -> Path:
        return self.agent_dir / "state"

    @property
    def tasks_state_dir(self) -> Path:
        return self.state_dir / "tasks"

    @property
    def supervision_state_dir(self) -> Path:
        return self.state_dir / "supervision"

    @property
    def index_path(self) -> Path:
        return self.state_dir / "index.json"

