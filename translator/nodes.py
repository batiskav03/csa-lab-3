from lexer import Token

class Node:
    def __init__(self):
        pass
    
class RootNode(Node):
    def __init__(self):
        self.codeStrings: list[Token] = []
    
    def add_node(self, Node) -> None:
        self.codeStrings.append(Node)    
    
class NumberNode(Node):
    def __init__(self, number: Token):
        self.number: Token = number

class VariableNode(Node):
    def __init__(self, var: Token):
        self.var: Token = var
        
class BinaryOp(Node):
    def __init__(self, operator: Token, left_node: Node, right_node: Node):
        self.operator: Token = operator
        self.left_node: Node = left_node
        self.right_node: Node = right_node

# int i = 5;
# while () : {}
# i = i + 5;
# if () : {} else : {}