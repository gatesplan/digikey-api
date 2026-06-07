from ff_digikey_api.Structs.ParametricFilterRequest import (
    ParameterFilter,
    ParametricFilterRequest,
)


class TestParameterFilter:
    def test_to_dict_single_value(self):
        pf = ParameterFilter(parameter_id=2085, value_ids=["345"])
        assert pf.to_dict() == {
            "ParameterId": 2085,
            "FilterValues": [{"Id": "345"}],
        }

    def test_to_dict_multiple_values(self):
        pf = ParameterFilter(parameter_id=2085, value_ids=["345", "346", "347"])
        d = pf.to_dict()
        assert d["ParameterId"] == 2085
        assert len(d["FilterValues"]) == 3
        assert d["FilterValues"][1] == {"Id": "346"}


class TestParametricFilterRequest:
    def test_to_dict_with_category(self):
        pf = ParameterFilter(parameter_id=2085, value_ids=["345"])
        req = ParametricFilterRequest(parameter_filters=[pf], category_id=52)
        d = req.to_dict()
        assert d["CategoryFilter"] == {"Id": "52"}
        assert len(d["ParameterFilters"]) == 1
        assert d["ParameterFilters"][0]["ParameterId"] == 2085

    def test_to_dict_without_category(self):
        pf = ParameterFilter(parameter_id=2085, value_ids=["345"])
        req = ParametricFilterRequest(parameter_filters=[pf])
        d = req.to_dict()
        assert "CategoryFilter" not in d
        assert len(d["ParameterFilters"]) == 1

    def test_to_dict_multiple_parameters(self):
        pf1 = ParameterFilter(parameter_id=2085, value_ids=["345"])
        pf2 = ParameterFilter(parameter_id=3050, value_ids=["200", "201"])
        req = ParametricFilterRequest(parameter_filters=[pf1, pf2], category_id=52)
        d = req.to_dict()
        assert len(d["ParameterFilters"]) == 2
        assert d["ParameterFilters"][1]["ParameterId"] == 3050
        assert len(d["ParameterFilters"][1]["FilterValues"]) == 2

    def test_from_match_results(self):
        matches = [
            {"parameter_id": 2085, "value_ids": ["100", "101"]},
            {"parameter_id": 3050, "value_ids": ["200"]},
        ]
        req = ParametricFilterRequest.from_match_results(matches, category_id=52)
        assert req.category_id == 52
        assert len(req.parameter_filters) == 2
        assert req.parameter_filters[0].parameter_id == 2085
        assert req.parameter_filters[0].value_ids == ["100", "101"]

    def test_from_match_results_no_category(self):
        matches = [{"parameter_id": 2085, "value_ids": ["100"]}]
        req = ParametricFilterRequest.from_match_results(matches)
        assert req.category_id is None
