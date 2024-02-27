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
        
    def inc_tick(self) -> None:
        self.tick += 1
        
    def cur_tick(self) -> int:
        return self.tick
    
    def start_processering(self) -> None:
        while (self.cur_tick() < self.limit):
            self.instruction_fetch()
            self.decode_fetch()
            self.PC += 1
            self.data_path.latch_AR(self.PC)
            # opearand fetch and execution fetch inner personal func
            self.operand_fetch()
            self.execution_fetch()
            
    def instruction_fetch(self):
        self.data_path.read_cur_command()
        self.instr = self.data_path.get_DR()
        self.inc_tick()
        
    
    def decode_fetch(self):
        opcode = struct.unpack(">Bbbb", self.instr)[0]
        cur_instruction = struct.unpack(">i", self.instr)
        self.commands_handler[opcode](cur_instruction)
        pass
    
    def operand_fetch(self):
        pass 
    
    def execution_fetch(self):
        pass
    
    
    def call_inc(self, bytes_command_arr: bytes) -> None:
        #execution fetch
        rax_value = self.data_path.get_register(REGISTERS.RAX)
        result = self.data_path.alu.do("+", 1, rax_value)
        self.data_path.latch_register(REGISTERS.RAX, result)
        self.inc_tick()

    def call_imov(self, bytes_command_arr: bytes) -> None:
        #operand fetch
        self.i_commands_op(bytes_command_arr)
        #execution fetch
        self.data_path.latch_register(REGISTERS.RAX, self.data_path.get_DR())
        self.inc_tick()
        pass
    
    def call_iadd(self, bytes_command_arr: bytes) -> None:
        self.call_ioperation_with_alu(bytes_command_arr, "+")
        
    def call_isub(self, bytes_command_arr: bytes) -> None:
        self.call_ioperation_with_alu(bytes_command_arr, "-")
        
    def call_imul(self, bytes_command_arr: bytes) -> None:
        self.call_ioperation_with_alu(bytes_command_arr, "*")
    
    def call_idiv(self, bytes_command_arr: bytes) -> None:
        self.call_ioperation_with_alu(bytes_command_arr, "/")
        
    def call_imod(self, bytes_command_arr: bytes) -> None:
        self.call_ioperation_with_alu(bytes_command_arr, "%")
        
    def call_iand(self, bytes_command_arr: bytes) -> None:
        self.call_ioperation_with_alu(bytes_command_arr, "&")
        
    def call_ioperation_with_alu(self, bytes_command_arr: bytes, operator: str) -> None:
        #operand fetch
        self.i_commands_op(bytes_command_arr)
        #execution fetch
        self.data_path.latch_register(REGISTERS.RDX, self.data_path.get_int_DR())
        self.inc_tick()
        rdx_int = self.data_path.get_register(REGISTERS.RDX)
        rax_int = self.data_path.get_register(REGISTERS.RAX)
        self.data_path.latch_register(REGISTERS.RAX, self.data_path.alu.do(operator, rax_int, rdx_int))
        self.inc_tick()
        
    def i_commands_op(self, bytes_command_arr: bytes) -> None:
        # finally, data from <adress> = <rbp> - <offset> in DR
        self.calculate_variable_adress(bytes_command_arr)
        self.data_path.latch_DR(self.data_path.get_cur_data())
        self.inc_tick()
        
    def calculate_variable_adress(self, bytes_command_arr: bytes) -> None:
        # finally, <adress> = <rbp> - <offset> in AR
        self.data_path.latch_register(REGISTERS.RDX,
                                      self.data_path.alu.get_offset(self.data_path.get_int_DR()))
        self.inc_tick()
        rdx_int = self.data_path.get_register(REGISTERS.RDX)
        rbx_int = self.data_path.get_register(REGISTERS.RBX)
        self.data_path.latch_AR(self.data_path.alu.do("+", rdx_int, rbx_int))
        self.inc_tick()
        
    def call_movv(self, bytes_command_arr: bytes) -> None: #64 bit instruction
        #operand fetch
        self.data_path.latch_register(REGISTERS.RDX,
                                      self.data_path.alu.get_offset(self.data_path.get_int_DR()))
        self.inc_tick()
        rdx_int = self.data_path.get_register(REGISTERS.RDX)
        rbx_int = self.data_path.get_register(REGISTERS.RBX)
        self.data_path.latch_register(REGISTERS.RDX, self.data_path.alu.do("+", rdx_int, rbx_int))
        self.inc_tick()
        self.PC += 1
        self.data_path.latch_AR(self.PC)
        self.inc_tick()
        self.data_path.read_cur_command()
        self.inc_tick()
        #execution fetch
        self.data_path.latch_AR(self.data_path.get_register(REGISTERS.RDX))
        self.inc_tick()
        self.data_path.write_memory()
        
        
    def call_nop(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_mov(self, bytes_command_arr: bytes) -> None:
        instr = bytes_command_arr[0]
        controll_bits = instr & 15728640
        reg1 = instr & 983040
        if controll_bits == 2:
            
        pass
    
    def call_add(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_sub(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_mul(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_div(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_mod(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_and(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_or(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_not(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_cmp(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_jmp(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_jz(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_jn(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_jp(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_hlt(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_mova(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_movva(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_pusha(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_popa(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_peeka(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_icmp(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_jneq(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_jneq(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_jne(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_jpe(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_jnz(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_cmpa(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_iaddval(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_isubval(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_imovsp(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_imulval(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_idivval(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_imodval(self, bytes_command_arr: bytes) -> None:
        pass
    
    def call_iandval(self, bytes_command_arr: bytes) -> None:
        pass
        
command_list = [
    b' \x02\x00\x00'
]
cu = ControlUnit(command_list, 1000).start_processering()