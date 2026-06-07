import pytest

from ff_digikey_api.Util.ParametricMatcher import match_filters
from ff_digikey_api.Util.ParametricExpression import parse_expression


SAMPLE_PARAMETRIC_FILTERS = [
    {
        "ParameterId": 2085,
        "ParameterName": "Resistance",
        "FilterValues": [
            {"ValueId": "100", "ValueName": "10 Ohms", "ProductCount": 500},
            {"ValueId": "101", "ValueName": "15 Ohms", "ProductCount": 300},
            {"ValueId": "102", "ValueName": "22 Ohms", "ProductCount": 200},
            {"ValueId": "103", "ValueName": "1.5 kOhms", "ProductCount": 150},
            {"ValueId": "104", "ValueName": "100 kOhms", "ProductCount": 100},
        ],
    },
    {
        "ParameterId": 3050,
        "ParameterName": "Tolerance",
        "FilterValues": [
            {"ValueId": "200", "ValueName": "0.1%", "ProductCount": 50},
            {"ValueId": "201", "ValueName": "1%", "ProductCount": 400},
            {"ValueId": "202", "ValueName": "5%", "ProductCount": 600},
        ],
    },
    {
        "ParameterId": 4000,
        "ParameterName": "Color",
        "FilterValues": [
            {"ValueId": "300", "ValueName": "Green", "ProductCount": 10},
            {"ValueId": "301", "ValueName": "Red", "ProductCount": 20},
            {"ValueId": "302", "ValueName": "Blue", "ProductCount": 15},
        ],
    },
]


class TestMatchFilters:
    def test_greater_than_resistance(self):
        exprs = [parse_expression("Resistance>15ohm")]
        results = match_filters(exprs, SAMPLE_PARAMETRIC_FILTERS)
        assert len(results) == 1
        assert results[0]["parameter_id"] == 2085
        assert results[0]["value_ids"] == ["102", "103", "104"]

    def test_greater_equal_resistance(self):
        exprs = [parse_expression("Resistance>=15ohm")]
        results = match_filters(exprs, SAMPLE_PARAMETRIC_FILTERS)
        assert results[0]["value_ids"] == ["101", "102", "103", "104"]

    def test_less_than_resistance(self):
        exprs = [parse_expression("Resistance<22ohm")]
        results = match_filters(exprs, SAMPLE_PARAMETRIC_FILTERS)
        assert results[0]["value_ids"] == ["100", "101"]

    def test_less_equal_resistance(self):
        exprs = [parse_expression("Resistance<=22ohm")]
        results = match_filters(exprs, SAMPLE_PARAMETRIC_FILTERS)
        assert results[0]["value_ids"] == ["100", "101", "102"]

    def test_equal_resistance_numeric(self):
        exprs = [parse_expression("Resistance=15ohm")]
        results = match_filters(exprs, SAMPLE_PARAMETRIC_FILTERS)
        assert results[0]["value_ids"] == ["101"]

    def test_not_equal_color(self):
        exprs = [parse_expression("Color!=Green")]
        results = match_filters(exprs, SAMPLE_PARAMETRIC_FILTERS)
        assert results[0]["parameter_id"] == 4000
        assert results[0]["value_ids"] == ["301", "302"]

    def test_equal_color_string(self):
        exprs = [parse_expression("Color=Green")]
        results = match_filters(exprs, SAMPLE_PARAMETRIC_FILTERS)
        assert results[0]["value_ids"] == ["300"]

    def test_equal_color_case_insensitive(self):
        exprs = [parse_expression("Color=green")]
        results = match_filters(exprs, SAMPLE_PARAMETRIC_FILTERS)
        assert results[0]["value_ids"] == ["300"]

    def test_tolerance_less_equal(self):
        exprs = [parse_expression("Tolerance<=1%")]
        results = match_filters(exprs, SAMPLE_PARAMETRIC_FILTERS)
        assert results[0]["value_ids"] == ["200", "201"]

    def test_case_insensitive_param_name(self):
        exprs = [parse_expression("resistance>15ohm")]
        results = match_filters(exprs, SAMPLE_PARAMETRIC_FILTERS)
        assert results[0]["value_ids"] == ["102", "103", "104"]

    def test_partial_param_name_match(self):
        exprs = [parse_expression("Resist>15ohm")]
        results = match_filters(exprs, SAMPLE_PARAMETRIC_FILTERS)
        assert results[0]["parameter_id"] == 2085

    def test_no_matching_parameter_raises(self):
        exprs = [parse_expression("Inductance>10uH")]
        with pytest.raises(ValueError, match="Inductance"):
            match_filters(exprs, SAMPLE_PARAMETRIC_FILTERS)

    def test_multiple_expressions(self):
        exprs = [
            parse_expression("Resistance>15ohm"),
            parse_expression("Tolerance<=1%"),
        ]
        results = match_filters(exprs, SAMPLE_PARAMETRIC_FILTERS)
        assert len(results) == 2
        assert results[0]["parameter_id"] == 2085
        assert results[1]["parameter_id"] == 3050

    def test_kilo_ohm_comparison(self):
        exprs = [parse_expression("Resistance>1kohm")]
        results = match_filters(exprs, SAMPLE_PARAMETRIC_FILTERS)
        assert results[0]["value_ids"] == ["103", "104"]

    def test_tolerance_with_plus_minus_prefix(self):
        # 실제 DigiKey 형식(U+00B1 접두)에서도 Tolerance<=1% 가 매칭돼야 한다.
        pm = chr(0x00b1)
        filters = [{
            "ParameterId": 3050,
            "ParameterName": "Tolerance",
            "FilterValues": [
                {"ValueId": "200", "ValueName": pm + "0.1%"},
                {"ValueId": "201", "ValueName": pm + "1%"},
                {"ValueId": "202", "ValueName": pm + "5%"},
            ],
        }]
        results = match_filters([parse_expression("Tolerance<=1%")], filters)
        assert results[0]["value_ids"] == ["200", "201"]

    def test_not_equal_numeric_excludes_unparseable(self):
        # != 숫자 비교는 파싱불가('-','Non-Standard') 값을 포함하지 않는다.
        filters = [{
            "ParameterId": 99,
            "ParameterName": "Resistance",
            "FilterValues": [
                {"ValueId": "r1", "ValueName": "1 kOhm"},
                {"ValueId": "r2", "ValueName": "10 kOhm"},
                {"ValueId": "r_dash", "ValueName": "-"},
                {"ValueId": "r_ns", "ValueName": "Non-Standard"},
            ],
        }]
        results = match_filters([parse_expression("Resistance!=1kOhm")], filters)
        assert results[0]["value_ids"] == ["r2"]

    def test_non_parseable_values_skipped(self):
        filters = [
            {
                "ParameterId": 99,
                "ParameterName": "Voltage",
                "FilterValues": [
                    {"ValueId": "1", "ValueName": "3.3V", "ProductCount": 10},
                    {"ValueId": "2", "ValueName": "N/A", "ProductCount": 5},
                    {"ValueId": "3", "ValueName": "5V", "ProductCount": 8},
                ],
            }
        ]
        exprs = [parse_expression("Voltage>3.3V")]
        results = match_filters(exprs, filters)
        assert results[0]["value_ids"] == ["3"]
