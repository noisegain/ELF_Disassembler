from io import StringIO

from common import write_text, get_cmd, convert_twos_complement
from text_common import *

rv32 = {
    0b0110111: "LUI",
    0b0010111: "AUIPC",
    0b1101111: "JAL",
    0b1100111: "JALR",
    0b1100011: RV32Type.BEQ,
    0b0000011: RV32Type.LB,
    0b0100011: RV32Type.SB,
    0b0010011: RV32Type.ADDI,
    0b0110011: RV32Type.ADD,
    0b0001111: "FENCE",
    0b1110011: RV32Type.ECALL
}


def unknown(cmd: str) -> str:
    print("Unknown command", cmd)
    return "X"


def parse_rv32(cmd: str) -> str:
    cmd_type = int(cmd[-7:], 2)
    if cmd_type in rv32:
        handler = rv32[cmd_type]
        match handler:
            case handler if isinstance(handler, str):
                return handler
            case RV32Type.BEQ:
                return get_cmd({
                    0b000: "BEQ",
                    0b001: "BNE",
                    0b100: "BLT",
                    0b101: "BGE",
                    0b110: "BLTU",
                    0b111: "BGEU",
                }, cmd)
            case RV32Type.LB:
                return get_cmd({
                    0b000: "LB",
                    0b001: "LH",
                    0b010: "LW",
                    0b100: "LBU",
                    0b101: "LHU"
                }, cmd)
            case RV32Type.SB:
                return get_cmd({
                    0b000: "SB",
                    0b001: "SH",
                    0b010: "SW",
                }, cmd)
            case RV32Type.ADDI:
                c = get_cmd({
                    0b000: "ADDI",
                    0b010: "SLTI",
                    0b011: "SLTIU",
                    0b100: "XORI",
                    0b110: "ORI",
                    0b111: "ANDI",
                    0b001: "SLLI",
                    0b101: ["SRLI", "SRAI"]
                }, cmd)
                if isinstance(c, list):
                    return c[cmd[1] == '1']
                else:
                    return c
            case RV32Type.ADD:
                t = int(cmd[0:7], 2)
                if t == 0 or t == 0b0100000:
                    c = get_cmd({
                        0b000: ["ADD", "SUB"],
                        0b001: "SLL",
                        0b010: "SLT",
                        0b011: "SLTU",
                        0b100: "XOR",
                        0b101: ["SRL", "SRA"],
                        0b110: "OR",
                        0b111: "AND"
                    }, cmd)
                    if isinstance(c, list):
                        return c[cmd[1] == '1']
                    else:
                        return c
                elif t == 1:
                    c = get_cmd({
                        0b000: "MUL",
                        0b001: "MULH",
                        0b010: "MULHSU",
                        0b011: "MULHU",
                        0b100: "DIV",
                        0b101: "DIVU",
                        0b110: "REM",
                        0b111: "REMU"
                    }, cmd)
                    return c
                else:
                    return unknown(cmd)
            case RV32Type.ECALL:
                v = int(cmd[:12], 2)
                if v == 0 or v == 1:
                    return ["ECALL", "EBREAK"][v]
                else:
                    return unknown(cmd)
            case _:
                return unknown(cmd)
    else:
        return unknown(cmd)


regs = {
    0: "zero",
    1: "ra",
    2: "sp",
    3: "gp",
    4: "tp",
    5: "t0",
    6: "t1",
    7: "t2",
    8: "s0",
    9: "s1"
}
regs.update({i: f"a{i - 10}" for i in range(10, 18)}
            | {i: f"s{i - 16}" for i in range(18, 28)}
            | {i: f"t{i - 25}" for i in range(28, 38)})


def get_rd(cmd: str) -> int:
    rd = int(cmd[-12:-7], 2)
    return regs[rd]


def get_rs1(cmd: str) -> int:
    rs1 = int(cmd[12:17], 2)
    return regs[rs1]


def get_rs2(cmd: str) -> int:
    rs2 = int(cmd[7:12], 2)
    return regs[rs2]


def parse_text(file: bytes, addr: int, offset: int, marks: dict[int, str]) -> str:
    ans = StringIO()
    ans.write(".text\n")
    i = 0
    entries: dict[int, TextEntry] = {}
    while i < len(file):
        entry = TextEntry()
        entry.id = addr + i
        if entry.id in marks:
            entry.mark = marks[entry.id]
        sz = 2
        if file[i] & 0b11 == 0b11:
            sz = 4  # not rvc
        cmd = [file[i + j] for j in range(sz)]
        if sz == 4:
            cmd = "".join(bin(x)[2:].rjust(8, '0') for x in cmd[::-1])
            res = parse_rv32(cmd)
            if res != "":
                entry.type = res
                cmd_type = rv32[int(cmd[-7:], 2)]
                if isinstance(cmd_type, RV32Type):
                    entry.enum = cmd_type
                if cmd_type not in (RV32Type.BEQ, RV32Type.SB, RV32Type.ECALL):
                    entry.rd = get_rd(cmd)
                if res not in ("LUI", "AUIPC", "JAL", "ECALL", "EBREAK"):
                    entry.rs1 = get_rs1(cmd)
                if cmd_type in (RV32Type.BEQ, RV32Type.SB, RV32Type.ADD):
                    entry.rs2 = get_rs2(cmd)
                if cmd_type in (RV32Type.LB, RV32Type.ADDI) or cmd_type == "JALR":
                    if cmd_type == RV32Type.ADDI and entry.type in ["SLLI", "SRLI", "SRAI"]:
                        entry.imm = convert_twos_complement(cmd[7:12])
                    else:
                        entry.imm = convert_twos_complement(cmd[:12])
                if cmd_type == RV32Type.SB:
                    entry.imm = convert_twos_complement(cmd[:7] + cmd[-12:-7])
                if cmd_type in ("AUIPC", "LUI"):
                    entry.imm = convert_twos_complement(cmd[:-12] + "0" * 12)
                if cmd_type == "JAL":
                    entry.imm = convert_twos_complement(
                        cmd[0] + cmd[-20:-12] + cmd[-21] + cmd[1:11] + "0")
                if cmd_type == RV32Type.BEQ:
                    entry.imm = convert_twos_complement(
                        cmd[0] + cmd[-8] + cmd[1:7] + cmd[-12:-8] + "0")
            else:
                unknown(cmd)
        else:
            entry.type = "RVC"
        entries[entry.id] = entry
        i += sz
    for value in entries.values():
        if value.enum == RV32Type.BEQ or value.type == "JAL":
            value.jmp_addr = value.id + value.imm
            if value.jmp_addr in marks:
                value.jmp_mark = marks[value.jmp_addr]
            else:
                entries[value.jmp_addr].mark = value.jmp_mark = "LOC_%05x" % value.jmp_addr
    for value in entries.values():
        write_text(ans, value)
    return ans.getvalue()
