from inspect import signature
NUM_REGISTERS = 13
NUM_MEM = 1000


class AQAAssemblyInterpreter:
    def __init__(self):
        self.registers = [0] * NUM_REGISTERS
        self.memory = [0] * NUM_MEM
        self.cmp_left = None
        self.cmp_right = None
        self.cur_line_num = 0

    def _get_memory_number(self, mem):
        try:
            mem_num = int(mem)
        except ValueError:
            raise Exception(
                f'Invalid memory address at line {self.cur_line_num + 1}')
        if mem_num >= NUM_MEM:
            raise Exception(
                f'Memory address out of range at line {self.cur_line_num + 1}')
        return mem_num

    def set_memory(self, mem, val):
        mem_num = self._get_memory_number(mem)
        self.memory[mem_num] = val % 256

    def get_memory(self, mem):
        mem_num = self._get_memory_number(mem)
        return self.memory[mem_num]

    def _get_register_number(self, reg):
        if reg[0] != 'R':
            raise Exception(
                f'Invalid register at line {self.cur_line_num + 1}')
        try:
            reg_num = int(reg[1:])
        except ValueError:
            raise Exception(
                f'Invalid register number at line {self.cur_line_num + 1}')
        if reg_num >= NUM_REGISTERS:
            raise Exception(
                f'Register number out of range at line {self.cur_line_num + 1}')
        return reg_num

    def set_register(self, reg, val):
        reg_num = self._get_register_number(reg)
        self.registers[reg_num] = val

    def get_register(self, reg):
        reg_num = self._get_register_number(reg)
        return self.registers[reg_num]

    def get_operand(self, operand):
        if operand[0] == 'R':
            return self.get_register(operand)
        elif operand[0] == '#':
            try:
                res = int(operand[1:])
            except ValueError:
                raise Exception(
                    f'Invalid operand at line {self.cur_line_num + 1}')
            return res

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
        self.set_register(reg, self.get_operand(operand))

    def _cmp(self, reg, operand):
        self.cmp_left = self.get_register(reg)
        self.cmp_right = self.get_operand(operand)

    def _eq(self):
        if self.cmp_left is None or self.cmp_right is None:
            raise Exception(
                f'CMP not called before BEQ at line {self.cur_line_num + 1}')
        return self.cmp_left == self.cmp_right

    def _ne(self):
        if self.cmp_left is None or self.cmp_right is None:
            raise Exception(
                f'CMP not called before BNE at line {self.cur_line_num + 1}')
        return self.cmp_left != self.cmp_right

    def _gt(self):
        if self.cmp_left is None or self.cmp_right is None:
            raise Exception(
                f'CMP not called before BGT at line {self.cur_line_num + 1}')
        return self.cmp_left > self.cmp_right

    def _lt(self):
        if self.cmp_left is None or self.cmp_right is None:
            raise Exception(
                f'CMP not called before BLT at line {self.cur_line_num + 1}')
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
        code_lines = [line.strip() for line in code_lines]
        self.cur_line_num = 0
        branches = {}
        instructions = {
            'LDR': self._ldr,
            'STR': self._str,
            'ADD': self._add,
            'SUB': self._sub,
            'MOV': self._mov,
            'CMP': self._cmp,
            'AND': self._and,
            'ORR': self._orr,
            'EOR': self._eor,
            'MVN': self._mvn,
            'LSL': self._lsl,
            'LSR': self._lsr,
            'B': None,
            'BEQ': None,
            'BNE': None,
            'BGT': None,
            'BLT': None,
            'HALT': None
        }
        for line_num, line in enumerate(code_lines):
            if line.endswith(':'):
                branches[line[:-1]] = line_num + 1

        while True:
            if self.cur_line_num >= len(code_lines):
                raise Exception(
                    f'No more instructions after line {self.cur_line_num}')
            cur_line = code_lines[self.cur_line_num]

            if cur_line == '' or ':' in cur_line:
                self.cur_line_num += 1
                continue

            cur_line_split = cur_line.split(' ', maxsplit=1)
            instruction = cur_line_split[0]
            args = [] if len(cur_line_split) == 1 else [arg.strip()
                                                        for arg in cur_line_split[1].split(',')]

            if instruction not in instructions:
                raise Exception(
                    f'Unknown instruction at line {self.cur_line_num + 1}')

            if instruction == 'HALT':
                if len(args) != 0:
                    raise Exception(
                        f'No arguments needed for instruction HALT at line {self.cur_line_num + 1}')
                return
            if instruction[0] == 'B':
                if len(args) != 1:
                    raise Exception(
                        f'Only 1 argument is needed for instruction {instruction} at line {self.cur_line_num + 1}')
                if instruction == 'B' or \
                    (instruction == 'BEQ' and self._eq()) or \
                    (instruction == 'BNE' and self._ne()) or \
                    (instruction == 'BGT' and self._gt()) or \
                        (instruction == 'BLT' and self._lt()):
                    if args[0] not in branches:
                        raise Exception(
                            f'Invalid branch at line {self.cur_line_num + 1}')
                    self.cur_line_num = branches[args[0]]
                    continue
            else:
                func = instructions[instruction]
                num_args = len(signature(func).parameters)
                if len(args) > num_args:
                    raise Exception(
                        f'Too many arguments (expected: {num_args}, you gave: {len(args)}) for instruction {instruction} at line {self.cur_line_num + 1}')
                if len(args) < num_args:
                    raise Exception(
                        f'Too few arguments (expected: {num_args}, you gave: {len(args)}) for instruction {instruction} at line {self.cur_line_num + 1}')
                try:
                    func(*args)
                except Exception as e:
                    raise Exception(
                        f'Error at line {self.cur_line_num + 1}') from e

            self.cur_line_num += 1


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='AQAASM file to run')
    parser.add_argument('-i', '--input', nargs='*', default=['100'], help='A list of memory addresses to input into')
    parser.add_argument('-o', '--output', nargs='*', default=['101'], help='A list of memory addresses to print from')
    args = parser.parse_args()

    aqaai = AQAAssemblyInterpreter()
    with open(args.file, 'r') as f:
        code = f.read()
    for input_address in args.input:
        aqaai.set_memory(input_address, int(input()))
    aqaai.run_code(code)
    for output_address in args.output:
        print(aqaai.get_memory(output_address))
