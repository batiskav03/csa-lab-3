from __future__ import annotations
from enum import IntEnum
import struct
# Машинное слово - non-fixed от 2 до 4 байт:
# |1---   |2---   |3---  |4---  |     |5---  |6---  |7---  |8---  |
# |opcode |ad.mode| regs |
#                        | regs |     |   address   |
#                 |   address   |     |   address   |   address   |
#                                     |           value           |

# Машинное слово - non-fixed 32 - бит  :
# |1---   |2---   |3---  |4---  |5---  |6---  |7---  |8---  opt:|9------- | 10------- | 11------- | 12------- |
# |    opcode     |  | regs |                               |                     value                   |
#                 |    offset   |       address      |          |                     value                   |
#                 | regs |       address      |                 |                     value                   |
#                 |       address      |                        |                     value                   |
#                 | regs        |                               |                     value                   |


# | mnemonic | opcode (HEX) | definition |
# | ------  | ------------  | ----------- |
# | NOP | 00 | nop |
# | MOV | 01 | move |
# | ADD | 02 | summary |
# | SUB | 03 | subtract |
# | MUL | 04 | multiply |
# | DIV | 05 | divide |
# | MOD | 06 | mod_div |
# | AND | 07 | logic and |
# | OR | 08 | logic or |
# | NOT | 09 | logic not |
# | CMP | 0A | compare |
# | JMP | 0B | jump |
# | JZ | 0C | jump zero |
# | JN | 0D | jump negative |
# | JP | 0E | jump positive |
# | HLT| 0F | halt |
# | IMOV | 10 | move value by <adress> = <rbp> - <value_offset> to rax|
# | MOVV | 11 | move absolute value to <adress> = <rbp> - <var_offset> |
# | MOVA | 12 | move rax to <adress> = <rbp> - <var_offset> |
# | MOVVA | 13 | move absolure value to rax |
# | ICMP | 1B | cmp value by xfx|
# | JNEQ | 1C | jump not equal|
# | JNE | 1D | jump negative or equal|
# | JPE | 1E | jump positive or equal |
# | JNZ | 1F | jump not zero |
# | CMPA | 2B | cmp rax with absolute value |
# | IADD | 20 | summary rax with value by <adress> |
# | IADDVAL | 21 | summary rax with <value>  |
# | ISUB | 30 | subtract rax with value by <adress>|
# | ISUBVAL | 31 | substact rax with <value>  |
# | IMUL | 40 | multiply rax with value by <adress>|
# | IMULVAL | 41 | multiply rax with <value>  |
# | IDIV| 50 | divide rax with value by <adress> |
# | IDIVVAL | 51 | divide rax with <value>  |
# | IMOD | 60 | mod rax with value by <adress> |
# | IMODVAL | 61 | mod rax with <value>  |
# | IAND | 70 | AND rax with value by <adress>  |
# | IANDVAL | 71 | AND rax with <value>  |


# - rax - регистр общего назначения, используемый при арифмитических операциях
# - rbx - регистр общего назначения
# - rdx - регистр общего назначения
# - rcx - регистр общего назначения
# - rsp - указатель стека

MAX_VALUE = 2**32
MAX_OFFSET = 2**15
MEMORY_SIZE = 65536
BUFFER_START = 40000
BUFFER_END = 44999


class REGISTERS(IntEnum):
    RAX = 0
    RBX = 1
    RDX = 2
    RCX = 3
    RSP = 4


class OPCODE(IntEnum):
    NOP = 0
    MOV = 1
    ADD = 2
    SUB = 3
    MUL = 4
    DIV = 5
    MOD = 6
    AND = 7
    OR = 8
    NOT = 9
    CMP = 10
    JMP = 11
    JZ = 12
    JN = 13
    JP = 14
    HLT = 15
    IMOV = 16
    MOVV = 17
    MOVA = 18
    MOVVA = 19
    PUSHA = 20
    POPA = 21
    PEEKA = 22
    ICMP = 27
    JNEQ = 28
    JNE = 29
    JPE = 30
    JNZ = 31
    CMPA = 43
    IADD = 32
    IADDVAL = 33
    ISUB = 48
    ISUBVAL = 49
    IMOVSP = 50
    IMUL = 64
    IMULVAL = 65
    IDIV = 80
    IDIVVAL = 81
    IMOD = 96
    IMODVAL = 97
    IAND = 112
    IANDVAL = 113
    INC = 128


str_regs: dict[int, str] = {0: "%rax", 1: "%rbx", 2: "%rdx", 3: "%rcx", 4: "%rsp"}

