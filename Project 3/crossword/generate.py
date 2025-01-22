import sys
import copy
from collections import deque, defaultdict
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            words_to_remove = set()
            for word in self.domains[var]:
                if len(word) != var.length:
                    words_to_remove.add(word)
            # Remove values from domains
            self.domains[var] -= words_to_remove

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        if not self.crossword.overlaps[x, y]:
            return False

        # xi, yi represent intersection position in x and y
        xi, yi = self.crossword.overlaps[x, y]
        wordx_to_remove = set()
        for wordx in self.domains[x]:
            char = wordx[xi]
            if all(char != wordy[yi] for wordy in self.domains[y]):
                wordx_to_remove.add(wordx)

        self.domains[x] -= wordx_to_remove

        return True if len(wordx_to_remove) > 0 else False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = deque()
        if arcs is None:
            # Include all the arcs into the queue
            queue = deque(list(self.crossword.overlaps.keys()))
        else:
            queue = deque(arcs)

        while queue:
            x, y = queue.popleft()
            if self.revise(x, y):
                # x has changes:
                if len(self.domains[x]) == 0:
                    return False
                else:
                    for z in self.crossword.neighbors(x) - {y}:
                        queue.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(self.crossword.variables) == len(assignment):
            return True

        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        word_set = set()
        for var in self.crossword.variables:
            if var not in assignment:
                continue

            word = assignment[var]
            # Check length
            if var.length != len(word):
                return False

            # Check Distinct
            if word in word_set:
                return False
            word_set.add(word)

            # Check Conflict with neighbors
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    continue
                overlap = self.crossword.overlaps[var, neighbor]
                if word[overlap[0]] != assignment[neighbor][overlap[1]]:
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        value_dict = defaultdict(int)
        for word in self.domains[var]:
            constrain = 0
            for v in assignment:
                if ((var, v) not in self.crossword.overlaps or
                    self.crossword.overlaps[var, v] is None):
                    continue
                xi, yi = self.crossword.overlaps[var, v]
                for wordy in self.domains[v]:
                    if word[xi] != wordy[yi]:
                        constrain += 1
            value_dict[word] = constrain

        # return sorted value_dict
        return sorted(value_dict, key=value_dict.get)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Get all the unassigned avaibles
        unassigned = list(self.crossword.variables - set(assignment.keys()))

        # Frist ranked by fewer size of values, and then
        # ranked by larger amount of neighbors
        var_dict = {
            var: (-len(self.domains[var]), len(self.crossword.neighbors(var)))
            for var in unassigned
        }

        # Sort the var_dict
        sorted_vars = sorted(var_dict, key=var_dict.get, reverse=True)

        # Return the first item or None
        return sorted_vars[0] if sorted_vars else None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        # Pick a variable to assign values
        var = self.select_unassigned_variable(assignment)

        # Can't pick a variable
        if not var:
            return None

        # Select a value assign to variable
        for value in self.order_domain_values(var, assignment):
            # assign a new value to assignment
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result:
                    return result
            else:
                del assignment[var]

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
