import sys
sys.path.append("../csa-lab-3")
from machine.isa import AdModRegAdressInstruction, Instruction, OPCODE, MEMORY_SIZE, REGISTERS, OffsetInstruction, SecondWord, MAX_VALUE, BUFFER_START, BUFFER_END
from lexer import Token, TokenType
from nodes import AssignNode, BinaryOp, InitNode, Node, NumberNode, RootNode, VariableNode, WhileIfNode, PrintNode
from lexer import TokenEnum, Tokenizer
from ast_parser import AstParser


class Translator:
    # todo: должна быть мапа памяти( получаеться надо расписать память), чтобы на уровне компиляции мы знали что откуда тянуть, куда закидывать
    # https://godbolt.org/
    def __init__(self, ast: Node):
        self.ast: Node = ast
        self.commands: list[Instruction] = []
        self.stack_pointer: int = 0
        self.buffer_pointer: int = BUFFER_START
        self.variable_offset: dict[str, int] = {}
        


    
    def operation_with_rax_value(self, operator: str) -> Instruction:
        if (operator == "+"):
            return Instruction(OPCODE.IADDVAL)
        elif (operator == "-"):
            return Instruction(OPCODE.ISUBVAL)
        elif (operator == "*"):
            return Instruction(OPCODE.IMULVAL)
        elif (operator == "/"):
            return Instruction(OPCODE.IDIVVAL)
        elif (operator == "%"):
            return Instruction(OPCODE.IMODVAL)
        elif (operator == "and"):
            return Instruction(OPCODE.IANDVAL)
        
    def operation_with_rax_offset_value(self, operator: str, offset: int) -> Instruction:
        if (operator == "+"):
            return OffsetInstruction(OPCODE.IADD, offset)
        elif (operator == "-"):
            return  OffsetInstruction(OPCODE.ISUB, offset)
        elif (operator == "*"):
            return OffsetInstruction(OPCODE.IMUL, offset)
        elif (operator == "/"):
            return OffsetInstruction(OPCODE.IDIV, offset)
        elif (operator == "%"):
            return OffsetInstruction(OPCODE.IMOD, offset)
        elif (operator == "and"):
            return OffsetInstruction(OPCODE.IAND, offset)
            
    
    def process_binary_op_var_and_num(self, left: Node, right: Node, var_str: str, operator: str) -> None:
        var_node = right if isinstance(right, VariableNode) else left
        number_node = right if isinstance(right, NumberNode) else left
        var_target = var_node.var.text
        var_offset = self.variable_offset.get(var_target)
        mov_to_rax = OffsetInstruction(OPCODE.IMOV, var_offset)
        operation_to_rax = self.operation_with_rax_value(operator)
        second_word = SecondWord(number_node.get_value())
        mov_rax_to_mem = OffsetInstruction(OPCODE.MOVA, self.variable_offset[var_str])
        self.commands += [mov_to_rax, operation_to_rax, second_word, mov_rax_to_mem]
    
    def process_binary_op_var_and_var(self, left: Node, right: Node, var_str: str, operator: str) -> None:
        var_left = left.var.text
        var_left_offset = self.variable_offset.get(var_left)
        var_right = right.var.text
        var_right_offset = self.variable_offset.get(var_right)
        mov_to_rax = OffsetInstruction(OPCODE.IMOV, var_left_offset)
        operation_to_rax = self.operation_with_rax_offset_value(operator, var_right_offset)
        mov_rax_to_mem = OffsetInstruction(OPCODE.MOVA, self.variable_offset[var_str])
        self.commands += [mov_to_rax, operation_to_rax, mov_rax_to_mem]
        
    def process_binary_op_num_and_num(self, left: NumberNode, right: NumberNode, var_str: str,  operator: str) -> None:
        res: int
        if (operator == "+"):
            res = left.get_value() + right.get_value()
        elif (operator == "-"):
            res = left.get_value() - right.get_value()
        elif (operator == "*"):
            res = left.get_value() * right.get_value()
        elif (operator == "/"):
            res = left.get_value() / right.get_value()
        elif (operator == "%"):
            res = left.get_value() % right.get_value()
        elif (operator == "and"):
            res = left.get_value() & right.get_value()
        if res > MAX_VALUE:
            raise ValueError("int overflow")
        movv = OffsetInstruction(OPCODE.MOVV, self.variable_offset[var_str])
        value = SecondWord(res)
        self.commands += [movv, value]
        
    def process_binary_op(self, binary_node: BinaryOp , var_str: str) -> None:
        left = binary_node.get_left_node()
        right = binary_node.get_right_node()
        operator = binary_node.get_operator()
        # if (isinstance(left, BinaryOp)):
        #     self.process_binary_op(left, var_str)
        # if (isinstance(right, BinaryOp)):
        #     self.process_binary_op(right, var_str)
        # recoursive binary op
        if (isinstance(left, NumberNode) and isinstance(right, NumberNode)):
            self.process_binary_op_num_and_num(left, right, var_str, operator)
        elif ((isinstance(left, NumberNode) and isinstance(right, VariableNode))
                    or (isinstance(left, VariableNode) and isinstance(right, NumberNode))):
            self.process_binary_op_var_and_num(left, right, var_str, operator)
        elif (isinstance(left, VariableNode) and isinstance(right, VariableNode)):
            self.process_binary_op_var_and_var(left, right, var_str, operator)
        
       
    def process_number_node(self, node: NumberNode, var_str: str) -> None:
        command = OffsetInstruction(OPCODE.MOVV, self.variable_offset[var_str])
        value = SecondWord(int(node.number.text))
        self.commands += [command, value]
        
    def process_variable_node(self, node: VariableNode, var_str: str) -> None:
        var_name = node.var.text
        mov_to_rax = OffsetInstruction(OPCODE.IMOV, self.variable_offset[var_name])
        mov_rax_to_mem = OffsetInstruction(OPCODE.MOVA, self.variable_offset[var_str])
        self.commands += [mov_to_rax, mov_rax_to_mem]
    
    def process_int_initilization(self, node: InitNode) -> None:
        variable_node = node.variable
        var_str = variable_node.var.text
        right_part = node.right_part
        # определяю offset относительно rbp для переменной
        if (self.variable_offset.get(var_str, None) == None):
            self.variable_offset[var_str] = self.stack_pointer
            self.stack_pointer += 1
        else:
            raise ValueError(f"variable {var_str} already has been initilazed")
        
        if (isinstance(right_part, NumberNode)):
            self.process_number_node(right_part, var_str)
        elif (isinstance(right_part, VariableNode)):
            self.process_variable_node(right_part, var_str)
        elif (isinstance(right_part, BinaryOp)):
            self.process_binary_op(right_part, var_str)

                
    def process_assign(self, node: AssignNode) -> None:
        variable_node = node.variable
        var_str = variable_node.var.text
        right_part = node.right_part
        if (self.variable_offset.get(var_str, None) == None):
            raise ValueError(f"variable {var_str} hasn't been initilazed")
        
        if (isinstance(right_part, NumberNode)):
            self.process_number_node(right_part, var_str)
        elif (isinstance(right_part, VariableNode)):
            self.process_variable_node(right_part, var_str)
        elif (isinstance(right_part, BinaryOp)):
            self.process_binary_op(right_part, var_str)

    def calculate_cmp(self, left_node: Node, right_node: Node) -> list[Instruction]:
        commands: list[Instruction] = []
        if (isinstance(left_node, NumberNode)):
            movva = Instruction(OPCODE.MOVA)
            value = SecondWord(int(left_node.number.text))
            commands += [movva, value]
        elif (isinstance(left_node, VariableNode)):
            imov = OffsetInstruction(OPCODE.IMOV, self.variable_offset[left_node.var.text])
            commands += [imov]
        if (isinstance(right_node, NumberNode)):
            cmpa = Instruction(OPCODE.CMPA)
            value = SecondWord(int(right_node.number.text))
            commands += [cmpa, value]
        elif (isinstance(right_node, VariableNode)):
            icmp = OffsetInstruction(OPCODE.ICMP, self.variable_offset[right_node.var.text])
            commands += [icmp]
        return commands
        



    def process_while_condition(self, prev_len: int , node: BinaryOp) -> list[Instruction]:
        left = node.get_left_node()
        right = node.get_right_node()
        operator = node.get_operator()
        compare_commands_list = self.calculate_cmp(left, right)
        length = len(compare_commands_list) + prev_len
        jump: Instruction
        #неполная длинна епта
        if (operator == "=="):
            jump = OffsetInstruction(OPCODE.JZ, -length)
        elif (operator == "<"):
            jump = OffsetInstruction(OPCODE.JN, -length)
        elif (operator == ">"):
            jump = OffsetInstruction(OPCODE.JP, -length)
        elif (operator == "<="):
            jump = OffsetInstruction(OPCODE.JNE, -length)
        elif (operator == ">="):
            jump = OffsetInstruction(OPCODE.JPE, -length)
        elif (operator == "!="):
            jump = OffsetInstruction(OPCODE.JNEQ, -length)
        compare_commands_list.append(jump)
        return compare_commands_list



    def process_while_statement(self, node: WhileIfNode) -> None:
        condition = node.statement
        saved_state = self.commands.copy()
        self.commands = []
        self.ast_to_list(node)
        commands_len = len(self.commands)
        self.commands += self.process_while_condition(commands_len, condition)
        jmp = OffsetInstruction(OPCODE.JMP, len(self.commands))
        self.commands = saved_state + [jmp] + self.commands
        
    def process_if_condition(self, prev_len: int, node: BinaryOp) -> list[Instruction]:
        left = node.get_left_node()
        right = node.get_right_node()
        operator = node.get_operator()
        compare_commands_list = self.calculate_cmp(left, right)
        length = len(compare_commands_list)
        
        jump: Instruction
        if (operator == "=="):
            jump = OffsetInstruction(OPCODE.JNEQ, length + prev_len + 1)
        elif (operator == "<"):
            jump = OffsetInstruction(OPCODE.JPE, length + prev_len + 1)
        elif (operator == ">"):
            jump = OffsetInstruction(OPCODE.JNZ, length + prev_len + 1)
        elif (operator == "<="):
            jump = OffsetInstruction(OPCODE.JP, length + prev_len + 1)
        elif (operator == ">="):
            jump = OffsetInstruction(OPCODE.JN, length + prev_len + 1)
        elif (operator == "!="):
            jump = OffsetInstruction(OPCODE.JZ, length + prev_len + 1)
        compare_commands_list.append(jump)

        return compare_commands_list
        
    
    def process_if_statement(self, node: WhileIfNode) -> None:
        condition = node.statement
        saved_state = self.commands.copy()
        self.commands = []
        if (node.else_node != None):
            commands_len = 1;
        else:
            commands_len = 0
        self.commands += self.process_if_condition(commands_len, condition)
        self.ast_to_list(node)
        new_state = []
        if (node.else_node != None):
            new_state = self.commands
            self.commands = []
            self.ast_to_list(node.else_node)
            jmp = OffsetInstruction(OPCODE.JMP, len(self.commands))
            self.commands = [jmp] + self.commands
        self.commands = saved_state + new_state + self.commands


    def process_output(self, node: PrintNode):
        type = node.get_token_type()
        commands: list[Instruction] = []
        if (type == TokenEnum.STRING):
            text = node.get_token_text()
            for ch in text:
                if (ch != '\''):
                    commands.append(SecondWord(ord(ch)))
            commands.append(SecondWord(0))
            length = len(commands)
            jump = OffsetInstruction(OPCODE.JMP, length + 1)
            commands = [jump] + commands
            movva = Instruction(OPCODE.MOVVA)
            movva_data = SecondWord(len(self.commands) - len(commands))
            pusha = Instruction(OPCODE.PUSHA)
            imovsp = Instruction(OPCODE.IMOVSP)
            mov_to_buff = AdModRegAdressInstruction(OPCODE.MOV, 9, REGISTERS.RAX, self.buffer_pointer)
            cmpa = Instruction(OPCODE.CMPA)
            cmpa_data = SecondWord(0)
            commands_after_string = [movva, movva_data, pusha, imovsp,
                                     mov_to_buff, cmpa, cmpa_data]
            pop = Instruction(OPCODE.POPA)
            inc = Instruction(OPCODE.INC)
            command_after_jump = [pop, inc, pusha]
            jz = OffsetInstruction(OPCODE.JZ, len(command_after_jump) + 2)
            commands_after_string.append(jz)
            jmp = OffsetInstruction(OPCODE.JMP, -(len(command_after_jump) + len(commands_after_string) - 3))
            command_after_jump.append(jmp)
            commands = commands + commands_after_string + command_after_jump
            self.commands += commands
            
        else:
            pass
        


    def translate_node(self, node: Node):
        if (isinstance(node, WhileIfNode)):
            if (node.token.token_type.name == TokenEnum.IF):
                self.process_if_statement(node)
            else:
                self.process_while_statement(node)
        elif (isinstance(node, InitNode)):
            self.process_int_initilization(node)
        elif (isinstance(node, AssignNode)):
            self.process_assign(node)
        elif (isinstance(node, PrintNode)):
            self.process_output(node)
        

        
    

    def ast_to_list(self, node: Node) -> None:
        current_node = node
        if (isinstance(current_node, RootNode)):
            children = current_node.childrens
            for node in children:
                self.translate_node(node)
                

