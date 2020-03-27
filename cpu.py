"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Create memory (256 bits)
        self.ram = [0] * 256

        # 8 general-purpose 8-bit numeric registers R0-R7
        # R5 is reserved as the interrupt mask (IM)
        # An internal switch setting that controls whether an interrupt can be processed or not. The mask is a bit that is turned on and off by the program.
        # R6 is reserved as the interrupt status (IS)
        # R7 is reserved as the stack pointer (SP)

        self.reg = [0] * 8

        self.SP = 7

        self.reg[self.SP] = 0xf4

        # Program Counter (PC)
        # Keep track of where you are on the memory stack
        self.pc = 0

        # Flag register (FL)
        # Holds the current flags status
        # These flags can change based on the operands given to the CMP opcode
        '''
        FL bits: 00000LGE
        L Less-than: during a CMP, set to 1 if registerA is less than registerB, zero otherwise.
        G Greater-than: during a CMP, set to 1 if registerA is greater than registerB, zero otherwise.
        E Equal: during a CMP, set to 1 if registerA is equal to registerB, zero otherwise.
        '''
        self.fl = 0b00000000

        # Used for generic functions for the CPU
        def LDI(operand_a, operand_b):
            self.reg[operand_a] = operand_b
            self.pc += 3

        def PRN(operand_a, operand_b):
            print(f'{self.reg[operand_a]}')
            self.pc += 2

        def PUSH(operand_a, operand_b):
            self.reg[self.SP] -= 1
            reg_num = operand_a
            reg_val = self.reg[reg_num]
            self.ram[self.reg[self.SP]] = reg_val
            self.pc += 2

        def POP(operand_a, operand_b):
            val = self.ram[self.reg[self.SP]]
            reg_num = operand_a
            self.reg[reg_num] = val
            self.reg[self.SP] += 1
            self.pc += 2

        def CALL(operand_a, operand_b):
            # Push return address on the stack
            return_address = self.pc + 2
            self.reg[self.SP] -= 1  # decrement SP
            self.ram[self.reg[self.SP]] = return_address

            # Set the PC to the value in the register
            reg_num = operand_a
            self.pc = self.reg[reg_num]

        def RET(operand_a, operand_b):
            # Pop the return address off the stack
            # Store it in the PC
            self.pc = self.ram[self.reg[self.SP]]
            self.reg[self.SP] += 1

        # Calls on ALU
        def MUL(operand_a, operand_b):
            self.alu('MUL', operand_a, operand_b)
            self.pc += 3

        def ADD(operand_a, operand_b):
            self.alu('ADD', operand_a, operand_b)
            self.pc += 3

        def SUB(operand_a, operand_b):
            self.alu('SUB', operand_a, operand_b)
            self.pc += 3

        # Used to stop running CPU
        def HLT(operand_a, operand_b):
            self.running = False
            self.pc += 1

        self.running = True

        self.opcodes = {
            # List of opcodes
            0b10000010: LDI,
            0b01000111: PRN,
            0b00000001: HLT,
            0b10100010: MUL,
            0b10100000: ADD,
            0b10100001: SUB,
            0b01000101: PUSH,
            0b01000110: POP,
            0b01010000: CALL,
            0b00010001: RET
        }

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        program = []

        f = open(f'examples/{sys.argv[1]}', 'r')

        for i in f.read().split('\n'):
            if i != '' and i[0] != '#':
                x = int(i[:8], 2)
                program.append(x)

        f.close()

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        def MUL(reg_a, reg_b):
            self.reg[reg_a] *= self.reg[reg_b]

        def ADD(reg_a, reg_b):
            self.reg[reg_a] += self.reg[reg_b]

        def SUB(reg_a, reg_b):
            self.reg[reg_a] -= self.reg[reg_b]

        alu_opcodes = {
            'MUL': MUL,
            'ADD': ADD,
            'SUB': SUB
        }

        alu_op = alu_opcodes[op]

        if alu_op:
            alu_op(reg_a, reg_b)
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

    # Accepts the address to read and return the value stored there.
    def ram_read(self, mar):
        return self.ram[mar]

    # Accepts a value to write, and the address to write it to.
    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr
        return True

    def run(self):
        """Run the CPU."""
            # Start running the CPU
        while self.running:
            # self.trace()
            # Get the first set of instructions
            # Instruction Register (IR)
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            opcode = self.opcodes[ir]

            if opcode:
                opcode(operand_a, operand_b)
            else:
                print(f'Unknown command: {ir}')
                sys.exit(1)