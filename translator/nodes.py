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

class ElseNode(RootNode):
    def __init__(self):
        super().__init__()

class WhileIfNode(RootNode):
    def __init__(self, statement: Node ,token: Token, else_node: ElseNode = None ):
        super(WhileIfNode, self).__init__()
        self.token: Token = token
        self.statement: Node = statement
        self.else_node: ElseNode = else_node
    
    def set_else_block(self, node: ElseNode) -> None:
        self.else_node = node
        
    def __str__(self) -> str:
        node_str = ""
        for node in self.childrens:
            node_str += str(node) + ", \n"
        return f"( {self.token.token_type.name.name} statement: [{self.statement}] \n: {node_str}  )"
    
class ElseNode(RootNode):
    def __init__(self):
        super().__init__()
        
    
    
class NumberNode(Node):
    def __init__(self, number: Token):
        self.number: Token = number

    def get_value(self) -> int:
        return int(self.number.text)

    def __str__(self) -> str:
        return f"NumberNode: [ {self.number} ]"

class VariableNode(Node):
    def __init__(self, var: Token, type: Token):
        self.var: Token = var
        self.type: Token = type 

    def get_value(self) -> int:
        return int(self.var.text)
    
    def __str__(self) -> str:
        return f"VariableNode:  [ type: {self.type}  value: {self.var}  ]"
    

        
class BinaryOp(Node):
    def __init__(self, operator: Token, left_node: Node, right_node: Node):
        self.operator: Token = operator
        self.left_node: Node = left_node
        self.right_node: Node = right_node

    def get_operator(self) -> str:
        return self.operator.text
    
    def get_left_node(self) -> Node:
        return self.left_node
    
    def get_right_node(self) -> Node:
        return self.right_node

    def __str__(self) -> str:
        return f"BinaryOperation: ( \n     left node: {self.left_node} \n       operator: {self.operator} \n        right node: {self.right_node}"

class PrintNode(Node):
    def __init__(self, string: Token):
        super().__init__()
        self.string: Token = string
        
    def get_token_type(self):
        return self.string.token_type.name
    
    def get_token_text(self):
        return self.string.text
    
    def __str__(self) -> str:
        return f" PrintNode: {self.get_token_type()}: {self.string.text}"
    
class ReadNode(Node):
    def __init__(self, variable: Token):
        super().__init__()
        self.string: Token = variable
        
    def get_token_type(self):
        return self.string.token_type.name
    
    def get_token_text(self):
        return self.string.text
    
    def __str__(self) -> str:
        return f" PrintNode: {self.get_token_type()}: {self.string.text}"
    

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