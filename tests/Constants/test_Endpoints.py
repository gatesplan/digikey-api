from ff_digikey_api.Constants.Endpoints import (
    BASE_URL,
    SANDBOX_BASE_URL,
    AUTH_URL,
    TOKEN_URL,
    SANDBOX_AUTH_URL,
    SANDBOX_TOKEN_URL,
    KEYWORD_SEARCH,
    PRODUCT_DETAILS,
    PRICING,
    MANUFACTURERS,
    CATEGORIES,
    CATEGORY_BY_ID,
)


class TestEndpoints:
    def test_base_url(self):
        assert BASE_URL == "https://api.digikey.com/products/v4"

    def test_sandbox_base_url(self):
        assert SANDBOX_BASE_URL == "https://sandbox-api.digikey.com/products/v4"

    def test_auth_url(self):
        assert AUTH_URL == "https://api.digikey.com/v1/oauth2/authorize"

    def test_token_url(self):
        assert TOKEN_URL == "https://api.digikey.com/v1/oauth2/token"

    def test_sandbox_auth_url(self):
        assert SANDBOX_AUTH_URL == "https://sandbox-api.digikey.com/v1/oauth2/authorize"

    def test_sandbox_token_url(self):
        assert SANDBOX_TOKEN_URL == "https://sandbox-api.digikey.com/v1/oauth2/token"

    def test_keyword_search(self):
        assert KEYWORD_SEARCH == "/search/keyword"

    def test_product_details_has_placeholder(self):
        assert "{product_number}" in PRODUCT_DETAILS

    def test_pricing_has_placeholder(self):
        assert "{product_number}" in PRICING

    def test_manufacturers(self):
        assert MANUFACTURERS == "/search/manufacturers"

    def test_categories(self):
        assert CATEGORIES == "/search/categories"

    def test_category_by_id_has_placeholder(self):
        assert "{category_id}" in CATEGORY_BY_ID
