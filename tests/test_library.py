import pytest

from .shared import DATA_POSITIVE, DATA_NEGATIVE

from linecalc import handle_line


@pytest.mark.parametrize("line,expected", DATA_POSITIVE)
def test_line_positive(mock_convert, line, expected):
    assert handle_line(line) == pytest.approx(expected)


@pytest.mark.parametrize("line,exception", DATA_NEGATIVE)
def test_line_negative(mock_convert, line, exception):
    with pytest.raises(exception):
        handle_line(line)
