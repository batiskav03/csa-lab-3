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
Машинное слово - non-fixed 16 - 32 бит  : 
|1---   |2---   |3---  |4---  |5---  |6---  |7---  |8---  |  
|    opcode     | regs | regs |
                |    offset   |
                | regs |       address      |
                |       address      |
                | regs |             value                |
```
-Система команд:
| mnemonic | opcode (HEX) | definition |
| ------  | ------------  | ----------- | 
| NOP | 00 | nop |
| MOV | 01 | move |
| ADD | 02 | summary |
| SUB | 03 | subtract |
| MUL | 04 | multiply |
| DIV | 05 | divide |
| MOD | 06 | mod_div |
| AND | 07 | logic and |
| OR | 08 | logic or |
| NOT | 09 | logic not |
| CMP | 0A | compare | 
| JMP | 0B | jump | 
| JZ | 0C | jump zero |
| JN | 0D | jump negative |
| JP | 0E | jump positive |
| HLT| 0F | halt |
| IMOV | 10 | move value by <adress> = <rbp> - <value_offset> to rax|
| IADD | 20 | summary rax with value by <adress> |
| ISUB | 30 | subtract rax with value by <adress>|
| IMUL | 40 | multiply rax with value by <adress>|
| IDIV| 50 | divide rax with value by <adress> |
| MOVV | 11 | move value to <adress> = <rbp> - <var_offset> |
| MOVA | 12 | move value to <adress> = <rbp> - <var_offset> |


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
