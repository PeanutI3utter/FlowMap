from enum import IntEnum


class gate(IntEnum):
    PI = 0
    AND = 1
    OR = 2
    PO = 3
    INTERMEDIATE = 4
    LUT = 5


# positional cube notation
class inSymbol(IntEnum):
    INV = 0
    ON = 1
    OFF = 2
    DC = 3
