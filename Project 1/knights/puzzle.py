from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    Not(And(AKnight, AKnave)),  # A cannot be both a knight and a knave
    Or(AKnight, AKnave),  # A is either a knight or a knave
    Implication(AKnight, And(AKnight, AKnave)),  # If A is a knight, the statement is true
    Implication(AKnave, Not(And(AKnight, AKnave)))  # If A is a knave, the statement is false
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    Not(And(AKnight, AKnave)),  # A cannot be both a knight and a knave
    Or(AKnight, AKnave),  # A is either a knight or a knave
    Not(And(BKnight, BKnave)),  # B cannot be both a knight and a knave
    Or(BKnight, BKnave),  # B is either a knight or a knave
    Implication(AKnight, And(AKnave, BKnave)),  # If A is a knight, the statement is true
    Implication(AKnave, Not(And(AKnave, BKnave)))  # If A is a knave, the statement is false
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Not(And(AKnight, AKnave)),  # A cannot be both a knight and a knave
    Or(AKnight, AKnave),  # A is either a knight or a knave
    Not(And(BKnight, BKnave)),  # B cannot be both a knight and a knave
    Or(BKnight, BKnave),  # B is either a knight or a knave
    Implication(AKnight, And(AKnight, BKnight)),  # If A is a knight, both must be the same
    Implication(AKnave, Not(And(AKnave, BKnave))),  # If A is a knave, the statement is false
    Implication(BKnight, And(AKnave, BKnight)),  # If B is a knight, A and B must differ
    Implication(BKnave, Not(And(AKnight, BKnave)))  # If B is a knave, the statement is false
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'." and "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Not(And(AKnight, AKnave)),  # A cannot be both a knight and a knave
    Or(AKnight, AKnave),  # A is either a knight or a knave
    Not(And(BKnight, BKnave)),  # B cannot be both a knight and a knave
    Or(BKnight, BKnave),  # B is either a knight or a knave
    Not(And(CKnight, CKnave)),  # C cannot be both a knight and a knave
    Or(CKnight, CKnave),  # C is either a knight or a knave
    Implication(AKnight, Or(AKnight, AKnave)),  # If A is a knight, their statement is true
    Implication(AKnave, Not(Or(AKnight, AKnave))),  # If A is a knave, their statement is false
    Implication(BKnight, And(
        Implication(AKnight, AKnave),  # B claims A said they are a knave
        Implication(AKnave, Not(AKnave))  # If B is a knight, their statement is true
    )),
    Implication(BKnave, Not(And(
        Implication(AKnight, AKnave),
        Implication(AKnave, Not(AKnave))
    ))),  # If B is a knave, their statement is false
    Implication(BKnight, CKnave),  # B claims C is a knave
    Implication(BKnave, Not(CKnave)),  # If B is a knave, their statement is false
    Implication(CKnight, AKnight),  # C claims A is a knight
    Implication(CKnave, Not(AKnight))  # If C is a knave, their statement is false
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
