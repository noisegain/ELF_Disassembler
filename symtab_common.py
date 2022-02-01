from dataclasses import dataclass

shndx_map = {
    0x0000: "UNDEF",
    0xff00: "LORESERVE",
    0xff01: "AFTER",
    0xff1f: "HIPROC",
    0xff20: "LOOS",
    0xff3f: "HIOS",
    0xfff1: "ABS",
    0xfff2: "COMMON",
    0xffff: "XINDEX"
}


@dataclass(init=False, repr=True)
class SymtabEntry:
    num: int
    value: int
    size: int
    info: int
    visible: int
    shndx: int
    name: str = ""

    def get_info(self):
        return tuple(hex(self.info)[2:].rjust(2, '0'))

    def get_bind(self):
        match self.get_info()[0]:
            case '1':
                return "GLOBAL"
            case '0':
                return "LOCAL"
            case _:
                return "UNKNOWN"

    def get_type(self):
        match self.get_info()[1]:
            case '0':
                return "NOTYPE"
            case '1':
                return "OBJECT"
            case '2':
                return "FUNC"
            case '3':
                return "SECTION"
            case '4':
                return "FILE"
            case _:
                return "UNKNOWN"

    def get_visible(self):
        match self.visible:
            case 0:
                return "DEFAULT"
            case 2:
                return "HIDDEN"
            case _:
                return "UNKNOWN"

    def get_index(self):
        return shndx_map[self.shndx] if self.shndx in shndx_map else str(self.shndx)
