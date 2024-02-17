from __future__ import annotations
from enum import Enum
import re

class TokenEnum(Enum):
    LITTERAL = "LITTERAL"
    INTVAL = "INTVAL"
    TYPE = "TYPE" # int, char , string
    PRINT = "PRINT"
    IF = "IF" # if
    WHILE = "WHILE" # while 
    SIGN = "SIGN" # + - / % *
    LPAREN = "LPAREN" # (
    RPAREN = "RPAREN" # )
    ASSIGN = "ASSIGN" # =
    SEMICOLON = "SEMICOLON" # ;
    LEFTBRACKET = "LEFTBRACKET" # {
    RIGHTBRACKET = "RIGHTBRACKET" # }
    COLON = "COLON" # :
    COMPARATION = "COMPARATION" # != == > <
    
class TokenType:
    def __init__(self, name: TokenEnum, regexp: str) -> None:
        self.regexp: str = regexp
        self.name: TokenEnum = name 
        
    def get_regexp(self) -> str:
        return self.regexp
    
    def __str__(self) -> str:
        return str(self.name)

token_type_list: list[TokenType] = [
    TokenType(TokenEnum.TYPE, "string|int|char"),
    TokenType(TokenEnum.LITTERAL, "[a-z]+"),
    TokenType(TokenEnum.INTVAL, "\d+"),
    TokenType(TokenEnum.PRINT, "print"),
    TokenType(TokenEnum.SIGN, "\\+|\\-|\\*|\\/|\\%"),
    TokenType(TokenEnum.COMPARATION, "!=|==|>|<"),
    TokenType(TokenEnum.ASSIGN, "="),
    TokenType(TokenEnum.SEMICOLON, ";"),
    TokenType(TokenEnum.COLON, ":"),
    TokenType(TokenEnum.LEFTBRACKET , "\{"),
    TokenType(TokenEnum.RIGHTBRACKET , "\}"),
    TokenType(TokenEnum.RPAREN , "\)"),
    TokenType(TokenEnum.LPAREN , "\("),
    TokenType(TokenEnum.IF, "if"),
    TokenType(TokenEnum.WHILE, "while"),
    
    ] 
    
    
    
    

class Token:
    def __init__(self, token_type: TokenType, text: str) -> None:
        self.token_type: TokenType = token_type
        self.text: str = text.strip()
    
    def __str__(self) -> str:
        return f'[{self.token_type}: {self.text}]'

    
class Tokenizer: 
    
    def __init__(self, input: str):
        self.input: str = input

        
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
        for type in token_type_list:
            regexp = type.get_regexp()
            result = re.match(regexp, self.input)
            if result is not None:
                return Token(type, result.group(0))
        return None

tokenizer = Tokenizer("""int i = 3;
                      int j = 4;
                      while (j != 0) {
                          j = j - 1;
                      }
                      if ((i > 0) and (j % 2 == 0)) : {
                          print;
                      }
                      """)



