import json
import os
import threading
from pathlib import Path
from datetime import datetime
from typing import Literal
from cryptography.fernet import Fernet

from core import GameState


ENCRYPTED_FILE_HEADER = b"ENCSAVEv1\n"


class SaveManager:
    """
    Singleton class responsible for saving and loading game states,
    supporting both development (raw JSON) and production (encrypted) modes.

    This class ensures that only one instance exists (thread-safe) and manages
    save files in a specified directory. It can encrypt saves using Fernet
    symmetric encryption and provides utility methods to list, save, and load
    game states.

    Attributes
    ----------
    mode: Literal["development", "production"]
        Determines how game states are saved. In "development" mode, saves are
        stored as plain JSON. In "production" mode, saves are encrypted.
    save_dir: Path
        Directory where save files are stored.
    prefix: str
        Prefix for save filenames.
    fernet: Fernet
        Fernet encryption object used for encrypting and decrypting saves.

    Methods
    -------
    list_saves() -> list[Path]
        Returns a list of save files sorted by newest first.
    save(state: GameState) -> Path
        Saves the provided GameState instance to a file.
    load(file_path: Path | None = None) -> GameState | None
        Loads the newest or specified save file and returns the GameState instance.
    _timestamp() -> str
        Generates a timestamp string for save filenames.
    """

    _instance = None
    _initialized = False
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        mode: Literal["development", "production"] = "development",
        save_dir: str = "saves",
        prefix: str = "save",
        encryption_key: bytes | None = None,
    ):
        if not self._initialized:
            self.mode = mode
            self.save_dir = Path(save_dir)
            self.save_dir.mkdir(parents=True, exist_ok=True)
            self.prefix = prefix

            if encryption_key is None:
                encryption_key = os.getenv("SAVE_AES_KEY")
                if encryption_key is None:
                    raise ValueError("No encryption key provided and SAVE_AES_KEY is not set.")
                encryption_key = encryption_key.encode("utf-8")

            self.fernet = Fernet(encryption_key)

            self._initialized = True

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
                encrypted_payload = data[len(ENCRYPTED_FILE_HEADER) :]
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
