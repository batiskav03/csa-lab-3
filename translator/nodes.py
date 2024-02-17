from lexer import Token

class Node:
    def __init__(self):
        self.childrens: list[Node] = []

    def __str__(self) -> str:
        node_str = ""
        for node in self.childrens:
            node_str += str(node) + ", \n"
        return "{ " + node_str + "}"
    


    
    
class NumberNode(Node):
    def __init__(self, number: Token):
        self.number: Token = number

    def __str__(self) -> str:
        return f"NumberNode: [ {self.number} ]"

class VariableNode(Node):
    def __init__(self, var: Token):
        self.var: Token = var

    def __str__(self) -> str:
        return f"VariableNode:  [ {self.var} ]"
        
class BinaryOp(Node):
    def __init__(self, operator: Token, left_node: Node, right_node: Node):
        self.operator: Token = operator
        self.left_node: Node = left_node
        self.right_node: Node = right_node

    def __str__(self) -> str:
        return f"BinaryOperation: ( \n     left node: {self.left_node} \n       operator: {self.operator} \n        right node: {self.right_node}"



