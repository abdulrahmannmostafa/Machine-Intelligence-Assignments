from typing import Tuple
import re
from CSP import Assignment, Problem, UnaryConstraint, BinaryConstraint
from itertools import combinations


# This is a class to define for cryptarithmetic puzzles as CSPs
class CryptArithmeticProblem(Problem):
    LHS: Tuple[str, str]
    RHS: str

    # Convert an assignment into a string (so that is can be printed).
    def format_assignment(self, assignment: Assignment) -> str:
        LHS0, LHS1 = self.LHS
        RHS = self.RHS
        letters = set(LHS0 + LHS1 + RHS)
        formula = f"{LHS0} + {LHS1} = {RHS}"
        postfix = []
        valid_values = list(range(10))
        for letter in letters:
            value = assignment.get(letter)
            if value is None:
                continue
            if value not in valid_values:
                postfix.append(f"{letter}={value}")
            else:
                formula = formula.replace(letter, str(value))
        if postfix:
            formula = formula + " (" + ", ".join(postfix) + ")"
        return formula

    @staticmethod
    def from_text(text: str) -> "CryptArithmeticProblem":
        # Given a text in the format "LHS0 + LHS1 = RHS", the following regex
        # matches and extracts LHS0, LHS1 & RHS
        # For example, it would parse "SEND + MORE = MONEY" and extract the
        # terms such that LHS0 = "SEND", LHS1 = "MORE" and RHS = "MONEY"
        pattern = r"\s*([a-zA-Z]+)\s*\+\s*([a-zA-Z]+)\s*=\s*([a-zA-Z]+)\s*"
        match = re.match(pattern, text)
        if not match:
            raise Exception("Failed to parse:" + text)
        LHS0, LHS1, RHS = [match.group(i + 1).upper() for i in range(3)]

        problem = CryptArithmeticProblem()
        problem.LHS = (LHS0, LHS1)
        problem.RHS = RHS

        # TODO Edit and complete the rest of this function
        # problem.variables:    should contain a list of variables where each variable is string (the variable name)
        # problem.domains:      should be dictionary that maps each variable (str) to its domain (set of values)
        #                       For the letters, the domain can only contain integers in the range [0,9].
        # problem.constaints:   should contain a list of constraint (either unary or binary constraints).

        # Reverse the strings to make it easier to handle carry overs
        LHS0 = LHS0[::-1]
        LHS1 = LHS1[::-1]
        RHS = RHS[::-1]

        problem.domains = {}
        problem.constraints = []
        problem.variables = list(set(LHS0 + LHS1 + RHS))

        two_digit_repeats = {i * 11 for i in range(10)}
        three_digit_repeats = set(range(111, 200, 11))

        # Domain for non-leading letters
        digit_domain = set(range(10))
        # Domain for leading letters
        non_zero_digit_domain = set(range(1, 10))
        # Domain for carry variables
        carry_domain = set(range(2))
        # Domain for carry variables + digit variables
        carry_digit_domain = set(range(20))
        # Domain for carry variables + two different digit variables
        carry_two_digit_domain = set(range(100)) - two_digit_repeats
        # Domain for carry variables + three different digit variables
        carry_three_digit_domain = (
            set(range(200)) - two_digit_repeats - three_digit_repeats
        )

        # Represent all constraints
        problem.constraints.extend(
            [
                BinaryConstraint((var1, var2), lambda x, y: x != y)
                for var1, var2 in combinations(problem.variables, 2)
            ]
        )

        # Assign variables to their domains
        for variable in problem.variables:
            # Leading letters cannot be zero
            if variable in (LHS0[-1], LHS1[-1], RHS[-1]):
                problem.domains[variable] = non_zero_digit_domain
            else:
                problem.domains[variable] = digit_domain

        max_length = max(len(LHS0), len(LHS1))
        min_length = min(len(LHS0), len(LHS1))
        max_LHS = LHS0 if len(LHS0) >= len(LHS1) else LHS1

        # Add carry variables and their domains
        problem.variables.extend([f"C{i}" for i in range(max_length)])
        problem.domains.update({f"C{i}": carry_domain for i in range(max_length)})

        # Add variables and domains for summation of (RHS[i] + C[i])
        problem.variables.extend([f"{RHS[i]}C{i}" for i in range(max_length)])
        problem.domains.update(
            {f"{RHS[i]}C{i}": carry_digit_domain for i in range(max_length)}
        )

        # Add variables and domains for sum(LHS1[0] + LHS0[0]) to not have repeats  (where both LHS strings start)
        problem.variables.extend([f"{LHS1[0]}{LHS0[0]}"])
        problem.domains.update(
            {
                f"{LHS1[0]}{LHS0[0]}": (
                    carry_two_digit_domain if LHS0[0] != LHS1[0] else two_digit_repeats
                )
            }
        )

        # Add variables and domains for sum(LHS1[i] + LHS0[i] + C[i]) to not have repeats (where both LHS strings haven't ended yet)
        problem.variables.extend(
            [f"{LHS1[i+1]}{LHS0[i+1]}C{i}" for i in range(min_length - 1)]
        )
        problem.domains.update(
            {
                f"{LHS1[i+1]}{LHS0[i+1]}C{i}": (
                    carry_three_digit_domain
                    if LHS0[i + 1] != LHS1[i + 1]
                    else two_digit_repeats | three_digit_repeats
                )
                for i in range(min_length - 1)
            }
        )

        # Add variables and domains for sum(max_LHS[i] + carry[i]) as max_LHS is the longer of the two LHS strings (if they are of different lengths)
        problem.variables.extend(
            [f"{max_LHS[i+1]}C{i}" for i in range(min_length - 1, len(max_LHS) - 1)]
        )
        problem.domains.update(
            {
                f"{max_LHS[i+1]}C{i}": carry_digit_domain
                for i in range(min_length - 1, len(max_LHS) - 1)
            }
        )

        # Add constraints for the addition (LHS0[0] + LHS1[0] = RHS[0] + 10*C0)
        problem.constraints.extend(
            [
                BinaryConstraint(
                    (f"{LHS1[0]}{LHS0[0]}", LHS1[0]), lambda x, y: x // 10 == y
                ),
                BinaryConstraint(
                    (f"{LHS1[0]}{LHS0[0]}", LHS0[0]), lambda x, y: x % 10 == y
                ),
            ]
        )

        # Add constraints for the of the addition of (LHS1[i] + LHS0[i] + C[i] = RHS[i] + 10*C[i+1])
        problem.constraints.append(
            BinaryConstraint(
                (f"{LHS1[0]}{LHS0[0]}", f"{RHS[0]}C{0}"),
                lambda x, y: (x % 10 + x // 10) == y % 10 + 10 * (y // 10),
            )
        )

        for i in range(max_length):

            carry_var = f"C{i}"
            sum_var = f"{RHS[i]}C{i}"

            # Add constraints of the RHS digit and carry from the sum
            problem.constraints.extend(
                [
                    BinaryConstraint((sum_var, carry_var), lambda x, y: x // 10 == y),
                    BinaryConstraint((sum_var, RHS[i]), lambda x, y: x % 10 == y),
                ]
            )

            # If the strings both havn't ended yet
            if i < min_length - 1:
                combined_var = f"{LHS1[i+1]}{LHS0[i+1]}C{i}"

                problem.constraints.extend(
                    [
                        BinaryConstraint(
                            (combined_var, carry_var), lambda x, y: x // 100 == y
                        ),  #  constraint for carry with combined variable
                        BinaryConstraint(
                            (combined_var, f"{RHS[i+1]}C{i+1}"),
                            lambda x, y: (
                                x // 100 + (x % 100) // 10 + (x % 100) % 10
                                == y % 10 + 10 * (y // 10)
                            ),
                        ),  # constraint for RHS with combined variable for validating the sum
                        BinaryConstraint(
                            (combined_var, f"{LHS1[i+1]}"),
                            lambda x, y: (x % 100) % 10 == y,
                        ),  # constraint for LHS1 with combined variable for validating the sum
                        BinaryConstraint(
                            (combined_var, f"{LHS0[i+1]}"),
                            lambda x, y: (x % 100) // 10 == y,
                        ),  # constraint for LHS0 with combined variable for validating the sum
                    ]
                )

            # If only one of the LHS strings has ended
            elif i < len(max_LHS) - 1:
                combined_var = f"{max_LHS[i+1]}C{i}"

                problem.constraints.extend(
                    [
                        BinaryConstraint(
                            (combined_var, max_LHS[i + 1]), lambda x, y: x % 10 == y
                        ),  # constraint for the longer string with the combined variable
                        BinaryConstraint(
                            (combined_var, carry_var), lambda x, y: x // 10 == y
                        ),  # constraint for carry with combined variable
                        BinaryConstraint(
                            (combined_var, f"{RHS[i+1]}C{i+1}"),
                            lambda x, y: (x // 10 + x % 10 == y % 10 + 10 * (y // 10)),
                        ),  # constraint for RHS with combined variable (to make sure the sum is correct)
                    ]
                )

        if len(RHS) > max_length:
            # Update the domain for the last digit of RHS and last carry if the RHS is longer than the sum of the two LHS strings because the last digit of RHS must be 1 (as the maximum sum of two digits + carry is 19)
            problem.domains[RHS[-1]] = {1}
            problem.domains[f"C{max_length-1}"] = {1}
        else:
            # Update the domain for the last carry if the LHS strings are as long or longer than the RHS because the last carry must be 0 in this case
            problem.domains[f"C{max_length-1}"] = {0}
        return problem

    # Read a cryptarithmetic puzzle from a file
    @staticmethod
    def from_file(path: str) -> "CryptArithmeticProblem":
        with open(path, "r") as f:
            return CryptArithmeticProblem.from_text(f.read())
