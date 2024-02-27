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
    

    def get_offset(self, unpacked: int) -> int:
        BIT_MASK = 65535
        unpacked &= BIT_MASK
        return unpacked
        pass
        


    

class DataPath:
    def __init__(self, program_memory: list[bytes]) -> None:
        self.alu = ALU();
        self.memory: list[bytes] = program_memory + [b'\x00\x00\x00\x00'] * (MEMORY_SIZE - len(program_memory))
        self.AR: int = 0
        self.DR: bytes = 0
        self.regs: dict [REGISTERS, int] = {
            REGISTERS.RAX: 0,
            REGISTERS.RBX: 0,
            REGISTERS.RCX: 0,
            REGISTERS.RDX: 0,
            REGISTERS.RSP: 0
        }
        
    def get_DR(self) -> bytes:
        return self.DR
    
    def get_int_DR(self) -> int:
        return struct.unpack(">i", self.DR)[0]
        
    def latch_AR(self, value: int) -> None:
        self.AR = value
    
    def get_register(self, reg: REGISTERS) -> int:
        return self.regs[reg]
    
    def latch_register(self, reg: REGISTERS, value: int) -> int:
        self.regs[reg] = value
    
    def get_cur_data(self) -> bytes:
        return self.memory[self.AR]
    
    def read_cur_command(self) -> None:
        self.latch_DR(self.get_cur_data())
        
    def latch_DR(self, command: bytes) -> None:
        self.DR = command
        
    def write_memory(self) -> None:
        self.memory[self.AR] = self.get_DR()    
    
        