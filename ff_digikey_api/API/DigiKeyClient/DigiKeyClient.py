import os

from loguru import logger

from ff_digikey_api.Constants.Endpoints import (
    BASE_URL, SANDBOX_BASE_URL, DEFAULT_SEARCH_LIMIT, MAX_SEARCH_LIMIT,
)
from ff_digikey_api.Structs.DigiKeyConfig import DigiKeyConfig
from ff_digikey_api.Structs.DigiKeyLocale import DigiKeyLocale
from ff_digikey_api.Structs.KeywordSearchRequest import KeywordSearchRequest
from ff_digikey_api.Structs.KeywordSearchResponse import KeywordSearchResponse
from ff_digikey_api.Structs.Product import Product
from ff_digikey_api.Structs.ProductPricingResponse import ProductPricingResponse
from ff_digikey_api.Structs.Manufacturer import Manufacturer
from ff_digikey_api.Structs.Category import Category
from ff_digikey_api.Structs.FilterOptions import FilterOptions
from ff_digikey_api.Structs.SortOptions import SortOptions
from ff_digikey_api.Structs.ParametricFilterRequest import ParametricFilterRequest
from ff_digikey_api.Util.ParametricExpression import parse_expression
from ff_digikey_api.Util.ParametricMatcher import match_filters
from ff_digikey_api.Core.HttpClient.HttpClient import HttpClient
from ff_digikey_api.Service.TokenManager.TokenManager import TokenManager
from ff_digikey_api.Service.ProductService.ProductService import ProductService


