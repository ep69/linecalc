from linecalc.linecalc import ConvertError, ParseError


DATA_POSITIVE = [
    ("2+2*2", 6.0),
    ("10 usd", 205.0),
    ("10 usd to czk", 205.0),
    ("10 eur", 245.0),
    ("10 eur to czk", 245.0),
    ("10 pln", 57.0),
    ("10 pln to czk", 57.0),
    ("1 eur to usd", 24.5 / 20.5),
    ("1 btc", 100_000.0 * 20.5),
    ("1 btc to czk", 100_000.0 * 20.5),
    ("1 btc to sat", 100_000_000.0),
    ("1 btc to usd", 100_000.0),
    ("1 btc to eur", 100_000.0 / 24.5 * 20.5),
    ("1 sat to btc", 1e-8),
]

DATA_NEGATIVE = [
    ("usd", ParseError),
    ("1 rincewind", ConvertError),
    ("+", ParseError),
    ("1+", ParseError),
    ("+1", ParseError),
    ("(", ParseError),
    (")", ParseError),
    ("()", ParseError),
    ("(1)(2)", ParseError),
    ("to czk to czk", ParseError),
]
