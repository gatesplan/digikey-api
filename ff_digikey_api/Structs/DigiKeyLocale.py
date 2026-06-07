from dataclasses import dataclass

from ff_digikey_api.Constants.Headers import LOCALE_LANGUAGE, LOCALE_CURRENCY, LOCALE_SITE


@dataclass
class DigiKeyLocale:
    language: str = "en"
    currency: str = "USD"
    site: str = "US"

    def to_headers(self) -> dict[str, str]:
        return {
            LOCALE_LANGUAGE: self.language,
            LOCALE_CURRENCY: self.currency,
            LOCALE_SITE: self.site,
        }
