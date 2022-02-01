from sys import argv
from time import time

from symtab import *
from text import *


def get_int(pos: int, sz: int = 4) -> int:
    return common.get_int(file, pos, sz)


def get_str(pos: int) -> str:
    return common.get_str(file, pos)


def main():
    if file[:4] != b'\x7fELF':  # magic number assert
        print("Elf file required.")
        exit(1)
    if file[4] != 1:
        print("Expected 32-bit format")
        exit(1)
    machine = get_int(0x12, 2)
    section_header_pos = get_int(0x20)
    section_header_sz = get_int(0x2E, 2)
    section_header_num = get_int(0x30, 2)
    section_header_names_pos = get_int(0x32, 2)
    nametable_pos = get_int(section_header_names_pos * section_header_sz + section_header_pos + 0x10)

    if machine != 0xF3:  # RISC-V
        print("Sorry, it is not RISC-V architecture")
        exit(1)

    sections = {}
    for i in range(section_header_num):
        section_offset = section_header_pos + i * section_header_sz
        offset = get_int(section_offset)
        section_name = get_str(nametable_pos + offset)
        cur_addr = get_int(section_offset + 0x0C)
        cur_offset = get_int(section_offset + 0x10)
        cur_size = get_int(section_offset + 0x14)

        sections[section_name] = (cur_addr, cur_offset, cur_size) if section_name == ".text" else (cur_offset, cur_size)

    symtab_off, symtab_sz = sections[".symtab"]
    strtab = sections[".strtab"]

    marks = {}
    symtab = parse_symtab(file[symtab_off:symtab_off + symtab_sz], file[strtab[0]: sum(strtab)], marks)

    text_addr, text_off, text_sz = sections[".text"]
    text = parse_text(file[text_off: text_off + text_sz], text_addr, text_off, marks)

    out = argv[1]
    with open(out, 'w') as out:
        print(text, file=out)
        print(symtab, file=out)


if __name__ == '__main__':
    start_time = time()
    if len(argv) > 0:
        if argv[0].endswith("main.py"):
            argv = argv[1:]  # check if programm is running with "py main.py {args}"
    else:
        print("Too few arguments.")
    if len(argv) != 2:
        print("2 arguments expected: in_file out_file")
        exit(1)
    name = argv[0]
    try:
        file = open(name, "rb").read()
        main()
        print(f"Programm finished in {int((time() - start_time) * 1000)}ms")
    except FileNotFoundError:
        print("File not found.")
