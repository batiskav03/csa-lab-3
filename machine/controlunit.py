from __future__ import annotations

import logging
import struct

from ..machine.datapath import DataPath
from ..machine.isa import BUFFER_END, BUFFER_START, MAX_OFFSET, OPCODE, REGISTERS, str_opcode


def unassigned_to_int(uint):
    return uint - MAX_OFFSET * 2 if uint >= MAX_OFFSET else uint


class ControlUnit:
    def __init__(self, program_memory: list[bytes], limit: int, input_file) -> None:
        self.tick: int = 0
        self.limit: int = limit
        self.PC = 0
        self.data_path = DataPath(program_memory, input_file)
        self.instr: bytes = b"/x01/x00/x00/x00"
        self.commands_handler: dict[OPCODE, callable] = {
            OPCODE.NOP: self.call_nop,
            OPCODE.MOV: self.call_mov,
            OPCODE.ADD: self.call_add,
            OPCODE.SUB: self.call_sub,
            OPCODE.MUL: self.call_mul,
            OPCODE.DIV: self.call_div,
            OPCODE.MOD: self.call_mod,
            OPCODE.AND: self.call_and,
            OPCODE.OR: self.call_or,
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
            OPCODE.INC: self.call_inc,
        }

    def inc_tick(self) -> None:
        self.tick += 1

    def cur_tick(self) -> int:
        return self.tick

    def start_processering(self) -> None:
        while self.cur_tick() < self.limit:
            self.instruction_fetch()
            self.PC += 1
            self.decode_fetch()
            logging.debug("%s", self)

    def instruction_fetch(self):
        self.data_path.latch_ar(self.PC)
        self.data_path.read_cur_command()
        self.instr = self.data_path.get_dr()
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
        # execution fetch
        rax_value = self.data_path.get_register(REGISTERS.RAX)
        result = self.data_path.alu.do("+", 1, rax_value)
        self.data_path.latch_register(REGISTERS.RAX, result)
        self.inc_tick()

    def call_imov(self, bytes_command_arr: bytes) -> None:
        # operand fetch
        self.i_commands_op(bytes_command_arr)
        # execution fetch
        self.data_path.latch_register(REGISTERS.RAX, self.data_path.get_int_dr())
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
        # operand fetch
        self.i_commands_op(bytes_command_arr)
        # execution fetch
        dr_int = self.data_path.get_int_dr()
        rax_int = self.data_path.get_register(REGISTERS.RAX)
        self.data_path.latch_register(REGISTERS.RAX, self.data_path.alu.do(operator, rax_int, dr_int))
        self.inc_tick()

    def i_commands_op(self, bytes_command_arr: bytes) -> None:
        # finally, data from <adress> = <rbp> - <offset> in DR
        self.calculate_variable_adress(bytes_command_arr)
        self.data_path.latch_dr(self.data_path.get_cur_data())
        self.inc_tick()

    def calculate_variable_adress(self, bytes_command_arr: bytes) -> None:
        # finally, <adress> = <rbp> - <offset> in AR
        self.data_path.latch_register(REGISTERS.RDX, self.data_path.alu.get_offset(self.data_path.get_int_dr()))
        self.inc_tick()
        rdx_int = self.data_path.get_register(REGISTERS.RDX)
        rbx_int = self.data_path.get_register(REGISTERS.RBX)
        self.data_path.latch_ar(self.data_path.alu.do("+", rdx_int, rbx_int))
        self.inc_tick()

    def call_movv(self, bytes_command_arr: bytes) -> None:  # 64 bit instruction
        # operand fetch
        self.data_path.latch_register(REGISTERS.RDX, self.data_path.alu.get_offset(self.data_path.get_int_dr()))
        self.inc_tick()
        rdx_int = self.data_path.get_register(REGISTERS.RDX)
        rbx_int = self.data_path.get_register(REGISTERS.RBX)
        self.data_path.latch_register(REGISTERS.RDX, self.data_path.alu.do("+", rdx_int, rbx_int))
        self.inc_tick()
        self.data_path.latch_ar(self.PC)
        self.inc_tick()
        self.data_path.read_cur_command()
        self.inc_tick()
        self.PC += 1
        # execution fetch
        self.data_path.latch_ar(self.data_path.get_register(REGISTERS.RDX))
        self.inc_tick()
        self.data_path.write_memory()

    def call_nop(self, bytes_command_arr: bytes) -> None:
        pass

    def call_mov(self, bytes_command_arr: bytes) -> None:
        instr = bytes_command_arr[0]
        controll_bits = instr & 15728640
        controll_bits = controll_bits >> 20
        reg1 = instr & 983040
        reg1 = reg1 >> 16
        offset_or_address = instr & 65535
        if controll_bits == 2:
            offset_or_address = unassigned_to_int(offset_or_address)
            self.data_path.latch_ar(self.data_path.alu.do("+", self.PC, offset_or_address))
            self.inc_tick()
            self.data_path.read_cur_command()
            self.inc_tick()
            self.data_path.latch_register(reg1, self.data_path.get_int_dr)
        if controll_bits == 9:
            self.data_path.latch_ar(offset_or_address)
            self.inc_tick()
            self.data_path.latch_dr(struct.pack(">i", self.data_path.get_register(reg1)))
            self.inc_tick()
            self.data_path.write_memory()
            self.inc_tick()
            if BUFFER_START <= offset_or_address <= BUFFER_END:
                self.data_path.output(self.data_path.get_register(reg1))
        if controll_bits == 12:
            self.data_path.latch_ar(self.PC)
            self.inc_tick()
            self.data_path.read_cur_command()
            self.inc_tick()
            self.data_path.latch_register(reg1, self.data_path.get_int_dr())
            self.inc_tick()
            self.PC += 1
        if controll_bits == 1:
            if BUFFER_START <= offset_or_address <= BUFFER_END:
                self.data_path.latch_ar(offset_or_address)
                self.inc_tick()
                self.data_path.read_cur_command()
                self.inc_tick()
                self.data_path.latch_register(reg1, self.data_path.input())
                self.inc_tick()

    def call_alu_operatoin(self, operator: str, bytes_command_arr: bytes) -> None:
        instr = bytes_command_arr[0]
        controll_bits = instr & 15728640
        controll_bits = controll_bits >> 20
        reg1 = instr & 983040
        reg1 = reg1 >> 16
        offset_or_address = instr & 65535
        if controll_bits == 2:
            offset_or_address = unassigned_to_int(offset_or_address)
            self.data_path.latch_ar(self.data_path.alu.do("+", self.PC, offset_or_address))
            self.inc_tick()
            self.data_path.read_cur_command()
            self.inc_tick()
            self.data_path.latch_register(
                reg1,
                self.data_path.alu.do(
                    operator,
                    self.data_path.get_register(reg1),
                    self.data_path.get_int_dr(),
                ),
            )
            self.inc_tick()

    def call_add(self, bytes_command_arr: bytes) -> None:
        self.call_alu_operatoin("+", bytes_command_arr)

    def call_sub(self, bytes_command_arr: bytes) -> None:
        self.call_alu_operatoin("-", bytes_command_arr)

    def call_mul(self, bytes_command_arr: bytes) -> None:
        self.call_alu_operatoin("*", bytes_command_arr)

    def call_div(self, bytes_command_arr: bytes) -> None:
        self.call_alu_operatoin("/", bytes_command_arr)

    def call_mod(self, bytes_command_arr: bytes) -> None:
        self.call_alu_operatoin("%", bytes_command_arr)

    def call_and(self, bytes_command_arr: bytes) -> None:
        self.call_alu_operatoin("&", bytes_command_arr)

    def call_or(self, bytes_command_arr: bytes) -> None:
        self.call_alu_operatoin("|", bytes_command_arr)

    def call_cmp(self, bytes_command_arr: bytes) -> None:
        instr = bytes_command_arr[0]
        controll_bits = instr & 15728640
        controll_bits = controll_bits >> 20
        reg1 = instr & 983040
        reg1 >> 16
        offset_or_address = instr & 65535
        if controll_bits == 2:
            offset_or_address = unassigned_to_int(offset_or_address)
            self.data_path.latch_ar(self.data_path.alu.do("+", self.PC, offset_or_address))
            self.inc_tick()
            self.data_path.read_cur_command()
            self.inc_tick()
            self.data_path.alu.do("-", self.data_path.get_register(reg1), self.data_path.get_int_dr())

    def call_jmp(self, bytes_command_arr: bytes) -> None:
        instr = bytes_command_arr[0]
        controll_bits = instr & 15728640
        controll_bits = controll_bits >> 20
        offset_or_address = instr & 65535
        if controll_bits == 2:
            offset_or_address = unassigned_to_int(offset_or_address)
            alu_res = self.data_path.alu.do("+", self.PC - 1, offset_or_address)
            self.data_path.latch_dr(struct.pack(">i", alu_res))
            self.inc_tick()
            self.PC = self.data_path.get_int_dr()
        elif controll_bits == 0:
            self.PC = offset_or_address
        self.inc_tick()

    def call_jz(self, bytes_command_arr: bytes) -> None:
        instr = bytes_command_arr[0]
        controll_bits = instr & 15728640
        controll_bits = controll_bits >> 20
        offset_or_address = instr & 65535
        if self.data_path.alu.Z == 1:
            if controll_bits == 2:
                offset_or_address = unassigned_to_int(offset_or_address)
                alu_res = self.data_path.alu.do("+", self.PC - 1, offset_or_address)
                self.data_path.latch_dr(struct.pack(">i", alu_res))
                self.inc_tick()
                self.PC = self.data_path.get_int_dr()
            elif controll_bits == 0:
                self.PC = offset_or_address
            self.inc_tick()

    def call_jn(self, bytes_command_arr: bytes) -> None:
        instr = bytes_command_arr[0]
        controll_bits = instr & 15728640
        controll_bits = controll_bits >> 20
        offset_or_address = instr & 65535
        if self.data_path.alu.N == 1:
            if controll_bits == 2:
                offset_or_address = unassigned_to_int(offset_or_address)
                alu_res = self.data_path.alu.do("+", self.PC - 1, offset_or_address)
                self.data_path.latch_dr(struct.pack(">i", alu_res))
                self.inc_tick()
                self.PC = self.data_path.get_int_dr()
            elif controll_bits == 0:
                self.PC = offset_or_address
            self.inc_tick()

    def call_jp(self, bytes_command_arr: bytes) -> None:
        instr = bytes_command_arr[0]
        controll_bits = instr & 15728640
        controll_bits = controll_bits >> 20
        offset_or_address = instr & 65535
        if self.data_path.alu.N == 0:
            if controll_bits == 2:
                offset_or_address = unassigned_to_int(offset_or_address)
                alu_res = self.data_path.alu.do("+", self.PC - 1, offset_or_address)
                self.data_path.latch_dr(struct.pack(">i", alu_res))
                self.inc_tick()
                self.PC = self.data_path.get_int_dr()
            elif controll_bits == 0:
                self.PC = offset_or_address
            self.inc_tick()

    def call_hlt(self, bytes_command_arr: bytes) -> None:
        self.limit = self.tick - 1
        self.data_path.device.output_the_buffer()
        logging.info("Simulation ended")

    def call_mova(self, bytes_command_arr: bytes) -> None:
        self.calculate_variable_adress(bytes_command_arr)
        self.data_path.latch_dr(struct.pack(">i", self.data_path.get_register(REGISTERS.RAX)))
        self.inc_tick()
        self.data_path.write_memory()
        self.inc_tick()

    def call_movva(self, bytes_command_arr: bytes) -> None:
        self.data_path.latch_ar(self.PC)
        self.inc_tick()
        self.data_path.read_cur_command()
        self.inc_tick()
        self.data_path.latch_register(REGISTERS.RAX, self.data_path.get_int_dr())
        self.PC += 1
        self.inc_tick()

    def call_pusha(self, bytes_command_arr: bytes) -> None:
        self.data_path.latch_register(
            REGISTERS.RSP,
            self.data_path.alu.do("-", self.data_path.get_register(REGISTERS.RSP), 1),
        )
        self.inc_tick()
        self.data_path.latch_ar(self.data_path.get_register(REGISTERS.RSP))
        self.inc_tick()
        self.data_path.latch_dr(struct.pack(">i", self.data_path.get_register(REGISTERS.RAX)))
        self.inc_tick()
        self.data_path.write_memory()
        self.inc_tick()

    def call_popa(self, bytes_command_arr: bytes) -> None:
        self.data_path.latch_ar(self.data_path.get_register(REGISTERS.RSP))
        self.inc_tick()
        self.data_path.latch_register(
            REGISTERS.RSP,
            self.data_path.alu.do("+", self.data_path.get_register(REGISTERS.RSP), 1),
        )
        self.inc_tick()
        self.data_path.read_cur_command()
        self.inc_tick()
        self.data_path.latch_register(REGISTERS.RAX, self.data_path.get_int_dr())
        self.inc_tick()

    def call_peeka(self, bytes_command_arr: bytes) -> None:
        self.data_path.latch_ar(self.data_path.get_register(REGISTERS.RSP))
        self.inc_tick()
        self.data_path.read_cur_command()
        self.inc_tick()
        self.data_path.latch_register(REGISTERS.RAX, self.data_path.get_int_dr())
        self.inc_tick()

    def call_icmp(self, bytes_command_arr: bytes) -> None:
        self.i_commands_op(bytes_command_arr)
        self.data_path.alu.do("-", self.data_path.get_register(REGISTERS.RAX), self.data_path.get_int_dr())

    def call_jneq(self, bytes_command_arr: bytes) -> None:
        instr = bytes_command_arr[0]
        controll_bits = instr & 15728640
        controll_bits = controll_bits >> 20
        offset_or_address = instr & 65535
        if self.data_path.alu.Z == 0:
            if controll_bits == 2:
                offset_or_address = unassigned_to_int(offset_or_address)
                alu_res = self.data_path.alu.do("+", self.PC - 1, offset_or_address)
                self.data_path.latch_dr(struct.pack(">i", alu_res))
                self.inc_tick()
                self.PC = self.data_path.get_int_dr()
            elif controll_bits == 0:
                self.PC = offset_or_address
            self.inc_tick()

    def call_jne(self, bytes_command_arr: bytes) -> None:
        instr = bytes_command_arr[0]
        controll_bits = instr & 15728640
        controll_bits = controll_bits >> 20
        offset_or_address = instr & 65535
        if self.data_path.alu.Z == 1 or self.data_path.alu.N == 1:
            if controll_bits == 2:
                offset_or_address = unassigned_to_int(offset_or_address)
                alu_res = self.data_path.alu.do("+", self.PC - 1, offset_or_address)
                self.data_path.latch_dr(struct.pack(">i", alu_res))
                self.inc_tick()
                self.PC = self.data_path.get_int_dr()
            elif controll_bits == 0:
                self.PC = offset_or_address
            self.inc_tick()

    def call_jpe(self, bytes_command_arr: bytes) -> None:
        instr = bytes_command_arr[0]
        controll_bits = instr & 15728640
        controll_bits = controll_bits >> 20
        offset_or_address = instr & 65535
        if self.data_path.alu.Z == 1 or self.data_path.alu.N == 0:
            if controll_bits == 2:
                offset_or_address = unassigned_to_int(offset_or_address)
                alu_res = self.data_path.alu.do("+", self.PC - 1, offset_or_address)
                self.data_path.latch_dr(struct.pack(">i", alu_res))
                self.inc_tick()
                self.PC = self.data_path.get_int_dr()
            elif controll_bits == 0:
                self.PC = offset_or_address
            self.inc_tick()

    def call_jnz(self, bytes_command_arr: bytes) -> None:
        instr = bytes_command_arr[0]
        controll_bits = instr & 15728640
        controll_bits = controll_bits >> 20
        offset_or_address = instr & 65535
        if self.data_path.alu.Z == 0:
            if controll_bits == 2:
                offset_or_address = unassigned_to_int(offset_or_address)
                alu_res = self.data_path.alu.do("+", self.PC - 1, offset_or_address)
                self.data_path.latch_dr(struct.pack(">i", alu_res))
                self.inc_tick()
                self.PC = self.data_path.get_int_dr()
            elif controll_bits == 0:
                self.PC = offset_or_address
            self.inc_tick()

    def call_cmpa(self, bytes_command_arr: bytes) -> None:
        self.data_path.latch_ar(self.PC)
        self.inc_tick()
        self.data_path.read_cur_command()
        self.inc_tick()
        self.PC += 1
        self.data_path.alu.do("-", self.data_path.get_register(REGISTERS.RAX), self.data_path.get_int_dr())
        self.inc_tick()

    def call_ival_alu_command(self, operator: str, bytes_command_arr: bytes) -> None:
        self.data_path.latch_ar(self.PC)
        self.inc_tick()
        self.data_path.read_cur_command()
        self.inc_tick()
        self.PC += 1
        self.data_path.latch_register(
            REGISTERS.RAX,
            self.data_path.alu.do(
                operator,
                self.data_path.get_register(REGISTERS.RAX),
                self.data_path.get_int_dr(),
            ),
        )
        self.inc_tick()

    def call_iaddval(self, bytes_command_arr: bytes) -> None:
        self.call_ival_alu_command("+", bytes_command_arr)

    def call_isubval(self, bytes_command_arr: bytes) -> None:
        self.call_ival_alu_command("-", bytes_command_arr)

    def call_imovsp(self, bytes_command_arr: bytes) -> None:
        self.data_path.latch_ar(self.data_path.get_register(REGISTERS.RSP))
        self.inc_tick()
        self.data_path.read_cur_command()
        self.inc_tick()
        self.data_path.latch_ar(self.data_path.get_int_dr())
        self.inc_tick()
        self.data_path.read_cur_command()
        self.inc_tick()
        self.data_path.latch_register(REGISTERS.RAX, self.data_path.get_int_dr())
        self.inc_tick()

    def call_imulval(self, bytes_command_arr: bytes) -> None:
        self.call_ival_alu_command("*", bytes_command_arr)

    def call_idivval(self, bytes_command_arr: bytes) -> None:
        self.call_ival_alu_command("/", bytes_command_arr)

    def call_imodval(self, bytes_command_arr: bytes) -> None:
        self.call_ival_alu_command("%", bytes_command_arr)

    def call_iandval(self, bytes_command_arr: bytes) -> None:
        self.call_ival_alu_command("&", bytes_command_arr)

    def __repr__(self):
        return "execute_command {:>15} | tick: {:10d} | pc: {:10d} | %rax: {:10d} | %rbx: {:10d} | %rcx: {:10d} | %rdx {:10d} | %rsp: {:10d} | dr: {:10d}".format(
            str_opcode[struct.unpack(">Bbbb", self.instr)[0]],
            self.tick,
            self.PC,
            self.data_path.get_register(REGISTERS.RAX),
            self.data_path.get_register(REGISTERS.RBX),
            self.data_path.get_register(REGISTERS.RCX),
            self.data_path.get_register(REGISTERS.RDX),
            self.data_path.get_register(REGISTERS.RSP),
            self.data_path.get_int_dr(),
        )
