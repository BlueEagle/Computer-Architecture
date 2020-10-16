"""CPU functionality."""

import sys

# registers
SP = 7

# opcodes
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
ADD = 0b10100000
CMP = 0b10100111
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.pc = 0
        self.halted = False
        self.fl = 0b00000000
        
        self.bt = {
            MUL: self.op_MUL,
            ADD: self.op_ADD,
            CMP: self.op_CMP
        }

    def load(self, filename='examples/print8.ls8'):
        """Load a program into memory."""

        address = 0

        try:
            with open(filename) as f:
                for line in f:
                    line = line.strip()
                    if line == '' or line[0] =='#':
                        continue

                    try:
                        string_value = line.split('#')[0] # the first item. The data.
                        value = int(string_value, 2)

                    except ValueError:
                        print(f"Not a number: {string_value}")
                        sys.exit(1)

                    self.ram_write(value, address)
                    address += 1
        except FileNotFoundError:
            print(f"File not found: {filename}")
            sys.exit(2)

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            a = self.reg[reg_a]
            b = self.reg[reg_b]
            self.fl = self.fl & 0
            if a < b:
                self.fl = self.fl | 0b00000100
            elif a > b:
                self.fl = self.fl | 0b00000010
            elif a == b:
                self.fl = self.fl | 0b00000001
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def op_ADD(self, a, b):
        self.alu("ADD", a, b)

    def op_MUL(self, a, b):
        self.alu("MUL", a, b)
    
    def op_CMP(self, a, b):
        self.alu("CMP", a, b)

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def prn(self, op_a):
        print(self.reg[op_a])

    def ldi(self, op_a, op_b):
        # print(op_a, op_b)
        self.reg[op_a] = op_b

    def push(self, op_a):
        self.reg[SP] -= 1

        value = self.reg[op_a]

        stack_addr = self.reg[SP]
        self.ram_write(value, stack_addr)

    def pop(self, op_a):
        stack_addr = self.reg[SP]
        value = self.ram_read(stack_addr)

        self.reg[op_a] = value

        self.reg[SP] += 1

    def call(self, op_a):
        next_addr = self.pc + 2 # the next address after the call. This should be the new PC.
        # print(next_addr) # Correct
        self.reg[SP] -= 1
        stack_addr = self.reg[SP]
        self.ram_write(next_addr, stack_addr)

        self.pc = self.reg[op_a]

    def ret(self):
        stack_addr = self.reg[SP]
        self.pc = self.ram_read(stack_addr) # the last value off the stack

        self.reg[SP] += 1

    def jmp(self, op_a):
        new_addr = self.reg[op_a]
        self.pc = new_addr

    def jeq(self, op_a):
        # print("Hello there!")
        if self.fl & 0b00000001:
            self.jmp(op_a)
        else: self.pc += 2
        
    def jne(self, op_a):
        if not self.fl & 1:
            self.jmp(op_a)
        else: self.pc += 2

    def run(self):
        """Run the CPU."""
        while not self.halted:
            # Store the memory address stored in reg[PC] into IR, a local variable
            ir = self.ram_read(self.pc)


            # Store pc+1 and pc+2 into operand_a, and operand_b
            operand_a, operand_b = self.ram_read(self.pc+1), self.ram_read(self.pc+2)

            # perform actions for the specific instruction, if/elif/else
            if ir == PRN:
                self.prn(operand_a)
            elif ir == LDI:
                self.ldi(operand_a,operand_b)
            elif ir == HLT:
                break
            elif ir == PUSH:
                self.push(operand_a)
            elif ir == POP:
                self.pop(operand_a)
            elif ir == CALL:
                self.call(operand_a)
            elif ir == RET:
                self.ret()
            elif ir == JMP:
                self.jmp(operand_a)
            elif ir == JEQ:
                self.jeq(operand_a)
            elif ir == JNE:
                self.jne(operand_a)
            elif ir & 0x20: # if ALU opcode, send to bt
                if ir in self.bt:
                    self.bt[ir](operand_a, operand_b)
                else:
                    print(f"No command found for instruction {bin(ir)} at address {bin(self.pc)}")
            else: print(f"No command found for instruction {bin(ir)} at address {bin(self.pc)}")

            # point PC to the correct next instruction
            if not ir & 0x10: # if the PC is not set by the operation
                if ir & 0x80:
                    self.pc += 3
                elif ir & 0x40:
                    self.pc += 2
                else: self.pc += 1
            # the opcode should indicate how many bytes an instruction uses. This is in the spec.

