import copy
import itertools
import sys

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
        for var in self.crossword.variables:
            for word in self.crossword.words:
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]
        if overlap:
            i, j = overlap
            for word_x in self.domains[x].copy():
                if not any(word_x[i] == word_y[j] for word_y in self.domains[y]):
                    self.domains[x].remove(word_x)
                    revised = True
        return revised

        # revised = False
        # intersection = self.crossword.overlaps[x, y]
        # if intersection is None:
        #     return False
        # domainx = self.domains[x].copy()
        #
        # for xword in domainx:
        #     for yword in self.domains[y]:
        #         if not xword[intersection[0]] == yword[intersection[1]]:
        #             self.domains[x].remove(xword)
        #             revised = True
        #
        # return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if arcs is None:
            arcs = list(self.crossword.overlaps.keys())

        while len(arcs) > 0:
            x, y = arcs.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False

                for z in self.crossword.neighbors(x) - self.domains[y]:  # TODO - {y}
                    arcs.append((x, z))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return all(var in assignment for var in self.crossword.variables)

    # def consistent(self, assignment):
    #     """
    #     Return True if `assignment` is consistent (i.e., words fit in crossword
    #     puzzle without conflicting characters); return False otherwise.
    #     """
    #     words = list(assignment.values())
    #     if len(words) != len(set(words)):
    #         return False
    #     for val in assignment.keys():
    #         if not len(assignment[val]) in [len(self.crossword.variables)]:
    #             return False
    #         for n in self.crossword.neighbors(val):
    #             if n in assignment:
    #                 if self.crossword.overlaps[n, val] is None:
    #                     continue
    #                 i,j = self.crossword.overlaps[n, val]
    #                 if assignment[val][j] != assignment[n][i]:
    #                     return False
    #
    #
    #     return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check if all words are unique
        # words = list(assignment.values())
        # if len(words) != len(set(words)):
        #     return False

        # Check if words fit into their respective variables and satisfy overlaps
        for variable, word in assignment.items():
            if len(word) != variable.length:
                return False
            for neighbor in self.crossword.neighbors(variable):
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[variable, neighbor]
                    if word[i] != assignment[neighbor][j]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        dict = {}
        for xword in self.domains[var]:
            dict[xword] = 0

        for xword, yvar in itertools.product(self.domains[var], assignment.keys()):
            for yword in yvar:
                if self.crossword.overlaps[var, yvar] is None:
                    continue

                i, j = self.crossword.overlaps[var, yvar]
                if (yword[i] != xword[j]) or (yword == xword):
                    dict[xword] += 1

        # sorted_items = sorted(dict.items())
        # sorted_keys = [item[0] for item in sorted_items]
        return sorted(dict, key=dict.get)
        # return sorted_keys

        # for var, domain in assignment:
        #     for xword in assignment[var]:
        #         for yword in domain:
        #             i, j = self.crossword.overlaps[var,]
        #             if yword[i] != assignment[neighbor][j]:

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        unassigned = [var for var in self.crossword.variables if var not in assignment]

        # Create a list of tuples (variable, domain size)
        unvars_lens = [(var, len(self.domains[var])) for var in unassigned]

        # Sort unassigned variables by domain size (ascending)
        unvars_sorted = sorted(unvars_lens, key=lambda x: x[1])

        # if unvars_sorted[0][1] == unvars_sorted[1][1]:
        #     if self.crossword.neighbors(unvars_sorted[0][0]) >= self.crossword.neighbors(unvars_sorted[1][0]):
        #         return unvars_sorted[0][0]
        #     else:
        #         return unvars_sorted[1][0]
        #
        # else:
        return unvars_sorted[0][0]
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if len(assignment) == len(self.crossword.variables):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.domains[var]:
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            assignment.pop(var)
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
