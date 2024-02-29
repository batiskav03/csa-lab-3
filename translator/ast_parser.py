from __future__ import annotations
from lexer import Tokenizer, TokenType, Token, TokenEnum, token_type_list
from nodes import AssignNode, InitNode, Node,  NumberNode, VariableNode, BinaryOp, WhileIfNode, RootNode, ElseNode, PrintNode,ReadNode


class AstParser:

    def __init__(self, tokens: list[Token]):
        self.tokens: list[Token] = tokens
        self.init_variables = {}
        self.pos = 0


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
    
    def parse_init(self, type: Token) -> Node:
        variable = self.match(TokenEnum.LITTERAL)
        if (variable != None and self.init_variables.get(variable.text, None) == None):
            self.init_variables[variable.text] = type
            return VariableNode(variable, type)
        raise ValueError(f"Missing variable on position {self.pos} or this variable already exists.")
        
        
    def parse_variable_or_number(self) -> Node:
        variable = self.match(TokenEnum.LITTERAL)
        if (variable != None):
            return VariableNode(variable, self.init_variables[variable.text])
        number = self.match(TokenEnum.INTVAL)
        if (number != None):
            return NumberNode(number)
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
        if (operator == None):
            operator = self.match(TokenEnum.COMPARATION)
        while (operator != None):
            right_node = self.parse_parentheses()
            left_node = BinaryOp(operator, left_node, right_node)
            operator = self.match(TokenEnum.SIGN)

        return left_node
    
    
    
    def parse_statement(self) -> Node:
        type_token = self.match(TokenEnum.TYPE) # встретилось инициализирование  
        if (type_token != None):
            variable_node = self.parse_init(type_token)
            assign_operator = self.match(TokenEnum.ASSIGN)
            if (assign_operator != None):
                right_operation_node = self.parse_operation()
                binary_node = InitNode(variable_node, right_operation_node)
                self.require(TokenEnum.SEMICOLON)
                return binary_node
            raise ValueError(f"After variable require assign operator on position {self.pos}")
        litteral_token = self.match(TokenEnum.LITTERAL)
        if (litteral_token != None): # встретилось присваивание 
            self.pos -= 1
            variable_node = self.parse_variable_or_number()
            assign_operator = self.match(TokenEnum.ASSIGN)
            if (assign_operator != None):
                right_operation_node = self.parse_operation()
                binary_node = AssignNode(variable_node, right_operation_node)
                self.require(TokenEnum.SEMICOLON)
                return binary_node
            raise ValueError(f'After variable require assign operator on position {self.pos}')
        if_statement_token = self.match(TokenEnum.IF)
        if (if_statement_token != None):
            statement = self.parse_operation()
            self.require(TokenEnum.LEFTBRACKET)
            if_node = WhileIfNode(statement, if_statement_token)
            while (self.match(TokenEnum.RIGHTBRACKET) == None):
                code_string_node = self.parse_statement()
                if_node.childrens.append(code_string_node)
            else_statmenet = self.match(TokenEnum.ELSE)
            if (else_statmenet != None):
                self.require(TokenEnum.LEFTBRACKET)
                else_node = ElseNode()
                while (self.match(TokenEnum.RIGHTBRACKET) == None):
                    code_string_node = self.parse_statement()
                    else_node.childrens.append(code_string_node)
                if_node.set_else_block(else_node)
            return if_node
        while_statement_node = self.match(TokenEnum.WHILE)
        if (while_statement_node != None):
            statement = self.parse_operation()
            self.require(TokenEnum.LEFTBRACKET)
            while_node = WhileIfNode(statement, while_statement_node)
            while (self.match(TokenEnum.RIGHTBRACKET) == None):
                code_string_node = self.parse_statement()
                while_node.childrens.append(code_string_node)
            return while_node
        print_statement = self.match(TokenEnum.PRINT)
        if (print_statement != None):
            self.require(TokenEnum.LPAREN)
            string = self.match(TokenEnum.STRING)
            print_node: PrintNode
            if (string != None):
                print_node = PrintNode(string)
            else:
                print_node = PrintNode(self.match(TokenEnum.LITTERAL))
            self.require(TokenEnum.RPAREN)
            self.require(TokenEnum.SEMICOLON)
            return print_node
        read_statement = self.match(TokenEnum.READ)
        if (read_statement != None):
            self.require(TokenEnum.LPAREN)
            read_node = ReadNode(self.match(TokenEnum.LITTERAL))
            self.require(TokenEnum.RPAREN)
            self.require(TokenEnum.SEMICOLON)
            return read_node
        
    def parse_code(self) -> Node:
        root = RootNode()
        while (self.pos < len(self.tokens)):
            code_string_node = self.parse_statement()
            root.childrens.append(code_string_node)
        return root



