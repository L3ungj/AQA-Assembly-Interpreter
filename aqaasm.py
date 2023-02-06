NUM_REGISTERS = 13
NUM_MEM = 1000


class Assembly:
    def __init__(self):
        self.registers = [0] * NUM_REGISTERS
        self.memory = [0] * NUM_MEM
        self.cmp_left = None
        self.cmp_right = None

    def set_memory(self, mem, val):
        if mem >= NUM_MEM:
            raise Exception('Memory address invalid')
        self.memory[mem] = val

    def get_memory(self, mem):
        if mem >= NUM_MEM:
            raise Exception('Memory address invalid')
        return self.memory[mem]

    def set_register(self, reg, val):
        if reg >= NUM_MEM:
            raise Exception('Register number invalid')
        self.registers[reg] = val

    def get_register(self, reg):
        if reg >= NUM_MEM:
            raise Exception('Register number invalid')
        return self.registers[reg]

    def get_operand(self, operand):
        if operand[0] == 'R':
            return self.get_register(operand)
        elif operand[0] == '#':
            return int(operand[1:])

    def _ldr(self, reg, mem):
        self.set_register(reg, self.get_memory(mem))

    def _str(self, reg, mem):
        self.set_memory(mem, self.get_register(reg))

    def _add(self, reg, reg2, operand):
        res = (self.get_register(reg2) + self.get_operand(operand)) % 256
        self.set_register(reg, res)

    def _sub(self, reg, reg2, operand):
        res = (self.get_register(reg2) - self.get_operand(operand) + 256) % 256
        self.set_register(reg, res)

    def _mov(self, reg, operand):
        self.set_register(reg, operand)

    def _cmp(self, reg, operand):
        self.cmp_left = self.get_register(reg)
        self.cmp_right = self.get_operand(operand)

    def _eq(self):  # ! raise
        return self.cmp_left == self.cmp_right

    def _ne(self):
        return self.cmp_left != self.cmp_right

    def _gt(self):
        return self.cmp_left > self.cmp_right

    def _lt(self):
        return self.cmp_left < self.cmp_right

    def _and(self, reg, reg2, operand):
        res = self.get_register(reg2) & self.get_operand(operand)
        self.set_register(reg, res)

    def _orr(self, reg, reg2, operand):
        res = self.get_register(reg2) | self.get_operand(operand)
        self.set_register(reg, res)

    def _eor(self, reg, reg2, operand):
        res = self.get_register(reg2) ^ self.get_operand(operand)
        self.set_register(reg, res)

    def _mvn(self, reg, operand):
        res = (~self.get_operand(operand)) % 256
        self.set_register(reg, res)

    def _lsl(self, reg, reg2, operand):
        res = (self.get_register(reg2) << self.get_operand(operand)) % 256
        self.set_register(reg, res)

    def _lsr(self, reg, reg2, operand):
        res = self.get_register(reg2) >> self.get_operand(operand)
        self.set_register(reg, res)

    def run_code(self, code: str):
        code_lines = code.splitlines()
        cur_line_num = 0
        branches = {}
        instructions = {
            'LDR': self._ldr,

        }

        def branch(label: str):
            pass
        while True:
            cur_line = code_lines[cur_line_num]
            instruction, args_raw = cur_line.split(' ', maxsplit=1)
            
            if instruction not in instructions:
                raise Exception('Unknown instruction')
                
            if instruction == 'HALT':
                return
            if instruction[0] == 'B':
                if instruction == 'B' or \
                    (instruction == 'BEQ' and self._eq()) or \
                    (instruction == 'BNE' and self._ne()) or \
                    (instruction == 'BGT' and self._gt()) or \
                        (instruction == 'BLT' and self._lt()):
                    branch(args_raw)
            else:
                func = instructions[instruction]
                args = args_raw.split(',')
                args = [arg.strip() for arg in args]

