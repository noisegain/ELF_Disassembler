from io import StringIO
from symtab_common import SymtabEntry
from text_common import TextEntry, RV32Type


def get_int(file: bytes, pos: int, sz: int = 4):
    return int.from_bytes(file[pos:pos + sz], byteorder='little')


def get_str(file: bytes, pos) -> str:
    res = ""
    while file[pos] != 0:
        res += chr(file[pos])
        pos += 1
    return res


def convert_twos_complement(bits: bin) -> int:
    return -int(bits[0]) << len(bits) | int(bits, 2)


def get_cmd(commands: dict[int: str], cmd: str) -> str:
    c = int(cmd[-15:-12], 2)
    if c not in commands:
        print("Unknown command: ", cmd)
        return "X"
    return commands[c]


def write_text(out: StringIO, entry: TextEntry):
    if entry.enum in (RV32Type.LB, RV32Type.SB) or entry.type == "JALR":
        out.write("%08x %10s %s %s, %i(%s)\n" %
                  (entry.id, entry.get_mark(), entry.type,
                   entry.rd if entry.enum != RV32Type.SB else entry.rs2,
                   entry.imm, entry.rs1))
    else:
        a = ", ".join(str(x) for x in (entry.rd, entry.rs1, entry.rs2, entry.imm) if x is not None)
        if entry.jmp_addr is not None:
            a += " " + hex(entry.jmp_addr) + " " + entry.jmp_mark
        out.write("%08x %10s %s " %
                  (entry.id, entry.get_mark(), entry.type) + a + '\n')


def write_symtab(out: StringIO, entry: SymtabEntry):
    out.write("[%4i] 0x%-15X %5i %-8s %-8s %-8s %6s %s\n" %
              (entry.num, entry.value, entry.size, entry.get_type(),
               entry.get_bind(), entry.get_visible(), entry.get_index(), entry.name))
