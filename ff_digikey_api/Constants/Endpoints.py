# DigiKey Products V4 API 엔드포인트

BASE_URL = "https://api.digikey.com/products/v4"
SANDBOX_BASE_URL = "https://sandbox-api.digikey.com/products/v4"
AUTH_URL = "https://api.digikey.com/v1/oauth2/authorize"
TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"
SANDBOX_AUTH_URL = "https://sandbox-api.digikey.com/v1/oauth2/authorize"
SANDBOX_TOKEN_URL = "https://sandbox-api.digikey.com/v1/oauth2/token"

# 엔드포인트 경로
KEYWORD_SEARCH = "/search/keyword"
PRODUCT_DETAILS = "/search/{product_number}/productdetails"
PRICING = "/search/{product_number}/pricing"
PRICING_OPTIONS = "/search/{product_number}/pricingoptionsbyquantity"
MEDIA = "/search/{product_number}/media"
ASSOCIATIONS = "/search/{product_number}/associations"
SUBSTITUTIONS = "/search/{product_number}/substitutions"
RECOMMENDED = "/search/{product_number}/recommendedproducts"
ALT_PACKAGING = "/search/{product_number}/alternatepackaging"
DIGIREEL_PRICING = "/search/{product_number}/digireelpricing"
MANUFACTURERS = "/search/manufacturers"
CATEGORIES = "/search/categories"
CATEGORY_BY_ID = "/search/categories/{category_id}"

# 검색 limit 기본값/상한 (모든 진입점 공통)
DEFAULT_SEARCH_LIMIT = 10
MAX_SEARCH_LIMIT = 50
