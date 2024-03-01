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
| prob2                   |                                                                                      |


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
             "(" <op> ")"  |
asign ::= <type> <litteral> "="  <op>  ";"         
type ::= "int" | "char"  
if_statement ::= "if" "(" <op> ")" "{"  <statements> { "else" ":" '{' <statements> '}' } "}"
loop_statement ::= "while" "(" <op> ")" ":" "{" <statements> "}"
number ::= [0-9]*
litteral ::= [a-bA-B][a-bA-B0-9]*
```
- Типизация: статическая
    int - целочисленный тип данных. Может принимать любое значение помещающееся в 4 байта.
    char - символный тип данных. Может принимать любое значение помещающееся в 4 байта.
    Строки храняться в памяти машины, как последовательный набор символов.
- Область видимости: Глобальная
- Все арифметические и логические операции левоассоциативные
- Переменные храняться в области памяти variables (см. Структура Памяти). Регеистр rbx хранит указатель на эту область памяти.

##Структура Памяти


```
- Структура памяти:
 Registers
+--------------------------------------------------------------------------------------------+
| rax - регистр общего назначения                                                            |
+--------------------------------------------------------------------------------------------+
| rbx - регситр общего назначения                                                            |
+--------------------------------------------------------------------------------------------+
| rdx - регистр общего назначения                                                            |
+--------------------------------------------------------------------------------------------+
| rcx - регситр общего назначения                                                            |
+--------------------------------------------------------------------------------------------+
| rsp - регистр общего назначения                                                            |
+--------------------------------------------------------------------------------------------+
| rbx - регситр общего назначения                                                            |
+--------------------------------------------------------------------------------------------+

            Instruction & Data memory
+-----------------------------------------------+
|    0    :  programm start                     |  <-- IP, SP
|        ...                                    |
| 40000   :  data buffer                        |
|        ...                                    |
| 44999   :  data buffer                        |
|        ...                                    |
| 45000   :  variables                          | <-- %rbx ↓
|        ...                                    |               
| 59999   :  variables                          |
|        ...                                    |
| 65536   :^   stack                            |
+-----------------------------------------------+
```
- Память данных и команд общая
- 6 регистров общего назначения, а так же регистр  __DR__, в который считываются данные из памяти или записываются, и регистр __AR__, который хранит адрес ячейки, к которой идет обращение.
- Размер всех регистров - 32 бита, за исключением __AR__, размер которого равен 16 бит.

Память разделена на 4 условных блока:
1. Блок, куда загружается программа _(programm start)_
2. Блок, куда мапятся устройства ввода/вывода _(data buffer)_
3. Блок, где храняться переменные _(variables)_. 
4. Стек _(stack)_

``` 
Машинное слово - non-fixed 32 - 64 бит  : 
|1---   |2---   |3---  |4---  |5---  |6---  |7---  |8--- | opt:|9------- | 10------- | 11------- | 12------- | 
|    opcode     | cntrl| reg  |           adress         |     |                     value                   |
                | cntrl| reg  |           offset         |     |                     value                   |
                | cntrl| reg  | reg  |
                
```
- Структура машинного слова имеет переменную длину. 
- Длинна машинного слова определяется либо по _opcode_, либо по _управляющим битам (cntrl)_.
- Инструкции с длинной машинного слова 64 бита используются для прямой загрузки операнда. 
##### Вариации битов управления:

- control bits 0010 - относительная адрессация 
- control bits 0100 - косвенная адрессация 
- control bits mov 1001 - reg -> adress 
- control bits mov 1100 - reg <- immid.value
- control bits mov 0001 - reg <- adress

## Система команд
True Complex Instruction Set:

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
| IMOV | 10 | move value by adress = rbp - value_offset to rax|
| MOVV | 11 | move absolute value to adress = rbp - var_offset |
| MOVA | 12 | move rax to adress = rbp - var_offset |
| MOVVA | 13 | move absolute value to rax |
| PUSHA | 14 | push rax value by rsp, rsp = rsp - 1 |
| POPA | 15 | pop value on rsp to rax, rsp = rsp + 1 |
| PEEKA | 16 | peek value from rsp to rax without changing rsp|
| ICMP | 1B | cmp value by adress = (rbp - value_offset) with rax|
| JNEQ | 1C | jump not equal|
| JNE | 1D | jump negative or equal|
| JPE | 1E | jump positive or equal |
| JNZ | 1F | jump not zero |
| CMPA | 2B | cmp rax with absolute value |
| IADD | 20 | summary rax with value by adress = rbp - value_offset|
| IADDVAL | 21 | summary rax with value  | 
| ISUB | 30 | subtract rax with value by adress = rbp - value_offset|
| ISUBVAL | 31 | substact rax with value  |
| IMOVSP | 32 | move operand from adress = rsp to rax |
| IMUL | 40 | multiply rax with value by adress = rbp - value_offset|
| IMULVAL | 41 | multiply rax with value  |
| IDIV| 50 | divide rax with value by adress = rbp - value_offset|
| IDIVVAL | 51 | divide rax with value  |
| IMOD | 60 | mod rax with value by adress = rbp - value_offset|
| IMODVAL | 61 | mod rax with value  |
| IAND | 70 | AND rax with value by adress = rbp - value_offset|
| IANDVAL | 71 | AND rax with value  |
| INC | 80 | inc rax | 

- Особенности процессора:
    - Машинное слово 32 - 64 бита.
    - Определение размера машинного слова происходит на цикле декодирования команды.
    - Работа с устройствами ввода вывода просходит через память.
    - Память процессора хранит команды в бинарном виде.
- Кодирование инструкций: 
  - Инструкции транслируются в бинарный файл в соответсвующем виде.
   Пример сгенерированного бинарого файла, открытого в hex editor-e:
  ![hex](./img/hex_editor.png)
   Пример откладочного файла:
  ```
    0 - 01c10000 - mov %rbx <- next 4 byte
    1 - 0000afc8 - 45000 
    2 - 11000000 - movv (rbp - 0) <- next 4 bytes
    3 - 00000000 - 0 
    4 - 01109c40 - mov %rax <- (40000)
    5 - 12000000 - mova %rax -> (rbp - 0)
    6 - 0b200008 - jmp %pc + 8
    7 - 10000000 - imov %rax <- (rbp - 0)
    8 - 01909c40 - mov %rax -> 40000
    9 - 13000000 - movva %rax <- next 4 bytes
    10 - 00000000 - 0 
    11 - 01909c40 - mov %rax -> 40000
    12 - 01109c40 - mov %rax <- (40000)
    13 - 12000000 - mova %rax -> (rbp - 0)
    14 - 10000000 - imov %rax <- (rbp - 0)
    15 - 2b000000 - cmpa
    16 - 00000000 - 0 
    17 - 1c20fff6 - jneq %pc + -10
    18 - 0f000000 - hlt
    ```






## Модель процессора
**DataPath**
![DataPath](./img/data_path.jpeg)
**ControlUnit**
![ControlUnit](./img/control_unit.jpeg)
