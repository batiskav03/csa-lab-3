from lexer import Tokenizer, TokenType, Token, TokenEnum, token_type_list
from nodes import Node,  NumberNode, VariableNode, BinaryOp

class AstParser:

    def __init__(self, tokens: list[Token]):
        self.tokens: list[Token] = tokens
        self.pos = 0
        self.scope = {}


    def match(self, token_type: TokenType) -> Token | None:
        if (self.pos < len(self.tokens)):
            current_token = self.tokens[self.pos]
            if (token_type == current_token.token_type.name):
                self.pos += 1
                return current_token
        return None

    

    def require(self, token_type: TokenType) -> Token:
        token = self.match(token_type)
        if (not token):
            raise ValueError(f'on position {self.pos} required ${token_type.name}')
        return token
    
    def parse_variable_or_number(self) -> Node:
        number = self.match(TokenEnum.INTVAL)
        if (number != None):
            print(number)
            return NumberNode(Token)
        
        variable = self.match(TokenEnum.LITTERAL)
        if (variable != None):
            return VariableNode(variable)
        
        raise ValueError(f'Required number or variable on position {self.pos}')
    
    def parse_parentheses(self) -> Node:
        if (self.match(TokenEnum.LPAREN) != None):
            node = self.parse_operation()
            self.require(TokenEnum.RPAREN)

            return node
        else:
            return self.parse_variable_or_number()
    
    def parse_operation(self) -> Node:
        left_node = self.parse_parentheses()
        operator = self.match(TokenEnum.SIGN)
        while (operator != None):
            right_node = self.parse_parentheses()
            left_node = BinaryOp(operator, left_node, right_node)
            operator = self.match(TokenEnum.SIGN)

        return left_node
    
    def parse_statement(self) -> Node:
        type_token = self.match(TokenEnum.TYPE) # встретилось инициализирование  
        if (type_token != None):
            variable_node = self.parse_variable_or_number()
            assign_operator = self.match(TokenEnum.ASSIGN)
            if (assign_operator != None):
                right_operation_node = self.parse_operation()
                binary_node = BinaryOp(assign_operator, variable_node, right_operation_node)
                return binary_node
            raise ValueError(f'After variable require assign operator on position {self.pos}')
        litteral_token = self.match(TokenEnum.LITTERAL)
        if (litteral_token != None): # встретилось присваивание 
            self.pos -= 1
            variable_node = self.parse_variable_or_number()
            assign_operator = self.match(TokenEnum.ASSIGN)
            if (assign_operator != None):
                right_operation_node = self.parse_operation()
                binary_node = BinaryOp(assign_operator, variable_node, right_operation_node)
                return binary_node
            raise ValueError(f'After variable require assign operator on position {self.pos}')
        statement_token = self.match(TokenEnum.IF)
        if (statement_token != None):
            statement = self.parse_operation()


    def parse_code(self) -> Node:
        root = Node()
        while (self.pos < len(self.tokens)):
            code_string_node = self.parse_statement()
            self.require(TokenEnum.SEMICOLON)
            root.childrens.append(code_string_node)
        return root


tokenizer = Tokenizer("""int i = 3 + 4;
                      i = 32;
                      """)
result = tokenizer.start_analyze()
parser = AstParser(result)
print(parser.parse_code())
