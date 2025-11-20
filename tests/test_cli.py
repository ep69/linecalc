import pytest
import sys
import io

from .data import DATA_POSITIVE

import linecalc
from linecalc import main


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
def test_cli_positive_oneline(mock_convert, capsys, monkeypatch, line, expected):
    monkeypatch.setattr("sys.stdin", io.StringIO(line))
    monkeypatch.setattr("sys.argv", ["linecalc"])
    # monkeypatch.setattr("sys.argv", ["linecalc", "-d"])
    main()
    captured = capsys.readouterr()
    output = captured.out.rstrip()
    # print(captured.err)
    assert output == f"{expected:.2f}"


def test_cli_positive_all(mock_convert, capsys, monkeypatch):
    long_input = "\n".join(map(lambda x: x[0], DATA_POSITIVE))
    expected_output = "\n".join(map(lambda x: f"{x[1]:.2f}", DATA_POSITIVE))
    monkeypatch.setattr("sys.stdin", io.StringIO(long_input))
    monkeypatch.setattr("sys.argv", ["linecalc"])
    # monkeypatch.setattr("sys.argv", ["linecalc", "-d"])
    main()
    captured = capsys.readouterr()
    output = captured.out.rstrip()
    # print(captured.err)
    assert output == expected_output
