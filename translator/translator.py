import sys

from nodes import AssignNode, BinaryOp, InitNode, Node, NumberNode, RootNode, VariableNode, WhileIfNode
from machine.isa import Instruction
from lexer import TokenEnum, Tokenizer
from translator.ast import AstParser


class Translator:

    def __init__(self, ast: Node):
        self.ast: Node = ast
        self.commands: list[Instruction] = []


    

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
        #todo: скорее всего придеться разделить ноду variable 
        #                       на две - присваивание и отдельную переменную
    
    

    def ast_to_list(self):
        current_node = self.ast
        if (isinstance(current_node, RootNode)):
            children = current_node.children
            for node in children:
                self.translate_node(node)



def main(source, target):
    with open(source, encoding="UTF-8") as f:
        code = f.read()
    tokens = Tokenizer(code).start_analyze()
    ast_tree = AstParser(tokens).parse_code()
    instr_list = Translator(ast_tree).ast_to_list()

if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    _, source, target = sys.argv
    main(source, target)