# csa-lab3

## Вариант 
| Особенность             |                                  |
|-------------------------|----------------------------------|
| alg                     | синтаксис языка должен напоминать java/javascript/lua.                               |
| cisc                    | Система команд должна содержать сложные инструкции, переменная длина машинного слова |
| neum                    | фон Неймановская архитектура.                                                        |
| hw                      | CU Реализуется как часть модели.                                                     |
| instr                   | процессор необходимо моделировать с точностью до каждой инструкции.                  |
| binary                  | бинарное представление.                                                              |
| stream                  | Ввод-вывод осуществляется как поток токенов.                                         |
| mem                     | memory-mapped                                                                        |
| cstr                    | Null-terminated (C string)                                                           |
| prob5                   |                                                                                      |


## Язык программирования 
- Грамматика:
``` ebnf
program ::= "{" <statements> "}"
statements ::= <statement> | <statement> <statements>
statement ::=  (<asign> | <if_statement> | <loop_statement> | <op>) ";"
op ::= <litteral> | <number> |
             <op> "+" <op> | 
             <op> "-" <op> |
             <op> "/" <op> |
             <op> "%" <op> |
             <op> "*" <op> |
             <op> "==" <op>|
             <op> "or" <op>|
             <op> "and" <op>|
             <op> "!=" <op>|
             "!"<op>       |
             <op>"++"      |
             <op>"--"      |
             "(" <op> ")"  |
asign ::= <type> <litteral> "="  <op>  ";"          #TODO: char and string
type ::= "int" | "char" | "string" 
if_statement ::= "if" <op> ":" "{"  <statements> { "else" ":" '{' <statements> '}' } "}"
loop_statement ::= "while" <op> ":" "{" <statements> "}"
number ::= [0-9]*
litteral ::= [a-bA-B][a-bA-B0-9]*
```
```
Машинное слово - non-fixed от 2 до 4 байт: 
|1---   |2---   |3---  |4---  |     |5---  |6---  |7---  |8---  |
|opcode |ad.mode| regs | val  | 
                       | regs |     |          address          |
                |short address|     
                                    |           value           |
```
-Система команд:
| mnemonic | opcode (HEX) | definition |
| ------  | ------------  | ----------- | 
| NOP | 0 | nop |
| MOV | 1 | move |
| ADD | 2 | summary |
| SUB | 3 | subtract |
| MUL | 4 | multiply |
| DIV | 5 | divide |
| MOD | 6 | mod_div |
| AND | 7 | logic and |
| OR | 8 | logic or |
| NOT | 9 | logic not |
| CMP | A | compare | 
| JMP | B | jump | 
| JZ | C | jump zero |
| JN | D | jump negative |
| JP | E | jump positive |
| HLT| F | halt |


- Типизация:
    int - целочисленный тип данных. Может принимать любое значение помещающееся в 1 машинное слово.
    char - символный тип данных. Может принимать любое значение помещающееся в 1 машинное слово.
    string - todo.
- Область видимости:
    Область видимости каждой переменной - глобальная.
- Операции:
```
    "+" : (int, int) -> int | (char, char) -> char;  
    "-": (int, int) -> int | (char, char) -> char;
    "*": (int, int) -> int;
    "/": (int, int) -> int;
    "%": (int, int) -> int;
    "++": (int) -> int | (char) -> char;
    "--": (int) -> int | (char) -> char;
    "!": (int) -> int  | (char) -> char;
    "==": (int, int) -> int | (char, char) -> int;
```
- Структура памяти:
 Registers
+------------------------------------+
| A0 - аккумулятор                   | #todo
+------------------------------------+
| ...                                |
+------------------------------------+
| A15 - аккумулятор                  |
+------------------------------------+
| CR - регистр инструкции            |
+------------------------------------+
| DR - регистр данных                |
+------------------------------------+
| IP - счётчик команд                |
+------------------------------------+
| SP - указатель стека               |
+------------------------------------+
| AR - адрес записи в память         |
+------------------------------------+
            Instruction & Data memory
+-----------------------------------------------+
|    0    :  programm start                     |  <-- IP, SP
|        ...                                    |
| start   :  buffer start adr                   |
|        ...                                    |
| end     :  buffer end adr                     |
|        ...                                    |
+-----------------------------------------------+
