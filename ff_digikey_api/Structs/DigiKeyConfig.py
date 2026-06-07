from dataclasses import dataclass


@dataclass
class DigiKeyConfig:
    client_id: str
    client_secret: str
    storage_path: str = "token_storage.json"
    sandbox: bool = False
