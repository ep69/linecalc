import pytest
import linecalc


@pytest.fixture
def mock_convert(monkeypatch):
    def fake_convert(base, quote="czk"):
        if base == "usd" and quote == "czk":
            return 20.5
        elif base == "eur" and quote == "czk":
            return 24.5
        elif base == "czk" and quote == "czk":
            return 1.0
        elif base == "pln" and quote == "czk":
            return 5.7
        elif base == "btc" and quote == "czk":
            return 100_000.0 * 20.5

        raise linecalc.linecalc.ConvertError("mock convert")

    monkeypatch.setattr(linecalc.linecalc, "convert", fake_convert)