class DigiKeyClient:
    def __init__(self, client_id: str, client_secret: str, locale: DigiKeyLocale | None = None, **kwargs):
        sandbox = kwargs.get("sandbox", False)
        storage_path = kwargs.get("storage_path", "token_storage.json")

        self._config = DigiKeyConfig(
            client_id=client_id,
            client_secret=client_secret,
            storage_path=storage_path,
            sandbox=sandbox,
        )
        self._locale = locale if locale else DigiKeyLocale()
        base_url = SANDBOX_BASE_URL if sandbox else BASE_URL
        self._token_manager = TokenManager(self._config)
        self._http_client = HttpClient(base_url=base_url, client_id=client_id, locale=self._locale)
        self._product_service = ProductService(self._http_client)
        logger.info("DigiKeyClient 초기화")

    @classmethod
    def from_env(cls, env_file: str | None = None) -> "DigiKeyClient":
        # python-dotenv가 있으면 로드. 명시 경로가 CWD에 없으면 상위 디렉토리까지 탐색.
        if env_file:
            try:
                from dotenv import load_dotenv, find_dotenv
                path = env_file if os.path.exists(env_file) else find_dotenv(env_file, usecwd=True)
                if path:
                    load_dotenv(path)
            except ImportError:
                pass

        client_id = os.environ.get("DIGIKEY_CLIENT_ID")
        client_secret = os.environ.get("DIGIKEY_CLIENT_SECRET")
        if not client_id or not client_secret:
            hint = f" (checked env vars and env_file={env_file!r}; cwd={os.getcwd()})" if env_file \
                else f" (checked env vars; cwd={os.getcwd()})"
            raise ValueError("DIGIKEY_CLIENT_ID and DIGIKEY_CLIENT_SECRET must be set" + hint)

        language = os.environ.get("DIGIKEY_LANGUAGE", "en")
        currency = os.environ.get("DIGIKEY_CURRENCY", "USD")
        site = os.environ.get("DIGIKEY_SITE", "US")
        locale = DigiKeyLocale(language=language, currency=currency, site=site)

        sandbox_str = os.environ.get("DIGIKEY_SANDBOX", "false")
        sandbox = sandbox_str.lower() in ("true", "1", "yes")

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            locale=locale,
            sandbox=sandbox,
        )

    def is_authenticated(self) -> bool:
        return self._token_manager.is_authenticated()

    def authorize(self):
        logger.info("authorize 시작")
        self._token_manager.authorize()

    def search(self, keywords: str, limit: int = DEFAULT_SEARCH_LIMIT, offset: int = 0,
               filters: FilterOptions | None = None, sort: SortOptions | None = None) -> KeywordSearchResponse:
        logger.info(f"search 시작: keywords={keywords}")
        # DigiKey V4는 limit 1~50만 허용. 클라이언트단에서 클램프.
        limit = max(1, min(limit, MAX_SEARCH_LIMIT))
        offset = max(0, offset)
        token = self._token_manager.get_access_token()
        request = KeywordSearchRequest(keywords=keywords, limit=limit, offset=offset, filters=filters, sort=sort)
        return self._product_service.keyword_search(token, request)

    def detect_leaf_category(self, keywords: str, filters: FilterOptions | None = None) -> int | None:
        # 키워드 검색 결과의 첫 제품 카테고리에서 리프 카테고리 ID를 추출. 없으면 None.
        pre = self.search(keywords, limit=5, offset=0, filters=filters)
        for p in pre.products:
            if p.category and p.category.id:
                return self._find_leaf_category(p.category)
        return None

    def parametric_search(
        self,
        keywords: str,
        expressions: list[str] | str,
        limit: int = DEFAULT_SEARCH_LIMIT,
        offset: int = 0,
        filters: FilterOptions | None = None,
        sort: SortOptions | None = None,
        category_id: int | None = None,
    ) -> KeywordSearchResponse:
        logger.info(f"parametric_search: keywords={keywords}, expressions={expressions}")

        if isinstance(expressions, str):
            expressions = [expressions]
        parsed = [parse_expression(e) for e in expressions]

        # category 미지정 시: 검색 결과에서 리프 카테고리 추출
        if category_id is None:
            category_id = self.detect_leaf_category(keywords, filters)
            if category_id is None:
                raise ValueError("category not found: provide category_id explicitly")

        # probe: CategoryFilter 포함하여 ParametricFilters 획득
        probe_filters = FilterOptions(category_ids=[category_id])
        if filters:
            probe_filters = FilterOptions(
                manufacturer_ids=list(filters.manufacturer_ids),
                category_ids=[category_id] + [c for c in filters.category_ids if c != category_id],
                status_ids=list(filters.status_ids),
                packaging_ids=list(filters.packaging_ids),
                marketplace=filters.marketplace,
            )
        probe = self.search(keywords, limit=1, offset=0, filters=probe_filters)
        fo = probe.filter_options

        parametric_filters = fo.get("ParametricFilters")
        if not parametric_filters:
            raise ValueError("ParametricFilters not found in response (category_id={})".format(category_id))

        # 매칭
        matches = match_filters(parsed, parametric_filters)
        pfr = ParametricFilterRequest.from_match_results(matches, category_id=category_id)

        # 필터 적용 검색
        new_filters = FilterOptions(
            manufacturer_ids=list(probe_filters.manufacturer_ids),
            category_ids=list(probe_filters.category_ids),
            status_ids=list(probe_filters.status_ids),
            packaging_ids=list(probe_filters.packaging_ids),
            marketplace=probe_filters.marketplace,
            parametric_filter=pfr,
        )

        return self.search(keywords, limit=limit, offset=offset, filters=new_filters, sort=sort)

    @staticmethod
    def _find_leaf_category(category: Category) -> int:
        # 자식이 없을 때까지 첫 자식 경로를 따라 재귀해 실제 리프 ID를 반환.
        if category.children:
            return DigiKeyClient._find_leaf_category(category.children[0])
        return category.id

    def product_details(self, product_number: str) -> Product:
        logger.info(f"product_details 시작: product_number={product_number}")
        token = self._token_manager.get_access_token()
        return self._product_service.product_details(token, product_number)

    def pricing(self, product_number: str, **kwargs) -> ProductPricingResponse:
        logger.info(f"pricing 시작: product_number={product_number}")
        token = self._token_manager.get_access_token()
        return self._product_service.pricing(token, product_number, **kwargs)

    def associations(self, product_number: str) -> list[Product]:
        logger.info(f"associations 시작: product_number={product_number}")
        token = self._token_manager.get_access_token()
        return self._product_service.associations(token, product_number)

    def substitutions(self, product_number: str) -> list[Product]:
        logger.info(f"substitutions 시작: product_number={product_number}")
        token = self._token_manager.get_access_token()
        return self._product_service.substitutions(token, product_number)

    def recommended_products(self, product_number: str) -> list[Product]:
        logger.info(f"recommended_products 시작: product_number={product_number}")
        token = self._token_manager.get_access_token()
        return self._product_service.recommended_products(token, product_number)

    def alternate_packaging(self, product_number: str) -> list[Product]:
        logger.info(f"alternate_packaging 시작: product_number={product_number}")
        token = self._token_manager.get_access_token()
        return self._product_service.alternate_packaging(token, product_number)

    def media(self, product_number: str) -> dict:
        logger.info(f"media 시작: product_number={product_number}")
        token = self._token_manager.get_access_token()
        return self._product_service.media(token, product_number)

    def manufacturers(self) -> list[Manufacturer]:
        logger.info("manufacturers 시작")
        token = self._token_manager.get_access_token()
        return self._product_service.manufacturers(token)

    def categories(self) -> list[Category]:
        logger.info("categories 시작")
        token = self._token_manager.get_access_token()
        return self._product_service.categories(token)

    def close(self):
        logger.info("DigiKeyClient 종료")
        self._http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
