from io import StringIO

import common
from common import write_symtab
from symtab_common import *


def parse_symtab(symtab: bytes, strtab: bytes, marks: dict[int, str]) -> str:
    def get_int(pos: int, sz: int = 4):
        return common.get_int(symtab, pos, sz)

    def get_str(pos) -> str:
        return common.get_str(strtab, pos)

    ans = StringIO()
    ans.write(".symtab\n")
    ans.write("%s %-15s %7s %-8s %-8s %-8s %6s %s\n"
              % ("Symbol", "Value", "Size", "Type", "Bind", "Vis", "Index", "Name"))
    for i in range(len(symtab) // 16):
        pos = i * 16
        cur = SymtabEntry()
        cur.num = i
        name = get_int(pos)
        pos += 4
        cur.value = get_int(pos)
        if name != 0:
            cur.name = get_str(name)
            marks[cur.value] = cur.name
        pos += 4
        cur.size = get_int(pos)
        pos += 4
        cur.info = get_int(pos, 1)
        pos += 1
        cur.visible = get_int(pos, 1)
        pos += 1
        cur.shndx = get_int(pos, 2)
        write_symtab(ans, cur)
    return ans.getvalue()
