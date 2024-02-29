from __future__ import annotations

import re
from enum import Enum


class TokenEnum(Enum):
    LITTERAL = "LITTERAL"
    INTVAL = "INTVAL"
    TYPE = "TYPE"  # int, char , string
    STRING = "STRING"
    PRINT = "PRINT"
    READ = "READ"
    IF = "IF"  # if
    ELSE = "ELSE"  # if
    WHILE = "WHILE"  # while
    SIGN = "SIGN"  # + - / % *
    LPAREN = "LPAREN"  # (
    RPAREN = "RPAREN"  # )
    ASSIGN = "ASSIGN"  # =
    SEMICOLON = "SEMICOLON"  # ;
    LEFTBRACKET = "LEFTBRACKET"  # {
    RIGHTBRACKET = "RIGHTBRACKET"  # }
    COLON = "COLON"  # :
    COMPARATION = "COMPARATION"  # != == > <


class TokenType:
    def __init__(self, name: TokenEnum, regexp: str) -> None:
        self.name: TokenEnum = name
        self.regexp: str = regexp

    def get_regexp(self) -> str:
        return self.regexp

    def __str__(self) -> str:
        return str(self.name)


token_type_list: list[TokenType] = [
    TokenType(TokenEnum.PRINT, "print"),
    TokenType(TokenEnum.READ, "read"),
    TokenType(TokenEnum.IF, "if"),
    TokenType(TokenEnum.ELSE, "else"),
    TokenType(TokenEnum.WHILE, "while"),
    TokenType(TokenEnum.TYPE, "string|int|char"),
    TokenType(TokenEnum.INTVAL, r"\d+"),
    TokenType(TokenEnum.SIGN, "\\+|\\-|\\*|\\/|\\%|and"),
    TokenType(TokenEnum.COMPARATION, "!=|==|>=|<=|<|>"),
    TokenType(TokenEnum.ASSIGN, "="),
    TokenType(TokenEnum.SEMICOLON, ";"),
    TokenType(TokenEnum.COLON, ":"),
    TokenType(TokenEnum.STRING, "'.*'"),
    TokenType(TokenEnum.LITTERAL, "[a-z]+"),
    TokenType(TokenEnum.LEFTBRACKET, r"\{"),
    TokenType(TokenEnum.RIGHTBRACKET, r"\}"),
    TokenType(TokenEnum.RPAREN, r"\)"),
    TokenType(TokenEnum.LPAREN, r"\("),
]


class Token:
    def __init__(self, token_type: TokenType, text: str) -> None:
        self.token_type: TokenType = token_type
        self.text: str = text.strip()

    def __str__(self) -> str:
        return f"[{self.token_type}: {self.text}]"


class Tokenizer:
    def __init__(self, input_str: str):
        self.input: str = input_str

    def start_analyze(self) -> list[Token]:
        token_list: list[Token] = list()
        while self.next_token():
            self.input = self.input.strip()
            token = self.next_token()
            token_list.append(token)
            self.input = self.input[len(token.text) :]
        return token_list

    def next_token(self) -> Token | None:
        if len(self.input) == 0:
            return None
        self.input = self.input.strip()
        for type_token in token_type_list:
            regexp = type_token.get_regexp()
            result = re.match(regexp, self.input)
            if result is not None:
                return Token(type_token, result.group(0))
        return None
