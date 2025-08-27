from InstructionGenerator import parse, parseFile
from Emu import Emu

def test_add1():
    asm = "addi t0 t0 10\nstop"
    state = {"t0": 10}
    build(parse(asm), state)

def test_beq():
    instr = parseFile("compiler/test_beq.asm")
    state = {
        "t0" : 10,
        "t1" : 10,
        "t3" : 1

    }
    build(instr, state)

def build(instrs, state):
    emu = Emu(instrs)
    emu.run()

    for reg in state:
        assert int(emu.getReg(reg)) == state[reg]
