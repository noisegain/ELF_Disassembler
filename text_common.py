from dataclasses import dataclass
from enum import IntEnum


class RV32Type(IntEnum):
    BEQ = 0
    LB = 1
    SB = 2
    ADDI = 3
    ADD = 4
    ECALL = 5


@dataclass(init=False, repr=True)
class TextEntry:
    id: int = 0
    type: str = ""
    mark: str = ""
    imm: int = None
    rd: str = None
    rs1: str = None
    rs2: str = None
    enum: RV32Type = None
    jmp_addr: int = None
    jmp_mark: str = None

    def get_mark(self):
        if self.mark != "":
            return self.mark + ":"
        return ""
