from __future__ import annotations
from enum import Enum
# Машинное слово - non-fixed от 2 до 4 байт: 
# |1---   |2---   |3---  |4---  |     |5---  |6---  |7---  |8---  |
# |opcode |ad.mode| regs | 
#                        | regs |     |   address   |
#                 |   address   |     |   address   |   address   |
#                                     |           value           |

# Машинное слово - non-fixed 32 - бит  : 
# |1---   |2---   |3---  |4---  |5---  |6---  |7---  |8---  opt:|9------- | 10------- | 11------- | 12------- | 
# |    opcode     | regs | regs |
#                 |    offset   |       address      |                               |                     value                   |
#                 | regs |       address      |
#                 |       address      |
#                 | regs        |                               


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
# | IADD | 20 | summary rax with value by <adress> |
# | IADDVAL | 21 | summary rax with <value>  |
# | ISUB | 30 | subtract rax with value by <adress>|
# | ISUBVAL | 31 | substact rax with <value>  |
# | IMUL | 40 | multiply rax with value by <adress>|
# | IMULVAL | 41 | multiply rax with <value>  |
# | IDIV| 50 | divide rax with value by <adress> |
# | IDIVVAL | 51 | divide rax with <value>  |
# | MOVV | 11 | move absolute value to <adress> = <rbp> - <var_offset> |
# | MOVA | 12 | move rax to <adress> = <rbp> - <var_offset> |


# - rax - регистр общего назначения, используемый при арифмитических операциях
# - rbx - регистр общего назначения
# - rdx - регистр общего назначения
# - rcx - регистр общего назначения
# - rsp - указатель стека

MAX_VALUE = 2**32
MEMORY_SIZE = 4096

class REGISTERS(Enum):
    RAX = 0,
    RBX = 1,
    RDX = 2,
    RCX = 3,
    RSP = 4

class OPCODE(Enum): 
    NOP =  0,
    MOV = 1,
    ADD = 2,
    SUB = 3,
    MUL = 4,
    DIV = 5,
    MOD = 6,
    AND = 7,
    OR = 8,
    NOT = 9,
    CMP = 10,
    JMP = 11,
    JZ = 12,
    JN = 13,
    JP = 14,
    HLT = 15,
    IMOV = 16,
    MOVV = 17,
    MOVA = 18,
    IADD = 32,
    IADDVAL = 33,
    ISUB = 48,
    ISUBVAL = 49,
    IMUL = 64,
    IMULVAL = 65,
    IDIV = 80,
    IDIVVAL = 81
    
class SecondWord:
    def __init__(self, data: int) -> None:
        self.data: int = data

class Instruction:

    def __init__(self, opcode: int):
        self.opcode: int = opcode

        
class OffsetInstruction(Instruction):
    def __init__(self, opcode: int, offset: int):
        super().__init__(opcode)
        self.offset: int = offset


class DoubleRegsInstruction(Instruction):

    def __init__(self, opcode: int, first_register: int, second_register: int):
        super().__init__(opcode)
        self.first_register: int = first_register
        self.second_register: int = second_register

class DoubleRegsAndAdressInstruction(DoubleRegsInstruction):

    def __init__(self, opcode: int, first_register: int, second_register: int, adress: int):
        super().__init__(opcode, first_register, second_register)
        self.adress: int = adress


class AdressInstruction(Instruction):

    def __init__(self, opcode: int, first_ad: int, second_ad: int, value: int= None , third_ad: int= None):
        super().__init__(opcode)
        self.first_ad: int = first_ad
        self.second_ad: int = second_ad
        # todo: в зависимости от типа адресации чекать на прямую загрузку или третий адрес
        
    