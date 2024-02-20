
# Машинное слово - non-fixed от 2 до 4 байт: 
# |1---   |2---   |3---  |4---  |     |5---  |6---  |7---  |8---  |
# |opcode |ad.mode| regs | 
#                        | regs |     |   address   |
#                 |   address   |     |   address   |   address   |
#                                     |           value           |


OPCODE = {
    "NOP": 0,
    "MOV": 1,
    "ADD": 2,
    "SUB": 3,
    "MUL": 4,
    "DIV": 5,
    "MOD": 6,
    "AND": 7,
    "OR": 8,
    "NOT": 9,
    "CMP": 10,
    "JMP": 11,
    "JZ": 13,
    "JN": 14,
    "JP": 15,
    "HLT": 16

}
class Instruction:

    def __init__(self, opcode: bin, adress_mode: bin):
        self.opcode: bin = opcode
        self.adress_mode: bin = adress_mode
    


class DoubleRegsInstruction(Instruction):

    def __init__(self, opcode: bin, adress_mode: bin, first_register: bin, second_register: bin):
        super().__init__(opcode, adress_mode)
        self.first_register: bin = first_register
        self.second_register: bin = second_register

class DoubleRegsAndAdressInstruction(DoubleRegsInstruction):

    def __init__(self, opcode: bin, adress_mode: bin, first_register: bin, second_register: bin, adress: bin):
        super().__init__(opcode, adress_mode, first_register, second_register)
        self.adress: bin = adress


class AdressInstruction(Instruction):

    def __init__(self, opcode: bin, adress_mode: bin, first_ad: bin, second_ad: bin, value: bin = None , third_ad: bin = None):
        super().__init__(opcode, adress_mode)
        self.first_ad: bin = first_ad
        self.second_ad: bin = second_ad
        # todo: в зависимости от типа адресации чекать на прямую загрузку или третий адрес