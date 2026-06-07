from ff_digikey_api.Constants.Headers import (
    CLIENT_ID,
    LOCALE_LANGUAGE,
    LOCALE_CURRENCY,
    LOCALE_SITE,
    ACCOUNT_ID,
)


class TestHeaders:
    def test_all_headers_have_digikey_prefix(self):
        headers = [CLIENT_ID, LOCALE_LANGUAGE, LOCALE_CURRENCY, LOCALE_SITE, ACCOUNT_ID]
        for header in headers:
            assert header.startswith("X-DIGIKEY-"), f"{header} does not start with X-DIGIKEY-"

    def test_client_id(self):
        assert CLIENT_ID == "X-DIGIKEY-Client-Id"

    def test_locale_language(self):
        assert LOCALE_LANGUAGE == "X-DIGIKEY-Locale-Language"

    def test_locale_currency(self):
        assert LOCALE_CURRENCY == "X-DIGIKEY-Locale-Currency"

    def test_locale_site(self):
        assert LOCALE_SITE == "X-DIGIKEY-Locale-Site"

    def test_account_id(self):
        assert ACCOUNT_ID == "X-DIGIKEY-Account-Id"