str_opcode: dict[int, str] = {
    0: "nop",
    1: "mov",
    2: "add",
    3: "sub",
    4: "mul",
    5: "div",
    6: "mod",
    7: "and",
    8: "or",
    9: "not",
    10: "cmp",
    11: "jmp",
    12: "jz",
    13: "jn",
    14: "jp",
    15: "hlt",
    16: "imov",
    17: "movv",
    18: "mova",
    19: "movva",
    20: "pusha",
    21: "popa",
    22: "peeka",
    27: "icmp",
    28: "jneq",
    29: "jne",
    30: "jpe",
    31: "jnz",
    43: "cmpa",
    32: "iadd",
    33: "iaddval",
    48: "isub",
    49: "isubval",
    50: "imovsp",
    64: "imul",
    65: "imulval",
    80: "idiv",
    81: "idivval",
    96: "imod",
    97: "imodval",
    112: "iand",
    113: "iandval",
    128: "inc",
}


class SecondWord:
    def __init__(self, data: int) -> None:
        self.data: int = data

    def __str__(self) -> str:
        return f"{self.data} "

    def get_bytes_value(self) -> bytes:
        return struct.pack(">i", self.data)


class Instruction:
    def __init__(self, opcode: OPCODE):
        self.opcode: OPCODE = opcode

    def __str__(self) -> str:
        if self.opcode == OPCODE.MOVVA:
            return f"{ str_opcode[self.opcode] } %rax <- next 4 bytes"
        elif self.opcode in [
            OPCODE.IADDVAL,
            OPCODE.ISUBVAL,
            OPCODE.IMULVAL,
            OPCODE.IDIVVAL,
            OPCODE.IMODVAL,
            OPCODE.IANDVAL,
        ]:
            return f"{ str_opcode[self.opcode] } %rax <- %rax {str_opcode[self.opcode][1:4]} next 4 bytes"

        return f"{ str_opcode[self.opcode] }"

    def get_bytes_value(self) -> bytes:
        return struct.pack(">Bxxx", self.opcode.value)


class OffsetInstruction(Instruction):
    def __init__(self, opcode: OPCODE, offset: int):
        super().__init__(opcode)

        self.offset: int = offset

    def __str__(self) -> str:
        if self.opcode == OPCODE.IMOV:
            return f"{str_opcode[self.opcode]} %rax <- (rbp - {self.offset})"
        if self.opcode == OPCODE.MOVV:
            return f"{str_opcode[self.opcode]} (rbp - {self.offset}) <- next 4 bytes"
        if self.opcode == OPCODE.MOVA:
            return f"{str_opcode[self.opcode]} %rax -> (rbp - {self.offset})"
        if self.opcode in [
            OPCODE.IADD,
            OPCODE.ISUB,
            OPCODE.IAND,
            OPCODE.IMUL,
            OPCODE.IDIV,
            OPCODE.IMOD,
        ]:
            return f"{str_opcode[self.opcode]} %rax <- %rax {str_opcode[self.opcode][1:]} (rbp - {self.offset}) "
        return f"{str_opcode[self.opcode]} offset: {self.offset}"

    def get_bytes_value(self) -> bytes:
        return struct.pack(">Bxh", self.opcode.value, self.offset)


class OffsetInstructionWithAdMon(OffsetInstruction):
    def __init__(self, opcode: OPCODE, adress_mode: int, offset: int):
        super().__init__(opcode, offset)
        self.adress_mode: int = adress_mode

    def __str__(self) -> str:
        if self.opcode in [
            OPCODE.JZ,
            OPCODE.JN,
            OPCODE.JMP,
            OPCODE.JP,
            OPCODE.JNEQ,
            OPCODE.JNE,
            OPCODE.JPE,
            OPCODE.JNZ,
        ]:
            if self.adress_mode == 2:
                return f"{str_opcode[self.opcode]} %pc + {self.offset}"
        return (
            f"{str_opcode[self.opcode]} admod: {self.adress_mode} offset: {self.offset}"
        )

    def get_bytes_value(self) -> bytes:
        return struct.pack(
            ">BBh", self.opcode.value, self.adress_mode << 4, self.offset
        )


class AdModRegAdressInstruction(Instruction):
    def __init__(self, opcode: OPCODE, adress_mode: int, reg: REGISTERS, adress):
        super().__init__(opcode)
        self.adress_mode: int = adress_mode
        self.reg: REGISTERS = reg
        self.adress: int = adress

    def __str__(self) -> str:
        if self.opcode == 1:
            if self.adress_mode == 9:
                return (
                    f"{str_opcode[self.opcode]} {str_regs[self.reg]} -> {self.adress}"
                )
            elif self.adress_mode == 12:
                return f"{str_opcode[self.opcode]} {str_regs[self.reg]} <- next 4 byte"
            elif self.adress_mode == 1:
                return (
                    f"{str_opcode[self.opcode]} {str_regs[self.reg]} <- ({self.adress})"
                )
        return f"{str_opcode[self.opcode]} reg: {self.reg} adress: {self.adress}"

    def get_bytes_value(self) -> bytes:
        to_byte_admod_reg = self.adress_mode * 16 + self.reg
        return struct.pack(">BBH", self.opcode, to_byte_admod_reg, self.adress)
