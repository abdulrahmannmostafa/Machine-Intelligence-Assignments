from typing import Any, Dict, List, Optional
from CSP import Assignment, BinaryConstraint, Problem, UnaryConstraint
from helpers.utils import NotImplemented

# This function applies 1-Consistency to the problem.
# In other words, it modifies the domains to only include values that satisfy their variables' unary constraints.
# Then all unary constraints are removed from the problem (they are no longer needed).
# The function returns False if any domain becomes empty. Otherwise, it returns True.
def one_consistency(problem: Problem) -> bool:
    remaining_constraints = []
    solvable = True
    for constraint in problem.constraints:
        if not isinstance(constraint, UnaryConstraint):
            remaining_constraints.append(constraint)
            continue
        variable = constraint.variable
        new_domain = {value for value in problem.domains[variable] if constraint.condition(value)}
        if not new_domain:
            solvable = False
        problem.domains[variable] = new_domain
    problem.constraints = remaining_constraints
    return solvable

# This function returns the variable that should be picked based on the MRV heuristic.
# NOTE: We don't use the domains inside the problem, we use the ones given by the "domains" argument 
#       since they contain the current domains of unassigned variables only.
# NOTE: If multiple variables have the same priority given the MRV heuristic, 
#       we order them in the same order in which they appear in "problem.variables".
def minimum_remaining_values(problem: Problem, domains: Dict[str, set]) -> str:
    _, _, variable = min((len(domains[variable]), index, variable) for index, variable in enumerate(problem.variables) if variable in domains)
    return variable

# This function should implement forward checking
# The function is given the problem, the variable that has been assigned and its assigned value and the domains of the unassigned values
# The function should return False if it is impossible to solve the problem after the given assignment, and True otherwise.
# In general, the function should do the following:
#   - For each binary constraints that involve the assigned variable:
#       - Get the other involved variable.
#       - If the other variable has no domain (in other words, it is already assigned), skip this constraint.
#       - Update the other variable's domain to only include the values that satisfy the binary constraint with the assigned variable.
#   - If any variable's domain becomes empty, return False. Otherwise, return True.
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.

def forward_checking(problem: Problem, assigned_variable: str, assigned_value: Any, domains: Dict[str, set]) -> bool:
    """
    Performs forward checking to prune the domains of unassigned variables.
    
    Algorithm:
    1. Identify all binary constraints involving the 'assigned_variable'.
    2. For each constraint, find the 'other_variable' (neighbor).
    3. If the neighbor is already assigned (not in domains), skip it.
    4. Iterate through the neighbor's domain and remove values inconsistent with the 
       (assigned_variable, assigned_value) assignment.
    5. If any neighbor's domain becomes empty, return False (failure).
    6. If all checks pass, return True.
    """
    
    # Iterate over all constraints in the problem definition
    for constraint in problem.constraints:
        
        # Forward checking strictly applies to binary constraints (those involving exactly 2 variables)
        if len(constraint.variables) != 2:
            continue
            
        # We strictly care about constraints that involve the variable we just assigned
        if assigned_variable not in constraint.variables:
            continue
            
        # Identify the other variable involved in this binary constraint
        # constraint.variables is a list/tuple. We pick the one that isn't the assigned_variable.
        other_variable = constraint.variables[0] if constraint.variables[1] == assigned_variable else constraint.variables[1]
        
        # "If the other variable has no domain (in other words, it is already assigned a value), skip this constraint."
        # We assume the 'domains' dictionary contains keys only for unassigned variables.
        if other_variable not in domains:
            continue
            
        # Get the domain of the neighbor. We will modify this set in place.
        other_domain = domains[other_variable]
        
        # We need to collect values to remove first, because we cannot modify a set while iterating over it.
        values_to_remove = []
        
        for other_value in other_domain:
            # Create a hypothetical assignment containing the new assignment and the neighbor's potential value
            assignment = {assigned_variable: assigned_value, other_variable: other_value}
            
            # Check if this combination satisfies the constraint
            if not constraint.is_satisfied(assignment):
                values_to_remove.append(other_value)
        
        # "Update the other variable's domain to only include the values that satisfy the binary constraint"
        for val in values_to_remove:
            other_domain.remove(val)
            
        # "If any variable's domain becomes empty, return False."
        if not other_domain:
            return False
            
    # If we finish checking all constraints and no domain is empty, the assignment is currently valid.
    return True

