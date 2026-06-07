import pytest

from ff_digikey_api.Util.ParametricExpression import (
    ParametricExpression,
    parse_expression,
)


class TestParseExpression:
    def test_greater_than(self):
        e = parse_expression("Resistance>15ohm")
        assert e.param_name == "Resistance"
        assert e.operator == ">"
        assert e.raw_value == "15ohm"
        assert e.numeric_value == pytest.approx(15.0)

    def test_greater_equal(self):
        e = parse_expression("Voltage>=3.3V")
        assert e.param_name == "Voltage"
        assert e.operator == ">="
        assert e.numeric_value == pytest.approx(3.3)

    def test_less_than(self):
        e = parse_expression("Resistance<100ohm")
        assert e.operator == "<"
        assert e.numeric_value == pytest.approx(100.0)

    def test_less_equal(self):
        e = parse_expression("Tolerance<=1%")
        assert e.param_name == "Tolerance"
        assert e.operator == "<="
        assert e.numeric_value == pytest.approx(1.0)

    def test_equal_numeric(self):
        e = parse_expression("Resistance=15ohm")
        assert e.operator == "="
        assert e.numeric_value == pytest.approx(15.0)

    def test_not_equal(self):
        e = parse_expression("Color!=Green")
        assert e.operator == "!="
        assert e.raw_value == "Green"
        assert e.numeric_value is None

    def test_equal_string(self):
        e = parse_expression("Color=Green")
        assert e.param_name == "Color"
        assert e.operator == "="
        assert e.raw_value == "Green"
        assert e.numeric_value is None

    def test_spaces_in_param_name(self):
        e = parse_expression("Core Processor=ARM")
        assert e.param_name == "Core Processor"
        assert e.raw_value == "ARM"

    def test_kilo_ohm_expression(self):
        e = parse_expression("Resistance>1.5kohm")
        assert e.numeric_value == pytest.approx(1500.0)

    def test_invalid_no_operator(self):
        with pytest.raises(ValueError):
            parse_expression("no-operator-here")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            parse_expression("")
