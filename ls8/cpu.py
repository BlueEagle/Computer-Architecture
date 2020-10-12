"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b11000010

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.pc = 0
        self.halted = False

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

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
            if ir == LDI:
                self.reg[operand_a] = operand_b
                print(f"LDI {operand_a} {operand_b}")
            elif ir == HLT:
                break
            else: print(f"No command found for instruction {bin(ir)} at address {bin(self.pc)}")

            # point PC to the correct next instruction
            if ir & 0b10000000:
                self.pc += 3
            elif ir & 0b01000000:
                self.pc += 2
            else: self.pc += 1
            # the opcode should indicate how many bytes an instruction uses. This is in the spec.

            # Decode the instruction at PC
