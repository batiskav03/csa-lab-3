from typing import Callable
from isa import *


alu_operations: dict[str, Callable[[int, int], int]] = {
    "+": lambda left, right: left + right,
    "-": lambda left, right: left - right,
    "%": lambda left, right: left % right,
    "/": lambda left, right: left // right,
    "*": lambda left, right: left * right,
    "&": lambda left, right: left & right,
    "|": lambda left, right: left | right
}


class ALU:
    def __init__(self) -> None:
        self.N = 0
        self.Z = 1
        
        
    def do(self, op: int, left: int, right: int) -> int:
        result:int = alu_operations[op](left, right)
        self.set_flags(result)
        return result
        pass
    
    def set_flags(self, value: int) -> None:
        self.Z = 1 if value == 0  else 0
        self.N = 1 if value < 0 else 0
        
    def get_zero_flag(self) -> int:
        return self.Z
    
    def get_negative_flag(self) -> int:
        return self.N
        


    

class DataPath:
    def __init__(self, program_memory: list[bytes]) -> None:
        self.alu = ALU();
        self.memory: list[bytes] = program_memory
        self.AR = 0
        self.regs: dict [REGISTERS, bytes] = {
            REGISTERS.RAX: 0,
            REGISTERS.RBX: 0,
            REGISTERS.RCX: 0,
            REGISTERS.RDX: 0,
            REGISTERS.RSP: 0
        }
        
    def get_rdx(self) -> bytes:
        return self.regs[REGISTERS.RDX]
        
    def latch_AR(self, value: int) -> None:
        self.AR = value
    
    def get_register(self, reg: REGISTERS) -> bytes:
        return self.regs[reg]
    
    def latch_register(self, reg: REGISTERS, value: bytes) -> bytes:
        self.regs[reg] = value
    
    def get_cur_data(self) -> bytes:
        return self.memory[self.AR]
    
    def read_cur_command(self) -> None:
        self.regs[REGISTERS.RDX] = self.get_cur_data()
        
        
    
        