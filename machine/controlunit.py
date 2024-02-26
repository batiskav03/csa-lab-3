


from datapath import DataPath
from isa import *


class ControlUnit:
    def __init__(self, program_memory: list[bytes], limit: int) -> None:
        self.tick: int = 0
        self.limit: int = limit
        self.PC = 0
        self.data_path = DataPath(program_memory)
        self.instr: bytes = 0
        self.commands_handler: dict [OPCODE, callable] = {
            OPCODE.NOP: self.call_nop,
            OPCODE.MOV: self.call_mov,
            OPCODE.ADD: self.call_add,
            OPCODE.SUB: self.call_sub,
            OPCODE.MUL: self.call_mul,
            OPCODE.DIV: self.call_div,
            OPCODE.MOD: self.call_mod,
            OPCODE.AND: self.call_and,
            OPCODE.OR: self.call_or,
            OPCODE.NOT: self.call_not,
            OPCODE.CMP: self.call_cmp,
            OPCODE.JMP: self.call_jmp,
            OPCODE.JZ: self.call_jz,
            OPCODE.JN: self.call_jn,
            OPCODE.JP: self.call_jp,
            OPCODE.HLT: self.call_hlt,
            OPCODE.IMOV: self.call_imov,
            OPCODE.MOVV: self.call_movv,
            OPCODE.MOVA: self.call_mova,
            OPCODE.MOVVA: self.call_movva,
            OPCODE.PUSHA: self.call_pusha,
            OPCODE.POPA: self.call_popa,
            OPCODE.PEEKA: self.call_peeka,
            OPCODE.ICMP: self.call_icmp,
            OPCODE.JNEQ: self.call_jneq,
            OPCODE.JNE: self.call_jne,
            OPCODE.JPE: self.call_jpe,
            OPCODE.JNZ: self.call_jnz,
            OPCODE.CMPA: self.call_cmpa,
            OPCODE.IADD: self.call_iadd,
            OPCODE.IADDVAL: self.call_iaddval,
            OPCODE.ISUB: self.call_isub,
            OPCODE.ISUBVAL: self.call_isubval,
            OPCODE.IMOVSP: self.call_imovsp,
            OPCODE.IMUL: self.call_imul,
            OPCODE.IMULVAL: self.call_imulval,
            OPCODE.IDIV: self.call_idiv,
            OPCODE.IDIVVAL: self.call_idivval,
            OPCODE.IMOD: self.call_imod,
            OPCODE.IMODVAL: self.call_imodval,
            OPCODE.IAND: self.call_iand,
            OPCODE.IANDVAL: self.call_iandval,
            OPCODE.INC: self.call_inc
        }
        
    def tick(self) -> None:
        self.tick += 1
        
    def cur_tick(self) -> int:
        return self.tick
    
    def start_processering(self) -> None:
        while (self.cur_tick() < self.limit):
            self.instruction_fetch()
            self.decode_fetch()
            # opearand fetch and execution fetch inner personal func
            self.operand_fetch()
            self.execution_fetch()
            
    def instruction_fetch(self):
        self.data_path.read_cur_command()
        self.instr = self.data_path.get_rdx()
        self.tick()
        
    
    def decode_fetch(self):
        cur_instruction = struct.unpack(">i", self.instr)
        opcode = cur_instruction[0]
        self.commands_handler[opcode](cur_instruction)

            
        
        pass
    
    def operand_fetch(self):
        pass 
    
    def execution_fetch(self):
        pass
    
    
    def inc(self, bytes_command_arr: bytes) -> None:
        rax_value = self.unpack(">i",self.data_path.get_register(REGISTERS.RAX))
        result = self.data_path.alu.do("+", 1, rax_value)
        self.data_path.latch_register(REGISTERS.RAX, result)
        self.tick()

    