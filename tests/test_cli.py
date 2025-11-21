import pytest
import io

from .shared import DATA_POSITIVE, DATA_NEGATIVE

from linecalc import main
from linecalc.linecalc import human_str


@pytest.mark.parametrize("line,expected", DATA_POSITIVE)
def test_cli_positive_oneline(mock_convert, capsys, monkeypatch, line, expected):
    monkeypatch.setattr("sys.stdin", io.StringIO(line))
    monkeypatch.setattr("sys.argv", ["linecalc"])
    # monkeypatch.setattr("sys.argv", ["linecalc", "-d"])
    main()
    captured = capsys.readouterr()
    output = captured.out.rstrip()
    # print(captured.err)
    assert output == human_str(expected)


def test_cli_positive_all(mock_convert, capsys, monkeypatch):
    long_input = "\n".join(map(lambda x: x[0], DATA_POSITIVE))
    expected_output = "\n".join(map(lambda x: human_str(x[1]), DATA_POSITIVE))
    monkeypatch.setattr("sys.stdin", io.StringIO(long_input))
    monkeypatch.setattr("sys.argv", ["linecalc"])
    # monkeypatch.setattr("sys.argv", ["linecalc", "-d"])
    main()
    captured = capsys.readouterr()
    output = captured.out.rstrip()
    # print(captured.err)
    assert output == expected_output


@pytest.mark.parametrize("line,exception", DATA_NEGATIVE)
def test_cli_negative_oneline(mock_convert, capsys, monkeypatch, line, exception):
    monkeypatch.setattr("sys.stdin", io.StringIO(line))
    monkeypatch.setattr("sys.argv", ["linecalc"])
    # monkeypatch.setattr("sys.argv", ["linecalc", "-d"])
    main()
    captured = capsys.readouterr()
    error = captured.err.rstrip()
    assert error.startswith(exception.__name__)


def test_cli_negative_all(mock_convert, capsys, monkeypatch):
    long_input = "\n".join(map(lambda x: x[0], DATA_NEGATIVE))
    expected_errors = list(map(lambda x: x[1].__name__, DATA_NEGATIVE))
    monkeypatch.setattr("sys.stdin", io.StringIO(long_input))
    monkeypatch.setattr("sys.argv", ["linecalc"])
    # monkeypatch.setattr("sys.argv", ["linecalc", "-d"])
    main()
    captured = capsys.readouterr()
    errors = captured.err.split("\n")
    if len(errors[-1]) == 0:
        # last line is empty
        del errors[-1]
    assert len(expected_errors) == len(errors)
    for i in range(len(expected_errors)):
        assert errors[i].startswith(expected_errors[i])


def test_cli_pipe(mock_convert, capsys, monkeypatch):
    line = "40000 + 2000"
    expected = 42000
    monkeypatch.setattr("sys.stdin", io.StringIO(line))
    monkeypatch.setattr("sys.argv", ["linecalc"])
    # monkeypatch.setattr("sys.argv", ["linecalc", "-d"])
    main()
    captured = capsys.readouterr()
    output1 = captured.out.rstrip()
    # print(captured.err)
    monkeypatch.setattr("sys.stdin", io.StringIO(output1))
    monkeypatch.setattr("sys.argv", ["linecalc"])
    # monkeypatch.setattr("sys.argv", ["linecalc", "-d"])
    main()
    captured = capsys.readouterr()
    output2 = captured.out.rstrip()
    # print(captured.err)
    assert output2 == human_str(expected)
