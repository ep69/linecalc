import pytest
import sys

from .data import DATA_POSITIVE

import linecalc
from linecalc import handle_line


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

        print(f"Unable to convert {base} to {quote}", file=sys.stderr)
        return None

    monkeypatch.setattr(linecalc.linecalc, "convert", fake_convert)


@pytest.mark.parametrize("line,expected", DATA_POSITIVE)
def test_line(mock_convert, line, expected):
    assert handle_line(line) == pytest.approx(expected)
