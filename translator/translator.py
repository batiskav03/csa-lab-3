import sys
sys.path.append("../csa-lab-3")
from machine.isa import Instruction, OPCODE
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


    def process_binary_operation(self, node: BinaryOp):
        left = node.get_left_node()
        right = node.get_right_node()
        if (isinstance(left,BinaryOp)):
            self.process_binary_operation(left)

        if (isinstance(right, BinaryOp)):
            self.process_binary_operation(right)
        
        op = node.get_operator()

        if (op == "+"):
            opcode = OPCODE["ADD"]
            if (isinstance(left, NumberNode) and isinstance(right, NumberNode)):
                summary = left.get_value() + right.get_value()

                print(bin(opcode)[2:] + bin(summary)[2:])
                if (summary < 256):
                    #todo: в одну команду
                    pass
                else:
                    #todo: в две команды
                    pass
            else: 
                pass
                #если число помещается в 1 байт, то в адрес моде НЕ ставим управляющий бит, и помещаем число в команду, 
                                    # иначе помещаем число следом за командой и тащим уже оттуда
            # нужно добавить указатели на память, собственно и расписать ее
            

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

nudes = BinaryOp(Token(TokenType(None, ""), "+"),NumberNode(Token(TokenType(None, ""), "127")), NumberNode(Token(TokenType(None, ""), "128")))
Translator([]).process_binary_operation(nudes)

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