import sys
sys.path.append("../csa-lab-3")
from machine.isa import Instruction, OPCODE, MEMORY_SIZE, REGISTERS, OffsetInstruction, SecondWord, MAX_VALUE
from lexer import Token, TokenType
from nodes import AssignNode, BinaryOp, InitNode, Node, NumberNode, RootNode, VariableNode, WhileIfNode
from lexer import TokenEnum, Tokenizer
from ast import AstParser


class Translator:
    # todo: должна быть мапа памяти( получаеться надо расписать память), чтобы на уровне компиляции мы знали что откуда тянуть, куда закидывать
    # https://godbolt.org/
    def __init__(self, ast: Node):
        self.ast: Node = ast
        self.commands: list[Instruction] = []
        self.stack_pointer: int = 0
        self.variable_offset: dict[str, int] = {}
        



    
    def operation_with_rax_value(operator: str) -> Instruction:
        if (operator == "+"):
            return Instruction(OPCODE.IADDVAL)
        if (operator == "-"):
            return Instruction(OPCODE.ISUBVAL)
        if (operator == "*"):
            return Instruction(OPCODE.IMULVAL)
        if (operator == "/"):
            return Instruction(OPCODE.IDIVVAL)
        
    def operation_with_rax_offset_value(operator: str, offset: int) -> Instruction:
        if (operator == "+"):
            return OffsetInstruction(OPCODE.IADD, offset)
        elif (operator == "-"):
            return  OffsetInstruction(OPCODE.ISUB, offset)
        elif (operator == "*"):
            return OffsetInstruction(OPCODE.IMUL, offset)
        elif (operator == "/"):
            return OffsetInstruction(OPCODE.IDIV, offset)
    
    def process_binary_op_var_and_num(self, left: Node, right: Node, var_str: str, operator: str) -> None:
        target_node = right if isinstance(right, VariableNode) else left
        var_target = target_node.get_value()
        var_target = right.type.text
        var_offset = self.variable_offset.get(var_target)
        mov_to_rax = OffsetInstruction(OPCODE.IMOV, var_offset)
        operation_to_rax = self.operation_with_rax_value(operator)
        second_word = SecondWord(target_node.get_value())
        mov_rax_to_mem = OffsetInstruction(OPCODE.MOVA, self.variable_offset[var_str])
        self.commands += [mov_to_rax, operation_to_rax, second_word, mov_rax_to_mem]
    
    def process_binary_op_var_and_var(self, left: Node, right: Node, var_str: str, operator: str) -> None:
        var_left = left.type.text
        var_left_offset = self.variable_offset.get(var_left)
        var_right = right.type.text
        var_right_offset = self.variable_offset.get(var_right)
        mov_to_rax = OffsetInstruction(OPCODE.IMOV, var_left_offset)
        operation_to_rax = self.operation_with_rax_offset_value(operator, var_right_offset)
        mov_rax_to_mem = OffsetInstruction(OPCODE.MOVA, self.variable_offset[var_str])
        self.commands += [mov_to_rax, operation_to_rax, mov_rax_to_mem]
        
    def process_binary_op_num_and_num(self, left: NumberNode, right: NumberNode, var_str: str,  operator: str) -> None:
        res: int
        if (operator == "+"):
            res = left.get_value() + right.get_value()
        elif (operator == "-"):
            res = left.get_value() - right.get_value()
        elif (operator == "*"):
            res = left.get_value() * right.get_value()
        elif (operator == "/"):
            res = left.get_value() / right.get_value()
        if res > MAX_VALUE:
            raise ValueError("int overflow")
        movv = OffsetInstruction(OPCODE.MOVV, self.variable_offset[var_str])
        value = SecondWord(res)
        self.commands += [movv, value]
        
    def process_binary_op(self, binary_node: BinaryOp , var_str: str) -> None:
        left = binary_node.get_left_node()
        right = binary_node.get_right_node()
        operator = binary_node.get_operator()
        if (isinstance(left, BinaryOp)):
            self.process_binary_op(left, var_str)
        if (isinstance(right, BinaryOp)):
            self.process_binary_op(right, var_str)
        elif (isinstance(left, NumberNode) and isinstance(right, NumberNode)):
            self.process_binary_op_num_and_num(left, right, var_str, operator)
        elif ((isinstance(left, NumberNode) and isinstance(right, VariableNode))
                    or (isinstance(left, VariableNode) and isinstance(right, NumberNode))):
            self.process_binary_op_var_and_num(left, right, var_str, operator)
        elif (isinstance(left, VariableNode) and isinstance(right, VariableNode)):
            self.process_binary_op_var_and_var(left, right)
        
       
    def process_number_node(self, node: NumberNode, var_str: str) -> None:
        command = OffsetInstruction(OPCODE.MOVV, self.variable_offset[var_str])
        value = SecondWord(int(node.number.text))
        self.commands += [command, value]
        
    def process_variable_node(self, node: VariableNode, var_str: str) -> None:
        var_name = node.type.text
        mov_to_rax = OffsetInstruction(OPCODE.IMOV, self.variable_offset[var_name])
        mov_rax_to_mem = OffsetInstruction(OPCODE.MOVA, self.variable_offset[var_str])
        self.commands += [mov_to_rax, mov_rax_to_mem]
    
    def process_initilization(self, node: AssignNode):
        variable_node = node.variable
        var_str = variable_node.var.text
        right_part = node.right_part
        # определяю offset относительно rbp для переменной
        if (self.variable_offset.get(var_str, None) == None):
            self.variable_offset[var_str] = self.stack_pointer
            self.stack_pointer += 1
        else:
            raise ValueError(f"variable {var_str} already has been initilazed")
        
        if (isinstance(right_part, NumberNode)):
            self.process_number_node(right_part, var_str)
        elif (isinstance(right_part, VariableNode)):
            self.process_variable_node(right_part, var_str)
        elif (isinstance(right_part, BinaryOp)):
            self.process_binary_op(right_part, var_str)

                
                
                
                

    def translate_node(self, node: Node):
        if (isinstance(node, WhileIfNode)):
            if (node.token.token_type.name == TokenEnum.IF):
                self.process_if_statement(node)
            else:
                self.process_else_statement(node)
        elif (isinstance(node, AssignNode)):
            self.process_assign(node)
        elif (isinstance(node, InitNode)):
            self.process_initilization(node)
        elif (isinstance(node, BinaryOp)):
            self.process_binary_operation(node)
        
    
    

    def ast_to_list(self):
        current_node = self.ast
        if (isinstance(current_node, RootNode)):
            children = current_node.children
            for node in children:
                self.translate_node(node)

nudes = AssignNode(VariableNode(Token(TokenType(TokenEnum.LITTERAL, ""), "i"), Token(TokenType(TokenEnum.TYPE, ""), "int")),BinaryOp(Token(TokenType(None, ""), "*"),NumberNode(Token(TokenType(None, ""), "127")), NumberNode(Token(TokenType(None, ""), "128"))))
nudes1 = AssignNode(VariableNode(Token(TokenType(TokenEnum.LITTERAL, ""), "j"), Token(TokenType(TokenEnum.TYPE, ""), "int")),BinaryOp(Token(TokenType(None, ""), "+"),NumberNode(Token(TokenType(None, ""), "127")), NumberNode(Token(TokenType(None, ""), "128"))))
trans = Translator([])
trans.process_initilization(nudes)
trans.process_initilization(nudes1)
for i in trans.commands:
    print(i)

# def main(source, target):
#     with open(source, encoding="UTF-8") as f:
#         code = f.read()
#     tokens = Tokenizer(code).start_analyze()
#     ast_tree = AstParser(tokens).parse_code()
#     instr_list = Translator(ast_tree).ast_to_list()

# if __name__ == "__main__":
#     assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
#     _, source, target = sys.argv
#     main(source, target)