# This function should return the domain of the given variable order based on the "least restraining value" heuristic.
# IMPORTANT: This function should not modify any of the given arguments.
# Generally, this function is very similar to the forward checking function, but it differs as follows:
#   - You are not given a value for the given variable, since you should do the process for every value in the variable's
#     domain to see how much it will restrain the neigbors domain
#   - Here, you do not modify the given domains. But you can create and modify a copy.
# IMPORTANT: If multiple values have the same priority given the "least restraining value" heuristic, 
#            order them in ascending order (from the lowest to the highest value).
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
def least_restraining_values(problem: Problem, variable_to_assign: str, domains: Dict[str, set]) -> List[Any]:
    """
    Values Ordering Heuristic: Least Restraining Value (LRV)
    """
    
    # Get the list of values currently available for the variable we are about to assign
    possible_values = list(domains[variable_to_assign])
    
    # We will store tuples of (score, value) to sort them later
    # Score = number of values removed from neighbors if we pick this value
    scored_values = []
    
    for value in possible_values:
        restraint_count = 0
        
        # Iterate over constraints to find neighbors, similar to forward_checking
        for constraint in problem.constraints:
            if len(constraint.variables) != 2:
                continue
                
            if variable_to_assign not in constraint.variables:
                continue
                
            # Identify the neighbor
            other_variable = constraint.variables[0] if constraint.variables[1] == variable_to_assign else constraint.variables[1]
            
            # Skip if neighbor is already assigned
            if other_variable not in domains:
                continue
                
            other_domain = domains[other_variable]
            
            # Count how many values in the neighbor's domain would be pruned
            for other_value in other_domain:
                assignment = {variable_to_assign: value, other_variable: other_value}
                if not constraint.is_satisfied(assignment):
                    restraint_count += 1
                    
        scored_values.append((restraint_count, value))
        
    # Sort by score (ascending). 
    # This ensures deterministic behavior on empty grids where scores are equal.
    scored_values.sort(key=lambda x: (x[0], x[1]))
    
    # Return only the values, extracted from the sorted tuples
    return [item[1] for item in scored_values]

# This function should solve CSP problems using backtracking search with forward checking.
# The variable ordering should be decided by the MRV heuristic.
# The value ordering should be decided by the "least restraining value" heurisitc.
# Unary constraints should be handled using 1-Consistency before starting the backtracking search.
# This function should return the first solution it finds (a complete assignment that satisfies the problem constraints).
# If no solution was found, it should return None.
# IMPORTANT: To get the correct result for the explored nodes, you should check if the assignment is complete only once using "problem.is_complete"
#            for every assignment including the initial empty assignment, EXCEPT for the assignments pruned by the forward checking.
#            Also, if 1-Consistency deems the whole problem unsolvable, you shouldn't call "problem.is_complete" at all.
def solve(problem: Problem) -> Optional[Assignment]:
    """
    Solves the CSP using Backtracking Search with Forward Checking, MRV, and LRV.
    """
    
    # 1. Pre-processing: Unary Constraints (1-Consistency)
    # If 1-Consistency deems the problem unsolvable, return None immediately.
    if not one_consistency(problem):
        return None
        
    # Initialize domains with the state after 1-consistency.
    # We create a dictionary representing the domains of currently unassigned variables.
    initial_domains = {v: problem.domains[v].copy() for v in problem.variables}
    
    def backtrack(assignment: Assignment, current_domains: Dict[str, set]) -> Optional[Assignment]:
        # 2. Check Completeness
        # "check if the assignment is complete only once... EXCEPT for the assignments pruned"
        if problem.is_complete(assignment):
            return assignment
        
        # 3. Variable Selection (MRV)
        # Select the unassigned variable with the smallest domain
        variable = minimum_remaining_values(problem, current_domains)
        
        # 4. Value Ordering (LRV)
        # Order values by how little they constrain neighbors
        ordered_values = least_restraining_values(problem, variable, current_domains)
        
        for value in ordered_values:
            # Create a new assignment with this value
            new_assignment = assignment.copy()
            new_assignment[variable] = value
            
            # Create a DEEP COPY of domains for the next branch
            # We filter out the variable we just assigned from the domains dictionary
            # This effectively marks it as 'assigned' for the helper functions
            new_domains = {k: v.copy() for k, v in current_domains.items() if k != variable}
            
            # 5. Forward Checking (Pruning)
            # This function modifies 'new_domains' in-place
            if forward_checking(problem, variable, value, new_domains):
                # If consistent, continue recursion
                result = backtrack(new_assignment, new_domains)
                if result is not None:
                    return result
            
            # If forward_checking returned False, we pruned this branch.
            # We do NOT call problem.is_complete on this failed branch (implicitly handled).
            
        # If no value works, return None (backtrack)
        return None

    # Start backtracking with empty assignment and initial domains
    return backtrack({}, initial_domains)