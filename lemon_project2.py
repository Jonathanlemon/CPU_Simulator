import sys
import time
from abc import ABC, abstractmethod

# Model - CPU Components
class CPUModel:
    def __init__(self):
        self.registers = [0] * 32
        self.line_count = 0
        self.memory = [0] * 256
        self.PC = 0
        self.cycles = 0
        self.ALU_operations = {'add': 0, 'and': 0, 'or': 0, 'sub': 0, 'slt': 0, 'addi': 0}
        self.memory_reads = 0
        self.memory_writes = 0
        self.instructions_count = {'add': 0, 'and': 0, 'or': 0, 'sub': 0, 'slt': 0, 'addi': 0, 'lw': 0, 'sw': 0, 'beq':0, 'j': 0}
        
    def fetch_instruction(self):
        instruction = self.memory[self.PC]
        self.PC += 1
        return instruction

    def execute_instruction(self, instruction):
        opcode = instruction >> 26
        if opcode == 0:
            self.execute_R_type(instruction)
        elif opcode == 2:  # Jump instruction
            self.instructions_count['j'] += 1
            target = instruction & 0x03FFFFFF
            self.PC = target
        elif opcode == 4:  # beq
            self.instructions_count['beq'] += 1
            self.ALU_operations['sub'] += 1
            rs = (instruction >> 21) & 0x1F
            rt = (instruction >> 16) & 0x1F
            if(self.registers[rs] == self.registers[rt]):
               value = (instruction & 0xFFFF)
               value = self.handle_negative(value, 16)
               self.PC += value
        elif opcode == 8: # addi
            self.execute_addi(instruction)
        elif opcode == 35 or opcode == 43:  # lw, sw
            self.memory_access(instruction)
        else:
            print("Unknown Opcode")
            return
    
    def handle_negative(self, value, bits):
        if(value > (pow(2, bits-1) - 1)):
            value -= pow(2, bits)
        
        return value

    def execute_addi(self, instruction):
        rs = (instruction >> 21) & 0x1F
        rt = (instruction >> 16) & 0x1F
        immediate = instruction & 0xFFFF
        immediate = self.handle_negative(immediate, 16)
        self.ALU_operations['addi'] += 1
        self.instructions_count['addi'] += 1
        self.registers[rt] = self.registers[rs] + immediate

    def execute_R_type(self, instruction):
        function_code = instruction & 0x3F
        rs = (instruction >> 21) & 0x1F
        rt = (instruction >> 16) & 0x1F
        rd = (instruction >> 11) & 0x1F
        shamt = (instruction >> 6) & 0x1F

        if function_code == 32:  # add
            self.registers[rd] = self.registers[rs] + self.registers[rt]
            self.ALU_operations['add'] += 1
            self.instructions_count['add'] += 1
        elif function_code == 36:  # and
            self.registers[rd] = self.registers[rs] & self.registers[rt]
            self.ALU_operations['and'] += 1
            self.instructions_count['and'] += 1
        elif function_code == 37:  # or
            self.registers[rd] = self.registers[rs] | self.registers[rt]
            self.ALU_operations['or'] += 1
            self.instructions_count['or'] += 1
        elif function_code == 34:  # sub
            self.registers[rd] = self.registers[rs] - self.registers[rt]
            self.ALU_operations['sub'] += 1
            self.instructions_count['sub'] += 1
        elif function_code == 42:  # slt
            self.registers[rd] = 1 if self.registers[rs] < self.registers[rt] else 0
            self.ALU_operations['slt'] += 1
            self.instructions_count['slt'] += 1

    def memory_access(self, instruction):
        opcode = instruction >> 26
        base = (instruction >> 21) & 0x1F
        rt = (instruction >> 16) & 0x1F
        offset = instruction & 0xFFFF
        offset = self.handle_negative(offset, 16)
        
        if opcode == 35:  # lw
            self.registers[rt] = self.memory[int((self.registers[base] + offset)/4)]
            self.memory_reads += 1
            self.instructions_count['lw'] += 1
        elif opcode == 43:  # sw
            print("Storing: ",self.registers[rt]," in ",int((self.registers[base] + offset)/4))
            self.memory[int((self.registers[base] + offset)/4)] = self.registers[rt]
            self.memory_writes += 1
            self.instructions_count['sw'] += 1

    def run(self):
        while self.PC < self.line_count:
            self.update_views()
            instruction = self.fetch_instruction()
            self.execute_instruction(instruction)
            self.cycles += 1
            time.sleep(2.5)  # To slow down execution for demonstration
        self.update_views()

    def attach_view(self, view):
        self.view = view

    def update_views(self):
        self.view.update()

# View
class TextView:
    def __init__(self, model):
        self.model = model

    def update(self):
        print("Cycle:", self.model.cycles)
        print("PC:", self.model.PC)
        print("Registers:", self.model.registers)
        print("Memory:", self.model.memory)
        print("ALU Operations:", self.model.ALU_operations)
        print("Memory Reads:", self.model.memory_reads)
        print("Memory Writes:", self.model.memory_writes)
        print("Instructions Count:", self.model.instructions_count)
        print()

# Controller
class Controller:
    def __init__(self, model):
        self.model = model

    def run_program(self):
        self.model.run()

# Main function
def main():
    # Read binary file and load instructions into memory
    cpu = CPUModel()

    file = open(sys.argv[1], "rb")
    instruction_value = -1
    count = 0

    while(instruction_value != 0):
        instruction_value = int.from_bytes(file.read(4), "big")
        if(instruction_value != 0):
            cpu.memory[count] = instruction_value
            count += 1
    
    cpu.line_count = count

    # Initialize view and controller
    text_view = TextView(cpu)
    cpu.attach_view(text_view)
    controller = Controller(cpu)
    print("Total instructions: ", count)
    # Run the program
    controller.run_program()
    file.close()
if __name__ == "__main__":
    main()
