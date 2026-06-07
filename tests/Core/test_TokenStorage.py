import json
import os

from ff_digikey_api.Core.TokenStorage.TokenStorage import TokenStorage
from ff_digikey_api.Structs.TokenData import TokenData


class TestTokenStorageSaveLoad:
    def test_save_and_load_roundtrip(self, tmp_path):
        file_path = str(tmp_path / "tokens.json")
        storage = TokenStorage(file_path=file_path)
        token_data = TokenData(
            access_token="abc123",
            refresh_token="ref456",
            expires=1700000000.0,
            refresh_token_expires=1700100000.0,
            token_type="Bearer",
        )
        storage.save(token_data)
        loaded = storage.load()
        assert loaded is not None
        assert loaded.access_token == "abc123"
        assert loaded.refresh_token == "ref456"
        assert loaded.expires == 1700000000.0
        assert loaded.refresh_token_expires == 1700100000.0
        assert loaded.token_type == "Bearer"

    def test_save_creates_json_file(self, tmp_path):
        file_path = str(tmp_path / "tokens.json")
        storage = TokenStorage(file_path=file_path)
        token_data = TokenData(access_token="abc")
        storage.save(token_data)
        assert os.path.exists(file_path)
        with open(file_path, "r") as f:
            data = json.load(f)
        assert data["access_token"] == "abc"


class TestTokenStorageLoad:
    def test_load_file_not_exists(self, tmp_path):
        file_path = str(tmp_path / "nonexistent.json")
        storage = TokenStorage(file_path=file_path)
        result = storage.load()
        assert result is None


class TestTokenStorageClear:
    def test_clear_removes_file(self, tmp_path):
        file_path = str(tmp_path / "tokens.json")
        storage = TokenStorage(file_path=file_path)
        token_data = TokenData(access_token="abc")
        storage.save(token_data)
        assert os.path.exists(file_path)
        storage.clear()
        assert not os.path.exists(file_path)

    def test_clear_nonexistent_file(self, tmp_path):
        file_path = str(tmp_path / "nonexistent.json")
        storage = TokenStorage(file_path=file_path)
        # clear on non-existent file should not raise
        storage.clear()


class TestTokenStorageExists:
    def test_exists_true(self, tmp_path):
        file_path = str(tmp_path / "tokens.json")
        storage = TokenStorage(file_path=file_path)
        token_data = TokenData(access_token="abc")
        storage.save(token_data)
        assert storage.exists() is True

    def test_exists_false(self, tmp_path):
        file_path = str(tmp_path / "nonexistent.json")
        storage = TokenStorage(file_path=file_path)
        assert storage.exists() is False
