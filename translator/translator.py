from __future__ import annotations

import sys

from translator.ast_parser import AstParser
from translator.lexer import TokenEnum, Tokenizer

sys.path.append("../csa_lab3")

from machine.isa import (
    BUFFER_START,
    OPCODE,
    REGISTERS,
    AdModRegAdressInstruction,
    Instruction,
    OffsetInstruction,
    OffsetInstructionWithAdMon,
    SecondWord,
)
from translator.nodes import (
    AssignNode,
    BinaryOp,
    InitNode,
    Node,
    NumberNode,
    PrintNode,
    ReadNode,
    RootNode,
    VariableNode,
    WhileIfNode,
)


class Translator:
    # https://godbolt.org/
    def __init__(self, ast: Node):
        self.ast: Node = ast
        self.commands: list[Instruction] = []
        self.stack_pointer: int = 0
        self.buffer_pointer: int = BUFFER_START
        self.variable_offset: dict[str, int] = {}
        self.str_var: dict[str, int] = {}  # var, offset

    def operation_with_rax_value(self, operator: str) -> Instruction:
        if operator == "+":
            return Instruction(OPCODE.IADDVAL)
        if operator == "-":
            return Instruction(OPCODE.ISUBVAL)
        if operator == "*":
            return Instruction(OPCODE.IMULVAL)
        if operator == "/":
            return Instruction(OPCODE.IDIVVAL)
        if operator == "%":
            return Instruction(OPCODE.IMODVAL)
        if operator == "and":
            return Instruction(OPCODE.IANDVAL)
        return None

    def operation_with_rax_offset_value(self, operator: str, offset: int) -> Instruction:
        if operator == "+":
            return OffsetInstruction(OPCODE.IADD, offset)
        if operator == "-":
            return OffsetInstruction(OPCODE.ISUB, offset)
        if operator == "*":
            return OffsetInstruction(OPCODE.IMUL, offset)
        if operator == "/":
            return OffsetInstruction(OPCODE.IDIV, offset)
        if operator == "%":
            return OffsetInstruction(OPCODE.IMOD, offset)
        if operator == "and":
            return OffsetInstruction(OPCODE.IAND, offset)
        return None

    def process_binary_op_var_and_num(self, left: Node, right: Node, var_str: str, operator: str) -> None:
        var_node = right if isinstance(right, VariableNode) else left
        number_node = right if isinstance(right, NumberNode) else left
        var_target = var_node.var.text
        var_offset = self.variable_offset.get(var_target)
        mov_to_rax = OffsetInstruction(OPCODE.IMOV, var_offset)
        operation_to_rax = self.operation_with_rax_value(operator)
        second_word = SecondWord(number_node.get_value())
        mov_rax_to_mem = OffsetInstruction(OPCODE.MOVA, self.variable_offset[var_str])
        self.commands += [mov_to_rax, operation_to_rax, second_word, mov_rax_to_mem]

    def process_binary_op_var_and_var(self, left: Node, right: Node, var_str: str, operator: str) -> None:
        var_left = left.var.text
        var_left_offset = self.variable_offset.get(var_left)
        var_right = right.var.text
        var_right_offset = self.variable_offset.get(var_right)
        mov_to_rax = OffsetInstruction(OPCODE.IMOV, var_left_offset)
        operation_to_rax = self.operation_with_rax_offset_value(operator, var_right_offset)
        mov_rax_to_mem = OffsetInstruction(OPCODE.MOVA, self.variable_offset[var_str])
        self.commands += [mov_to_rax, operation_to_rax, mov_rax_to_mem]

    def process_binary_op_num_and_num(self, left: NumberNode, right: NumberNode, var_str: str, operator: str) -> None:
        res: int
        if operator == "+":
            res = left.get_value() + right.get_value()
        elif operator == "-":
            res = left.get_value() - right.get_value()
        elif operator == "*":
            res = left.get_value() * right.get_value()
        elif operator == "/":
            res = left.get_value() / right.get_value()
        elif operator == "%":
            res = left.get_value() % right.get_value()
        elif operator == "and":
            res = left.get_value() & right.get_value()
        movv = OffsetInstruction(OPCODE.MOVV, self.variable_offset[var_str])
        value = SecondWord(res)
        self.commands += [movv, value]

    def process_binary_op(self, binary_node: BinaryOp, var_str: str) -> None:
        left = binary_node.get_left_node()
        right = binary_node.get_right_node()
        operator = binary_node.get_operator()
        if isinstance(left, NumberNode) and isinstance(right, NumberNode):
            self.process_binary_op_num_and_num(left, right, var_str, operator)
        elif (isinstance(left, NumberNode) and isinstance(right, VariableNode)) or (
            isinstance(left, VariableNode) and isinstance(right, NumberNode)
        ):
            self.process_binary_op_var_and_num(left, right, var_str, operator)
        elif isinstance(left, VariableNode) and isinstance(right, VariableNode):
            self.process_binary_op_var_and_var(left, right, var_str, operator)

    def process_number_node(self, node: NumberNode, var_str: str) -> None:
        command = OffsetInstruction(OPCODE.MOVV, self.variable_offset[var_str])
        value = SecondWord(int(node.number.text))
        self.commands += [command, value]

    def process_variable_node(self, node: VariableNode, var_str: str) -> None:
        var_name = node.var.text
        mov_to_rax = OffsetInstruction(OPCODE.IMOV, self.variable_offset[var_name])
        mov_rax_to_mem = OffsetInstruction(OPCODE.MOVA, self.variable_offset[var_str])
        self.commands += [mov_to_rax, mov_rax_to_mem]

    def process_int_initilization(self, node: InitNode) -> None:
        variable_node = node.variable
        var_str = variable_node.var.text
        right_part = node.right_part
        # определяю offset относительно rbp для переменной
        if self.variable_offset.get(var_str, None) is None:
            self.variable_offset[var_str] = self.stack_pointer
            self.stack_pointer += 1
        else:
            raise ValueError()

        if isinstance(right_part, NumberNode):
            self.process_number_node(right_part, var_str)
        elif isinstance(right_part, VariableNode):
            self.process_variable_node(right_part, var_str)
        elif isinstance(right_part, BinaryOp):
            self.process_binary_op(right_part, var_str)

    def process_assign(self, node: AssignNode) -> None:
        variable_node = node.variable
        var_str = variable_node.var.text
        right_part = node.right_part
        if self.variable_offset.get(var_str, None) is None:
            raise ValueError()

        if isinstance(right_part, NumberNode):
            self.process_number_node(right_part, var_str)
        elif isinstance(right_part, VariableNode):
            self.process_variable_node(right_part, var_str)
        elif isinstance(right_part, BinaryOp):
            self.process_binary_op(right_part, var_str)

    def calculate_cmp(self, left_node: Node, right_node: Node) -> list[Instruction]:
        commands: list[Instruction] = []
        if isinstance(left_node, NumberNode):
            movva = Instruction(OPCODE.MOVVA)
            value = SecondWord(int(left_node.number.text))
            commands += [movva, value]
        elif isinstance(left_node, VariableNode):
            imov = OffsetInstruction(OPCODE.IMOV, self.variable_offset[left_node.var.text])
            commands += [imov]
        if isinstance(right_node, NumberNode):
            cmpa = Instruction(OPCODE.CMPA)
            value = SecondWord(int(right_node.number.text))
            commands += [cmpa, value]
        elif isinstance(right_node, VariableNode):
            icmp = OffsetInstruction(OPCODE.ICMP, self.variable_offset[right_node.var.text])
            commands += [icmp]
        return commands

    def process_while_condition(self, prev_len: int, node: BinaryOp) -> list[Instruction]:
        left = node.get_left_node()
        right = node.get_right_node()
        operator = node.get_operator()
        compare_commands_list = self.calculate_cmp(left, right)
        length = len(compare_commands_list) + prev_len
        jump: Instruction
        # неполная длинна епта
        if operator == "==":
            jump = OffsetInstructionWithAdMon(OPCODE.JZ, 2, -length)
        elif operator == "<":
            jump = OffsetInstructionWithAdMon(OPCODE.JN, 2, -length)
        elif operator == ">":
            jump = OffsetInstructionWithAdMon(OPCODE.JP, 2, -length)
        elif operator == "<=":
            jump = OffsetInstructionWithAdMon(OPCODE.JNE, 2, -length)
        elif operator == ">=":
            jump = OffsetInstructionWithAdMon(OPCODE.JPE, 2, -length)
        elif operator == "!=":
            jump = OffsetInstructionWithAdMon(OPCODE.JNEQ, 2, -length)
        compare_commands_list.append(jump)
        return compare_commands_list

    def process_while_statement(self, node: WhileIfNode) -> None:
        condition = node.statement
        saved_state = self.commands.copy()
        self.commands = []
        self.ast_to_list(node)
        commands_len = len(self.commands)
        compare_commads_list = self.process_while_condition(commands_len, condition)
        jmp = OffsetInstructionWithAdMon(OPCODE.JMP, 2, len(self.commands) + 1)
        self.commands = [*saved_state, jmp, *self.commands, *compare_commads_list]

    def process_if_condition(self, prev_len: int, node: BinaryOp) -> list[Instruction]:
        left = node.get_left_node()
        right = node.get_right_node()
        operator = node.get_operator()
        compare_commands_list = self.calculate_cmp(left, right)
        len(compare_commands_list)

        jump: Instruction
        if operator == "==":
            jump = OffsetInstructionWithAdMon(OPCODE.JNEQ, 2, prev_len + 1)
        elif operator == "<":
            jump = OffsetInstructionWithAdMon(OPCODE.JPE, 2, prev_len + 1)
        elif operator == ">":
            jump = OffsetInstructionWithAdMon(OPCODE.JNZ, 2, prev_len + 1)
        elif operator == "<=":
            jump = OffsetInstructionWithAdMon(OPCODE.JP, 2, prev_len + 1)
        elif operator == ">=":
            jump = OffsetInstructionWithAdMon(OPCODE.JN, 2, prev_len + 1)
        elif operator == "!=":
            jump = OffsetInstructionWithAdMon(OPCODE.JZ, 2, prev_len + 1)
        compare_commands_list.append(jump)

        return compare_commands_list

    def process_if_statement(self, node: WhileIfNode) -> None:
        condition = node.statement
        saved_state = self.commands.copy()
        self.commands = []
        self.ast_to_list(node)
        if node.else_node is not None:
            commands_len = len(self.commands) + 1
        else:
            commands_len = len(self.commands)
        self.commands = self.process_if_condition(commands_len, condition) + self.commands

        new_state = []
        if node.else_node is not None:
            new_state = self.commands
            self.commands = []
            self.ast_to_list(node.else_node)
            jmp = OffsetInstructionWithAdMon(OPCODE.JMP, 2, len(self.commands) + 1)
            self.commands = [jmp, *self.commands]
        self.commands = saved_state + new_state + self.commands

    def process_output(self, node: PrintNode):
        type_token = node.get_token_type()
        commands: list[Instruction] = []
        if type_token == TokenEnum.STRING:
            text = node.get_token_text()
            for ch in text:
                if ch != "'":
                    commands.append(SecondWord(ord(ch)))
            commands.append(SecondWord(0))
            length = len(commands)
            jump = OffsetInstructionWithAdMon(OPCODE.JMP, 2, length + 1)
            commands = [jump, *commands]
            movva = Instruction(OPCODE.MOVVA)
            movva_data = SecondWord(3 + len(self.commands))
            pusha = Instruction(OPCODE.PUSHA)
            imovsp = Instruction(OPCODE.IMOVSP)
            mov_to_buff = AdModRegAdressInstruction(OPCODE.MOV, 9, REGISTERS.RAX, self.buffer_pointer)
            cmpa = Instruction(OPCODE.CMPA)
            cmpa_data = SecondWord(0)
            commands_after_string = [
                movva,
                movva_data,
                pusha,
                imovsp,
                mov_to_buff,
                cmpa,
                cmpa_data,
            ]
            pop = Instruction(OPCODE.POPA)
            inc = Instruction(OPCODE.INC)
            command_after_jump = [pop, inc, pusha]
            jz = OffsetInstructionWithAdMon(OPCODE.JZ, 2, len(command_after_jump) + 2)
            commands_after_string.append(jz)
            jmp = OffsetInstructionWithAdMon(
                OPCODE.JMP,
                2,
                -(len(command_after_jump) + len(commands_after_string) - 3),
            )
            command_after_jump.append(jmp)
            commands = commands + commands_after_string + command_after_jump
            self.commands += commands

        elif type_token == TokenEnum.LITTERAL:
            if node.var_type.text == "int":
                self.commands.append(Instruction(OPCODE.MOVVA))
                self.commands.append(SecondWord(1))
                self.commands.append(AdModRegAdressInstruction(OPCODE.MOV, 9, REGISTERS.RAX, self.buffer_pointer))
                self.commands.append(OffsetInstruction(OPCODE.IMOV, self.variable_offset[node.get_token_text()]))
                self.commands.append(AdModRegAdressInstruction(OPCODE.MOV, 9, REGISTERS.RAX, self.buffer_pointer))
            else:
                self.commands.append(OffsetInstruction(OPCODE.IMOV, self.variable_offset[node.get_token_text()]))
                self.commands.append(AdModRegAdressInstruction(OPCODE.MOV, 9, REGISTERS.RAX, self.buffer_pointer))
            self.commands.append(Instruction(OPCODE.MOVVA))
            self.commands.append(SecondWord(0))
            self.commands.append(AdModRegAdressInstruction(OPCODE.MOV, 9, REGISTERS.RAX, self.buffer_pointer))

    def process_input(self, node: ReadNode):
        variable = node.get_token_text()
        self.commands.append(AdModRegAdressInstruction(OPCODE.MOV, 1, REGISTERS.RAX, 40000))
        self.commands.append(OffsetInstruction(OPCODE.MOVA, self.variable_offset[variable]))

    def translate_node(self, node: Node):
        if isinstance(node, WhileIfNode):
            if node.token.token_type.name == TokenEnum.IF:
                self.process_if_statement(node)
            else:
                self.process_while_statement(node)
        elif isinstance(node, InitNode):
            self.process_int_initilization(node)
        elif isinstance(node, AssignNode):
            self.process_assign(node)
        elif isinstance(node, PrintNode):
            self.process_output(node)
        elif isinstance(node, ReadNode):
            self.process_input(node)

    def ast_to_list(self, node: Node) -> None:
        current_node = node
        if isinstance(current_node, RootNode):
            children = current_node.childrens
            for node in children:
                self.translate_node(node)


def main(source, target, debug_file):
    with open(source, encoding="UTF-8") as fr:
        code = fr.read()
    tokens = Tokenizer(code).start_analyze()
    ast_tree = AstParser(tokens).parse_code()
    instr_list = Translator(ast_tree)
    instr_list.ast_to_list(instr_list.ast)
    instr_list: list[Instruction] = instr_list.commands
    pre = AdModRegAdressInstruction(OPCODE.MOV, 12, REGISTERS.RBX, 0)
    s_w = SecondWord(45000)
    hlt = Instruction(OPCODE.HLT)
    instr_list = [pre, s_w, *instr_list, hlt]
    with open(target, "wb") as fw, open(debug_file, "w") as file_debug:
        j = 0
        for instruction in instr_list:
            file_debug.write(f" {j} - {instruction.get_bytes_value().hex()} - {instruction}\n")
            fw.write(instruction.get_bytes_value())
            j += 1



if __name__ == "__main__":
    assert len(sys.argv) == 4, "Wrong arguments: translator.py <input_file> <target_file> <debug_file>"
    _, source, target, debug = sys.argv
    main(source, target, debug)
