from ff_digikey_api.Structs.KeywordSearchRequest import KeywordSearchRequest
from ff_digikey_api.Structs.FilterOptions import FilterOptions
from ff_digikey_api.Structs.SortOptions import SortOptions
from ff_digikey_api.Structs.ParametricFilterRequest import (
    ParameterFilter,
    ParametricFilterRequest,
)


class TestKeywordSearchRequest:
    def test_to_dict_basic(self):
        req = KeywordSearchRequest(keywords="STM32")
        d = req.to_dict()
        assert d["Keywords"] == "STM32"
        assert d["Limit"] == 50
        assert d["Offset"] == 0
        assert "FilterOptionsRequest" not in d
        assert "SortOptions" not in d

    def test_to_dict_custom_limit_offset(self):
        req = KeywordSearchRequest(keywords="capacitor", limit=25, offset=10)
        d = req.to_dict()
        assert d["Limit"] == 25
        assert d["Offset"] == 10

    def test_to_dict_with_filters(self):
        filters = FilterOptions(manufacturer_ids=[497], category_ids=[771])
        req = KeywordSearchRequest(keywords="STM32", filters=filters)
        d = req.to_dict()
        assert "FilterOptionsRequest" in d
        filt = d["FilterOptionsRequest"]
        assert filt["ManufacturerFilter"] == [{"Id": "497"}]
        assert filt["CategoryFilter"] == [{"Id": "771"}]

    def test_to_dict_with_sort(self):
        sort = SortOptions(field="UnitPrice", sort_order="Descending")
        req = KeywordSearchRequest(keywords="STM32", sort=sort)
        d = req.to_dict()
        assert d["SortOptions"]["Field"] == "UnitPrice"
        assert d["SortOptions"]["SortOrder"] == "Descending"

    def test_to_dict_with_filters_and_sort(self):
        filters = FilterOptions(manufacturer_ids=[100])
        sort = SortOptions(field="UnitPrice")
        req = KeywordSearchRequest(keywords="res", filters=filters, sort=sort)
        d = req.to_dict()
        assert "FilterOptionsRequest" in d
        assert "SortOptions" in d


class TestFilterOptions:
    def test_to_dict_empty(self):
        f = FilterOptions()
        d = f.to_dict()
        assert "ManufacturerFilter" not in d
        assert "MarketPlaceFilter" not in d

    def test_to_dict_with_values(self):
        f = FilterOptions(
            manufacturer_ids=[1, 2],
            category_ids=[100],
            marketplace=True,
        )
        d = f.to_dict()
        assert d["ManufacturerFilter"] == [{"Id": "1"}, {"Id": "2"}]
        assert d["CategoryFilter"] == [{"Id": "100"}]
        assert d["MarketPlaceFilter"] == "MarketPlaceOnly"

    def test_to_dict_marketplace_false(self):
        f = FilterOptions(marketplace=False)
        d = f.to_dict()
        assert d["MarketPlaceFilter"] == "ExcludeMarketPlace"

    def test_to_dict_none_excluded(self):
        f = FilterOptions(manufacturer_ids=[1])
        d = f.to_dict()
        assert "MarketPlaceFilter" not in d

    def test_to_dict_status_and_packaging(self):
        f = FilterOptions(status_ids=[1, 2], packaging_ids=[3])
        d = f.to_dict()
        assert d["StatusFilter"] == [{"Id": "1"}, {"Id": "2"}]
        assert d["PackagingFilter"] == [{"Id": "3"}]


class TestSortOptions:
    def test_to_dict(self):
        s = SortOptions(field="UnitPrice", sort_order="Descending")
        d = s.to_dict()
        assert d == {"Field": "UnitPrice", "SortOrder": "Descending"}

    def test_defaults(self):
        s = SortOptions()
        d = s.to_dict()
        assert d == {"Field": "None", "SortOrder": "Ascending"}


class TestFilterOptionsWithParametric:
    def test_to_dict_with_parametric_filter(self):
        pf = ParametricFilterRequest(
            parameter_filters=[ParameterFilter(parameter_id=2085, value_ids=["345"])],
            category_id=52,
        )
        f = FilterOptions(category_ids=[52], parametric_filter=pf)
        d = f.to_dict()
        assert "ParameterFilterRequest" in d
        assert d["ParameterFilterRequest"]["CategoryFilter"] == {"Id": "52"}
        assert d["CategoryFilter"] == [{"Id": "52"}]

    def test_to_dict_without_parametric_filter(self):
        f = FilterOptions(category_ids=[52])
        d = f.to_dict()
        assert "ParameterFilterRequest" not in d

    def test_full_request_with_parametric(self):
        pf = ParametricFilterRequest(
            parameter_filters=[ParameterFilter(parameter_id=2085, value_ids=["345"])],
            category_id=52,
        )
        filters = FilterOptions(category_ids=[52], parametric_filter=pf)
        req = KeywordSearchRequest(keywords="resistor", filters=filters)
        d = req.to_dict()
        assert d["Keywords"] == "resistor"
        filt = d["FilterOptionsRequest"]
        assert filt["CategoryFilter"] == [{"Id": "52"}]
        assert "ParameterFilterRequest" in filt
        assert filt["ParameterFilterRequest"]["ParameterFilters"][0]["ParameterId"] == 2085
