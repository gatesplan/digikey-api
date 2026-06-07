from ff_digikey_api.Structs.DigiKeyConfig import DigiKeyConfig


class TestDigiKeyConfig:
    def test_defaults(self):
        config = DigiKeyConfig(client_id="cid", client_secret="csec")
        assert config.storage_path == "token_storage.json"
        assert config.sandbox is False

    def test_custom_values(self):
        config = DigiKeyConfig(
            client_id="my_id",
            client_secret="my_secret",
            storage_path="custom.json",
            sandbox=True,
        )
        assert config.client_id == "my_id"
        assert config.client_secret == "my_secret"
        assert config.storage_path == "custom.json"
        assert config.sandbox is True
