import json
from pathlib import Path
from datetime import datetime

from src.core import GameState


def _generate_timestamp() -> str:
    """Returns a filesystem-safe timestamp."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def list_saves(save_dir: str = "saves") -> list[Path]:
    """Returns all save files sorted newest-first."""
    save_path = Path(save_dir)
    if not save_path.exists():
        return []
    saves = list(save_path.glob("save_*.json"))
    return sorted(saves, reverse=True)


def save_game(
    state: GameState,
    save_dir: str = "saves",
    prefix: str = "save"
) -> Path:
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    timestamp = _generate_timestamp()
    file_path = save_path / f"{prefix}_{timestamp}.json"

    json_data = state.model_dump_json(indent=2)
    file_path.write_text(json_data, encoding="utf-8")

    return file_path


def load_game(
    save_file: Path | None = None,
    save_dir: str = "saves"
) -> GameState | None:
    try:
        if save_file is None:
            saves = list_saves(save_dir)
            if not saves:
                return None
            save_file = saves[0]

        json_content = Path(save_file).read_text(encoding="utf-8")
        state = GameState.model_validate_json(json_content)
        return state

    except json.JSONDecodeError as e:
        print(f"Invalid save format: {e}")
        return None