# nudes = InitNode(VariableNode(Token(TokenType(TokenEnum.LITTERAL, ""), "i"), Token(TokenType(TokenEnum.TYPE, ""), "int")),BinaryOp(Token(TokenType(None, ""), "*"),NumberNode(Token(TokenType(None, ""), "127")), NumberNode(Token(TokenType(None, ""), "128"))))
# nudes1 = InitNode(VariableNode(Token(TokenType(TokenEnum.LITTERAL, ""), "j"), Token(TokenType(TokenEnum.TYPE, ""), "int")),BinaryOp(Token(TokenType(None, ""), "+"),NumberNode(Token(TokenType(None, ""), "127")), NumberNode(Token(TokenType(None, ""), "128"))))
                
tokenizer = Tokenizer("""
                      
                      """)
result = tokenizer.start_analyze()
j = 0
parser = AstParser(result)
parsed = parser.parse_code()
trans = Translator(parsed)
trans.ast_to_list(trans.ast)
for i in trans.commands:
    print(f"adress => {j} : {i} : {i.get_bytes_value()}")
    j+=1

def main(source, target):
    with open(source, encoding="UTF-8") as fr:
        code = fr.read()
    tokens = Tokenizer(code).start_analyze()
    ast_tree = AstParser(tokens).parse_code()
    instr_list = Translator(ast_tree)
    instr_list.ast_to_list(instr_list.ast)
    instr_list = instr_list.commands
    with open(target, "br+") as fw:
        for instruction in instr_list:
            print(instruction)
            fw.write(instruction.get_bytes_value())
        
        

if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    _, source, target = sys.argv
    main(source, target)