import pytest

from ff_digikey_api.Util.ValueParser import parse_numeric_value


class TestParseNumericValue:
    def test_plain_integer(self):
        assert parse_numeric_value("15") == 15.0

    def test_plain_float(self):
        assert parse_numeric_value("3.3") == pytest.approx(3.3)

    def test_with_unit_suffix(self):
        assert parse_numeric_value("15ohm") == 15.0

    def test_with_unit_suffix_uppercase(self):
        assert parse_numeric_value("15Ohm") == 15.0

    def test_kilo_prefix(self):
        assert parse_numeric_value("1.5kohm") == pytest.approx(1500.0)

    def test_kilo_prefix_uppercase(self):
        assert parse_numeric_value("1.5Kohm") == pytest.approx(1500.0)

    def test_mega_prefix(self):
        assert parse_numeric_value("2.2Mohm") == pytest.approx(2.2e6)

    def test_micro_prefix_u(self):
        assert parse_numeric_value("4.7uF") == pytest.approx(4.7e-6)

    def test_nano_prefix(self):
        assert parse_numeric_value("100nF") == pytest.approx(100e-9)

    def test_pico_prefix(self):
        assert parse_numeric_value("10pF") == pytest.approx(10e-12)

    def test_milli_prefix(self):
        assert parse_numeric_value("100mV") == pytest.approx(0.1)

    def test_giga_prefix(self):
        assert parse_numeric_value("1.2GHz") == pytest.approx(1.2e9)

    def test_percentage(self):
        assert parse_numeric_value("1%") == 1.0

    def test_percentage_decimal(self):
        assert parse_numeric_value("0.5%") == pytest.approx(0.5)

    def test_digikey_format_space(self):
        assert parse_numeric_value("15 Ohms") == 15.0

    def test_digikey_format_kilo(self):
        assert parse_numeric_value("1.5 kOhms") == pytest.approx(1500.0)

    def test_digikey_format_nano(self):
        assert parse_numeric_value("100 nF") == pytest.approx(100e-9)

    def test_digikey_format_micro_mu(self):
        assert parse_numeric_value("4.7 \u00b5F") == pytest.approx(4.7e-6)

    def test_negative_value(self):
        assert parse_numeric_value("-40C") == -40.0

    def test_non_numeric_returns_none(self):
        assert parse_numeric_value("Green") is None

    def test_empty_returns_none(self):
        assert parse_numeric_value("") is None

    def test_only_unit_returns_none(self):
        assert parse_numeric_value("Ohms") is None

    def test_plus_minus_tolerance(self):
        # DigiKey 공차값은 U+00B1(+/-)로 시작한다. 제거 후 크기로 파싱.
        pm = chr(0x00b1)
        assert parse_numeric_value(pm + "1%") == 1.0
        assert parse_numeric_value(pm + "5%") == 5.0
        assert parse_numeric_value(pm + "0.1%") == pytest.approx(0.1)

    def test_unit_letter_not_treated_as_prefix(self):
        # 접두사 글자가 사실은 단위(뒤에 단위 없음)면 배율 적용하지 않는다.
        assert parse_numeric_value("3000K") == 3000.0          # 켈빈(색온도)
        assert parse_numeric_value("5G") == 5.0                # 가우스
        assert parse_numeric_value("1.4 T") == pytest.approx(1.4)  # 테슬라

    def test_real_prefix_still_scales(self):
        # 접두사 뒤에 단위가 오면 정상 배율
        assert parse_numeric_value("10kOhm") == pytest.approx(10000.0)
        assert parse_numeric_value("100 mT") == pytest.approx(0.1)   # 밀리테슬라
        assert parse_numeric_value("2.4GHz") == pytest.approx(2.4e9)
