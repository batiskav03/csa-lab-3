from lexer import Token, TokenEnum

class Node:
    def __init__(self):
        self.childrens: list[Node] = []

    def __str__(self) -> str:
        node_str = ""
        for node in self.childrens:
            node_str += str(node) + ", \n"
        return "{ " + node_str + "}"
    
class RootNode(Node):
    def __init__(self):
        self.childrens: list[Node] = []

    def __str__(self) -> str:
        node_str = ""
        for node in self.childrens:
            node_str += str(node) + ", \n"
        return "{ " + node_str + "}"

class WhileIfNode(RootNode):
    def __init__(self, statement: Node ,token: Token):
        super(WhileIfNode, self).__init__()
        self.token: Token = token
        self.statement: Node = statement
        
    def __str__(self) -> str:
        node_str = ""
        for node in self.childrens:
            node_str += str(node) + ", \n"
        return f"( {self.token.token_type.name.name} statement: [{self.statement}] \n: {node_str}  )"
    
    
class NumberNode(Node):
    def __init__(self, number: Token):
        self.number: Token = number

    def __str__(self) -> str:
        return f"NumberNode: [ {self.number} ]"

class VariableNode(Node):
    def __init__(self, var: Token, type: Token):
        self.var: Token = var
        self.type: Token = type 

    def __str__(self) -> str:
        return f"VariableNode:  [ type: {self.type}  value: {self.var}  ]"
        
class BinaryOp(Node):
    def __init__(self, operator: Token, left_node: Node, right_node: Node):
        self.operator: Token = operator
        self.left_node: Node = left_node
        self.right_node: Node = right_node

    def get_operator(self) -> TokenEnum:
        return self.operator.token_type.name
    
    def get_left_node(self) -> Node:
        return self.left_node
    
    def get_right_node(self) -> Node:
        return self.right_node

    def __str__(self) -> str:
        return f"BinaryOperation: ( \n     left node: {self.left_node} \n       operator: {self.operator} \n        right node: {self.right_node}"


class AssignNode(Node):
    def __init__(self, variable: VariableNode, right_part: Node):
        self.variable: VariableNode = variable
        self.right_part: Node = right_part

    def __str__(self):
        return f"Assign:  \n  {self.variable} right: {self.right_part} \n"

class InitNode(AssignNode):
    def __init__(self, variable: VariableNode, right_part: Node):
        super().__init__(variable, right_part)
        
    def __str__(self):
        return f"Initilization:  \n  {self.variable} right: {self.right_part} \n"