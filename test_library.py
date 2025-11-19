import pytest
import sys

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

    monkeypatch.setattr(linecalc, "convert", fake_convert)


@pytest.mark.parametrize(
    "line,expected",
    [
        ("2+2*2", 6.0),
        ("10 usd", 205.0),
        ("10 usd to czk", 205.0),
        ("10 eur", 245.0),
        ("10 eur to czk", 245.0),
        ("10 pln", 57.0),
        ("10 pln to czk", 57.0),
        ("1 eur to usd", 245.0 / 205.0),
        ("1 btc", 100_000.0 * 20.5),
        ("1 btc to czk", 100_000.0 * 20.5),
        ("1 btc to usd", 100_000.0),
        ("1 btc to eur", 100_000.0 / 24.5 * 20.5),
    ],
)
def test_line(mock_convert, line, expected):
    assert handle_line(line) == pytest.approx(expected)
