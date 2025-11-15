import json
import os
from pathlib import Path
from datetime import datetime
from typing import Literal
from cryptography.fernet import Fernet

from core import GameState


ENCRYPTED_FILE_HEADER = b"ENCSAVEv1\n"


class SaveManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SaveManager, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        mode: Literal["development", "production"] = "development",
        save_dir: str = "saves",
        prefix: str = "save",
        encryption_key: bytes | None = None,
    ):
        self.mode = mode
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.prefix = prefix

        if encryption_key is None:
            encryption_key = os.getenv("SAVE_AES_KEY").encode("utf-8")

        if self.mode == "production":
            if encryption_key is None:
                raise ValueError("Encryption key must be provided in production mode")
            self.fernet = Fernet(encryption_key)
        else:
            self.fernet = None

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def list_saves(self) -> list[Path]:
        """Returns save files sorted newest-first."""
        saves = list(self.save_dir.glob(f"{self.prefix}_*"))
        return sorted(saves, reverse=True)

    def save(self, state: GameState) -> Path:
        """Saves game state depending on mode (encrypted or raw JSON)."""
        timestamp = self._timestamp()
        file_path = self.save_dir / f"{self.prefix}_{timestamp}.sav"

        json_data = state.model_dump_json(indent=2)

        if self.mode == "production":
            encrypted = self.fernet.encrypt(json_data.encode("utf-8"))
            file_path.write_bytes(ENCRYPTED_FILE_HEADER + encrypted)
        elif self.mode == "development":
            file_path.write_text(json_data, encoding="utf-8")
        else:
            raise RuntimeError(f"Unknown save mode. Got: {self.mode}, Available options: 'production', 'development'.")

        return file_path

    def load(self, file_path: Path | None = None) -> GameState | None:
        """Loads the newest save or a specific one depending on mode."""
        try:
            if file_path is None:
                saves = self.list_saves()
                if not saves:
                    return None
                file_path = saves[0]

            data = file_path.read_bytes()

            if data.startswith(ENCRYPTED_FILE_HEADER):
                encrypted_payload = data[len(ENCRYPTED_FILE_HEADER):]
                decrypted = self.fernet.decrypt(encrypted_payload).decode("utf-8")
                return GameState.model_validate_json(decrypted)

            text = data.decode("utf-8")
            return GameState.model_validate_json(text)

        except json.JSONDecodeError as e:
            print(f"Invalid save format: {e}")
            return None

        except Exception as e:
            print(f"Could not load save. {e}")
            return None
