from __future__ import annotations

import sys
import logging

sys.path.append("../csa-lab-3")
import struct
from typing import Callable, ClassVar

from isa import BUFFER_END, BUFFER_START, MEMORY_SIZE, REGISTERS

alu_operations: dict[str, Callable[[int, int], int]] = {
    "+": lambda left, right: left + right,
    "-": lambda left, right: left - right,
    "%": lambda left, right: left % right,
    "/": lambda left, right: left // right,
    "*": lambda left, right: left * right,
    "&": lambda left, right: left & right,
    "|": lambda left, right: left | right,
}


class ALU:
    def __init__(self) -> None:
        self.N = 0
        self.Z = 1

    def do(self, op: int, left: int, right: int) -> int:
        result: int = alu_operations[op](left, right)
        self.set_flags(result)
        return result
        pass
        return None

    def set_flags(self, value: int) -> None:
        self.Z = 1 if value == 0 else 0
        self.N = 1 if value < 0 else 0

    def get_zero_flag(self) -> int:
        return self.Z

    def get_negative_flag(self) -> int:
        return self.N

    def get_offset(self, unpacked: int) -> int:
        bit_mask = 65535
        unpacked &= bit_mask
        return unpacked
        pass
        return None


class DataPath:
    def __init__(self, program_memory: list[bytes], input_file: str) -> None:
        self.alu = ALU()
        self.memory: list[bytes] = program_memory + [b"\x00\x00\x00\x00"] * (MEMORY_SIZE - len(program_memory))
        self.AR: int = 0
        self.DR: bytes = 0
        self.device = DeviceIO(input_file)
        self.regs: dict[REGISTERS, int] = {
            REGISTERS.RAX: 0,
            REGISTERS.RBX: 0,
            REGISTERS.RCX: 0,
            REGISTERS.RDX: 0,
            REGISTERS.RSP: MEMORY_SIZE - 1,
        }

    def get_dr(self) -> bytes:
        return self.DR

    def get_int_dr(self) -> int:
        return struct.unpack(">i", self.DR)[0]

    def latch_ar(self, value: int) -> None:
        self.AR = value

    def get_register(self, reg: REGISTERS) -> int:
        return self.regs[reg]

    def latch_register(self, reg: REGISTERS, value: int) -> int:
        self.regs[reg] = value

    def get_cur_data(self) -> bytes:
        return self.memory[self.AR]

    def read_cur_command(self) -> None:
        self.latch_dr(self.get_cur_data())

    def latch_dr(self, command: bytes) -> None:
        self.DR = command

    def write_memory(self) -> None:
        self.memory[self.AR] = self.get_dr()

    def output(self, value: int) -> None:
        if value == 1 and self.device.output_type != "int":
            self.device.output_type = "int"
            return
        self.device.output(value)

        if self.device.output_type == "int":
            self.device.output_type = "str"

    def input(self) -> int:
        return self.device.get_char_from_device()


class DeviceIO:
    output_buffer: ClassVar[list] = []
    input_buffer: ClassVar[list] = []

    def __init__(self, input_file: str):
        self.start_buffer_pointer = BUFFER_START
        self.end_buffer_pointer = BUFFER_END
        self.output_type = "str"
        self.input_buffer_pointer = -1
        with open(input_file, encoding="utf-8") as f:
            text = f.read()
            self.input_buffer = [c for c in text]
        self.input_buffer.append("0")

    def output(self, value: int) -> None:
        if self.output_type == "str":
            if value == 0:
                return
            if chr(value) == " ":
                logging.debug("".join(self.output_buffer) + " <- ' '")
            else:
                logging.debug("".join(self.output_buffer) + " <- " + chr(value))
            self.output_buffer.append(chr(value))
        else:
            logging.debug("".join(self.output_buffer) + " <- " + str(value))
            self.output_buffer.append(str(value))

    def get_char_from_device(self) -> int:
        self.input_buffer_pointer += 1
        return (
            ord(self.input_buffer[self.input_buffer_pointer])
            if self.input_buffer[self.input_buffer_pointer] != "0"
            else 0
        )
        
    def output_the_buffer(self):
        for c in self.output_buffer:
            print(c, end="")
        logging.debug("output: " + "".join(self.output_buffer))
        self.output_buffer.clear()
