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
PUSH = 0b01000101
POP = 0b01000110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.pc = 0
        self.halted = False
        
        self.bt = {
            MUL: self.op_MUL,
            ADD: self.op_ADD
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
        if op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def op_MUL(self, a, b):
        self.alu("MUL", a, b)
    
    def op_ADD(self, a, b):
        self.alu("ADD", a, b)

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

    def run(self):
        """Run the CPU."""
        while not self.halted:
            # Store the memory address stored in reg[PC] into IR, a local variable
            ir = self.ram_read(self.pc)


            # Store pc+1 and pc+2 into operand_a, and operand_b
            operand_a, operand_b = self.ram_read(self.pc+1), self.ram_read(self.pc+2)

            # perform actions for the specific instruction, if/elif/else
            if ir == PRN:
                print(self.reg[operand_a])
            elif ir == LDI:
                self.reg[operand_a] = operand_b
            elif ir == HLT:
                break
            elif ir == PUSH:
                self.reg[SP] -= 1

                value = self.reg[operand_a]

                stack_addr = self.reg[SP]
                self.ram_write(value, stack_addr)
            elif ir == POP:
                stack_addr = self.reg[SP]
                value = self.ram_read(stack_addr)

                self.reg[operand_a] = value

                self.reg[SP] += 1

            elif ir & 0x20: # if ALU opcode, send to bt
                if ir in self.bt:
                    self.bt[ir](operand_a, operand_b)
                else:
                    print(f"No command found for instruction {bin(ir)} at address {bin(self.pc)}")
            else: print(f"No command found for instruction {bin(ir)} at address {bin(self.pc)}")

            # point PC to the correct next instruction
            if ir & 0x80:
                self.pc += 3
            elif ir & 0x40:
                self.pc += 2
            else: self.pc += 1
            # the opcode should indicate how many bytes an instruction uses. This is in the spec.

