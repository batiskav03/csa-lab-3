from __future__ import annotations

from translator.lexer import Token, TokenEnum, TokenType
from translator.nodes import (
    AssignNode,
    BinaryOp,
    ElseNode,
    InitNode,
    Node,
    NumberNode,
    PrintNode,
    ReadNode,
    RootNode,
    VariableNode,
    WhileIfNode,
)


class AstParser:
    def __init__(self, tokens: list[Token]):
        self.tokens: list[Token] = tokens
        self.init_variables = {}
        self.pos = 0

    def match(self, token_type: TokenType) -> Token | None:
        if self.pos < len(self.tokens):
            current_token = self.tokens[self.pos]
            if token_type == current_token.token_type.name:
                self.pos += 1
                return current_token
        return None

    def require(self, token_type: TokenType) -> Token:
        token = self.match(token_type)
        if not token:
            raise ValueError()
        return token

    def parse_init(self, type_token: Token) -> Node:
        variable = self.match(TokenEnum.LITTERAL)
        if variable is not None and self.init_variables.get(variable.text, None) is None:
            self.init_variables[variable.text] = type_token
            return VariableNode(variable, type_token)
        raise ValueError()

    def parse_variable_or_number(self) -> Node:
        variable = self.match(TokenEnum.LITTERAL)
        if variable is not None:
            return VariableNode(variable, self.init_variables[variable.text])
        number = self.match(TokenEnum.INTVAL)
        if number is not None:
            return NumberNode(number)
        raise ValueError()

    def parse_parentheses(self) -> Node:
        if self.match(TokenEnum.LPAREN) is not None:
            node = self.parse_operation()
            self.require(TokenEnum.RPAREN)

            return node

        return self.parse_variable_or_number()

    def parse_operation(self) -> Node:
        left_node = self.parse_parentheses()
        operator = self.match(TokenEnum.SIGN)
        if operator is None:
            operator = self.match(TokenEnum.COMPARATION)
        while operator is not None:
            right_node = self.parse_parentheses()
            left_node = BinaryOp(operator, left_node, right_node)
            operator = self.match(TokenEnum.SIGN)

        return left_node

    def parse_type_token(self, type_token: Token) -> Node:
        variable_node = self.parse_init(type_token)
        assign_operator = self.match(TokenEnum.ASSIGN)
        if assign_operator is not None:
            right_operation_node = self.parse_operation()
            binary_node = InitNode(variable_node, right_operation_node)
            self.require(TokenEnum.SEMICOLON)
            return binary_node
        raise ValueError()

    def parse_litteral_token(self) -> Node:
        self.pos -= 1
        variable_node = self.parse_variable_or_number()
        assign_operator = self.match(TokenEnum.ASSIGN)
        if assign_operator is not None:
            right_operation_node = self.parse_operation()
            binary_node = AssignNode(variable_node, right_operation_node)
            self.require(TokenEnum.SEMICOLON)
            return binary_node
        raise ValueError()

    def parse_if_statement_token(self, if_statement_token: Token):
        statement = self.parse_operation()
        self.require(TokenEnum.LEFTBRACKET)
        if_node = WhileIfNode(statement, if_statement_token)
        while self.match(TokenEnum.RIGHTBRACKET) is None:
            code_string_node = self.parse_statement()
            if_node.childrens.append(code_string_node)
        else_statmenet = self.match(TokenEnum.ELSE)
        if else_statmenet is not None:
            self.require(TokenEnum.LEFTBRACKET)
            else_node = ElseNode()
            while self.match(TokenEnum.RIGHTBRACKET) is None:
                code_string_node = self.parse_statement()
                else_node.childrens.append(code_string_node)
            if_node.set_else_block(else_node)
        return if_node

    def parse_while_statement_token(self, while_statement_node: Token) -> Node:
        statement = self.parse_operation()
        self.require(TokenEnum.LEFTBRACKET)
        while_node = WhileIfNode(statement, while_statement_node)
        while self.match(TokenEnum.RIGHTBRACKET) is None:
            code_string_node = self.parse_statement()
            while_node.childrens.append(code_string_node)
        return while_node

    def parse_print_statement_token(self) -> Node:
        self.require(TokenEnum.LPAREN)
        string = self.match(TokenEnum.STRING)
        print_node: PrintNode
        if string is not None:
            print_node = PrintNode(string)
        else:
            var_token = self.match(TokenEnum.LITTERAL)
            print_node = PrintNode(var_token, self.init_variables[var_token.text])
        self.require(TokenEnum.RPAREN)
        self.require(TokenEnum.SEMICOLON)
        return print_node

    def parse_statement(self) -> Node:
        type_token = self.match(TokenEnum.TYPE)  # встретилось инициализирование
        if type_token is not None:
            return self.parse_type_token(type_token)
        litteral_token = self.match(TokenEnum.LITTERAL)
        if litteral_token is not None:  # встретилось присваивание
            return self.parse_litteral_token()
        if_statement_token = self.match(TokenEnum.IF)
        if if_statement_token is not None:
            return self.parse_if_statement_token(if_statement_token)
        while_statement_node = self.match(TokenEnum.WHILE)
        if while_statement_node is not None:
            return self.parse_while_statement_token(while_statement_node)
        print_statement = self.match(TokenEnum.PRINT)
        if print_statement is not None:
            return self.parse_print_statement_token()
        read_statement = self.match(TokenEnum.READ)
        if read_statement is not None:
            self.require(TokenEnum.LPAREN)
            read_node = ReadNode(self.match(TokenEnum.LITTERAL))
            self.require(TokenEnum.RPAREN)
            self.require(TokenEnum.SEMICOLON)
            return read_node
        return None

    def parse_code(self) -> Node:
        root = RootNode()
        while self.pos < len(self.tokens):
            code_string_node = self.parse_statement()
            root.childrens.append(code_string_node)
        return root
