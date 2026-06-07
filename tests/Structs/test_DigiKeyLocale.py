from ff_digikey_api.Structs.DigiKeyLocale import DigiKeyLocale
from ff_digikey_api.Constants.Headers import LOCALE_LANGUAGE, LOCALE_CURRENCY, LOCALE_SITE


class TestDigiKeyLocale:
    def test_defaults(self):
        locale = DigiKeyLocale()
        assert locale.language == "en"
        assert locale.currency == "USD"
        assert locale.site == "US"

    def test_to_headers(self):
        locale = DigiKeyLocale(language="ko", currency="KRW", site="KR")
        headers = locale.to_headers()
        assert headers[LOCALE_LANGUAGE] == "ko"
        assert headers[LOCALE_CURRENCY] == "KRW"
        assert headers[LOCALE_SITE] == "KR"

    def test_to_headers_default(self):
        locale = DigiKeyLocale()
        headers = locale.to_headers()
        assert headers[LOCALE_LANGUAGE] == "en"
        assert headers[LOCALE_CURRENCY] == "USD"
        assert headers[LOCALE_SITE] == "US"
