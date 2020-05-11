# Samuel Eriksson Lidbrink Grudat20
"""A symbolic math API.

This module is a simple library of tools to make symbolic computations and basic operations on algebraic functions.



Example:
    Example usage:

        >>> import symbol_math
        >>> f = symbol_math.Function("x^2+x+3x", "x")
        >>> print(f.simplify())
        x^2 + 4x
        >>> print(f.derivative())
        2x + 4

Todo:
    * Fix function 'simplify'
    * Add more functionality.
    * Improve documentation.
    * Error handling
"""
import math


class Function(object):
    """A class for storing functions.

    Todo:
        * Add functionality for multivariable functions
        * Implement more operators such as sub, div.
        * Fix methods 'evaluate', 'derivative'
        * Error handling

    """

    def __init__(self, expression, variable):
        """
        Args:
            expression (string): The functions expression. Must be an algebraic expression
            variable (string): The function variable
        Raises:
            TypeError: expression not recognisable as algebraic expression or variable name equal to protected function
        """
        _check_expression(expression, variable)
        self.expression = expression
        self.variable = variable

    def simplify(self):
        """Simplifies expression to simplest form.
        Returns:
            string: new expression for function
            """
        self.expression = simplify(self.expression, self.variable)
        return self.expression

    def evaluate(self, value):
        """Evaluates the function at specified value
        Args:
            value (float, int): Value where function should be evaluated
        Returns:
            float: function evaluation
        """
        return evaluate(self.expression, self.variable, value)

    def change_variable(self, variable):
        """Changes the current function variable to the given variable.
        Args:
            variable (string): New variable for function
        Returns:
            string: New function expression
        """
        self.expression = replace_var(self.expression, self.variable, variable)
        self.variable = variable
        return self.expression

    def __add__(self, other):
        """Addition operator for two functions of the same variables.
        Overloads + operator as addition defined for functions.
        Args:
            other (Function): Other function to be added
        Returns:
            object: the function that is the sum of self and other
        Raises:
             TypeError: If other.variable != self.variable
         """
        if other.variable != self.variable:
            raise TypeError("Functions must have the same variable")
        return Function(simplify(self.expression + other.expression), self.variable)

    def __str__(self):
        """String representation.
        Overloads str operator with function expression"""
        return self.expression

    def derivative(self):
        """Calculate derivative of function
        Returns:
            object: the function derivative
        Raises:
             SystemError: Cannot compute derivative internally
         """
        pass

    def finite_integration(self, lower_bound, upper_bound):
        """Calculate derivative of function
        Args:
            lower_bound (float): lower integration bound
            upper_bound (float): upper integration bound
        Returns:
            float: integral of self over lower_bound to upper_bound
         """
        pass


COMMON_OPERATORS = ["sinh", "cosh", "tanh", "asinh", "acosh", "atanh", "sin", "cos", "tan", "asin", "atan", "acos",
                    "log", "exp"]


def simplify(expression, variable):
    """Simplifies expression to simplest form.
    Args:
        expression (string): The expression that should be simplified.
        variable (string): Used variable in expression
    Returns:
        string: simplified expression.
    Raises:
        TypeError: expression not recognisable as algebraic expression or variable name equal to protected function
    """
    _check_expression(expression, variable)
    return "".join(_simp_helper(_interp_expr(expression.replace(variable, "X"), "X"))).replace("X", variable)


def _simp_helper(expression_list, mem=None):
    """A help function for simplify."""
    # memorizes previous result to avoid loops
    if mem is None:
        mem = []
    mem.append(expression_list.copy())

    prev_thing = "{"
    for index in range(0, len(expression_list)):
        thing = expression_list[index]
        if index + 1 < len(expression_list):
            next_thing = expression_list[index + 1]
        else:
            next_thing = "}"

        # Remove redundant expressions
        if not (isinstance(thing, list) or isinstance(prev_thing, list))\
                and ((thing == "0" and prev_thing in "+-{(" and next_thing in "+-") or \
                (thing == "1" and prev_thing == "^") or (thing == "1" and prev_thing in "*/") or \
                (thing in "*/" and prev_thing == "1")):
            if index - 1 > 0:
                expression_list = expression_list[:index - 1] + expression_list[index + 1:]
            else:
                expression_list = expression_list[index + 1:]
            break
        elif prev_thing == "(" and next_thing == ")":
            if index-2 < 0 or expression_list[index-2] not in COMMON_OPERATORS:
                if index - 1 > 0:
                    expression_list = expression_list[:index-1] + [thing] + expression_list[index+1:]
                else:
                    expression_list = [thing] + expression_list[index+1:]
                break

        # does basic calculation
        if not isinstance(thing, list):
            if thing == "/" and (isinstance(prev_thing, int) or prev_thing.isdigit()) and (isinstance(next_thing, int) or
                                                                                           next_thing.isdigit()):
                divisor = math.gcd(int(prev_thing), int(next_thing))
                if divisor not in [0, 1]:
                    expression_list[index-1] = str(int(prev_thing)/divisor)
                    expression_list[index+1] = str(int(next_thing)/divisor)
                    break
            elif thing in "+-*/^" and _is_float(prev_thing) and _is_float(next_thing):
                if index + 2 == len(expression_list) or expression_list[index + 2] != "^":
                    new_num = eval(prev_thing + thing.replace("^", "**") + next_thing)
                    if index - 1 > 0:
                        expression_list = expression_list[:index-1] + [str(new_num)] + expression_list[index+1:]
                    else:
                        expression_list = [str(new_num)] + expression_list[index+1:]
                    break

        prev_thing = thing

    # groups similar object together in preferred order
    def group(list_to_group):
        first_level = []
        is_first = True
        second_level = []
        par_count = 0
        for item in list_to_group:
            if item == "(":
                if not is_first:
                    second_level.append(item)
                par_count += 1
                is_first = False
            elif item == ")":
                par_count -= 1
                if par_count == 0:
                    is_first = True
                    first_level.append(group(second_level))
                    second_level = []
                else:
                    second_level.append(item)
            elif is_first:
                first_level.append(item)
            else:
                second_level.append(thing)
        return first_level

    def sort_and_ungroup(list_to_fix):
        res = []
        list_to_fix = sort_group(list_to_fix)
        for item in list_to_fix:
            if isinstance(item, list):
                res.append("(")
                nested_list = sort_and_ungroup(item)
                for nested_item in nested_list:
                    res.append(nested_item)
                res.append(")")
            else:
                res.append(item)
        return res

    def sort_group(list_to_sort):
        types = dict()
        cur = []
        prev_sign = 1
        if list_to_sort[0] == "-":
            prev_sign = -1
        for item_index in range(0, len(list_to_sort)+1):
            if item_index < len(list_to_sort):
                item = list_to_sort[item_index]
            else:
                item = "}"
            if (item == "+" or item == "-" or item == "}") and (len(cur) > 0 or
                                                                item_index - 1 >= 0 and cur[item_index - 1] != "("):
                fixed_part = fix_mult(cur)
                if len(fixed_part) == 1:
                    types["1"] = ["1", types.setdefault("1", ["", 0])[1] + prev_sign * float(fixed_part[0])]
                else:
                    types[str(fixed_part[2:])] = [fixed_part[2:], types.setdefault(str(fixed_part[2:]), ["", 0])[1] +
                                                  prev_sign * float(fixed_part[0])]
                if item == "+":
                    prev_sign = 1
                elif item == "-":
                    prev_sign = -1
                cur = []
            else:
                cur.append(item)
        res = []
        for dic_item in types.items():
            if dic_item[1][1] == 0:
                continue
            elif dic_item[1][1] == 1:
                res.extend(["+"] + dic_item[1][0])
            elif dic_item[1][1] == -1:
                res.extend(["-"] + dic_item[1][0])
            elif dic_item[1][1] > 0:
                res.extend(["+", str(dic_item[1][1]), "*"] + dic_item[1][0])
        return res

    def fix_mult(list_to_fix):
        # Returns an expression without +- simplified with a leading coefficient (and perhaps *[...])
        prev = "{"
        const = 1
        var_pow = 0
        exp = []
        par = []
        exp_to_check = []
        par_to_check = {}
        for item_index in range(0, len(list_to_fix)):
            item = list_to_fix[item_index]
            if item_index + 1 == len(list_to_fix):
                next_i = "}"
            else:
                next_i = list_to_fix[item_index + 1]
            if (isinstance(item, str) and item in "*/^") or (isinstance(prev, str) and prev == "^"):
                prev = item
                continue
            if prev in "*{":
                sign = 1
            elif prev in "/":
                sign = -1
            if item == "X":
                if next_i == "^":
                    x_pow = list_to_fix[item_index + 2]
                    if x_pow == "X" or isinstance(x_pow, list):
                        if sign == 1:
                            if len(exp) > 0:
                                exp.append("*")
                        elif sign == -1:
                            if len(exp) == 0:
                                exp.append("1")
                            exp.append("/")
                        exp.extend(["X", "^", x_pow])
                        prev = item
                        continue
                else:
                    x_pow = 1
                if isinstance(x_pow, int) or x_pow.isdigit():
                    var_pow += sign * int(x_pow)
                else:
                    var_pow += sign * float(x_pow)
            elif _is_float(item):
                if next_i == "^":
                    num_pow = list_to_fix[item_index + 2]
                    if num_pow == "X":
                        exp_to_check.append(item)
                        prev = item
                        continue
                    elif isinstance(num_pow, list):
                        if sign == 1:
                            if len(exp) > 0:
                                exp.append("*")
                        elif sign == -1:
                            if len(exp) == 0:
                                exp.append("1")
                            exp.append("/")
                        exp.extend([item, "^", num_pow])
                        prev = item
                        continue
                else:
                    num_pow = 1
                if sign == 1:
                    const *= float(item) ** float(num_pow)
                elif sign == -1:
                    const /= float(item) ** float(num_pow)
            elif isinstance(item, list) and prev != "^":

                if next_i == "^" and not _is_float(list_to_fix[item_index + 2]):
                    if sign == 1:
                        if len(par) > 0:
                            par.append("*")
                    elif sign == -1:
                        if len(par) == 0:
                            par.append("1")
                        par.append("/")
                    if next_i == "^":
                        par.extend([item, "^", list_to_fix[item_index + 2]])
                else:
                    if next_i == "^":
                        extra = float(list_to_fix[item_index + 2])
                    else:
                        extra = 1
                    par_to_check[str(item)] = [item, par_to_check.setdefault(str(item), [[], 0])[1] + sign * extra]
            prev = item
        for dic_item in par_to_check.items():
            if dic_item[1][1] == 0:
                continue
            elif dic_item[1][1] == 1:
                if len(par) > 0:
                    par.append("*")
                par.append([dic_item[1][0]])
            elif dic_item[1][1] == -1:
                if len(par) == 0:
                    par.append("1")
                par.extend(["/"] + [dic_item[1][0]])
            elif dic_item[1][1] > 0:
                if len(par) > 0:
                    par.append("*")
                par.extend([dic_item[1][0]] + ["^"] + [str(dic_item[1][1])])
            else:
                if len(par) == 0:
                    par.append("1")
                par.extend(["/"] + [dic_item[1][0]] + ["^"] + [str(dic_item[1][1])])

        # simplifies exponents
        prev_check = []
        while prev_check != exp_to_check:
            prev_check = exp_to_check.copy()
            exp_to_check = sorted(exp_to_check)
            for dig_index in range(0, len(exp_to_check) - 1):
                cur_dig = exp_to_check[dig_index]
                next_dig = exp_to_check[dig_index + 1]
                if cur_dig == next_dig:
                    if dig_index > 0:
                        exp_to_check = exp_to_check[:dig_index] + exp_to_check[dig_index + 2:] + [str(float(cur_dig) *
                                                                                                      float(next_dig))]
                        break
                    else:
                        exp_to_check = exp_to_check[dig_index + 2:] + [str(float(cur_dig) * float(next_dig))]
                        break
        if len(exp_to_check) == 1:
            if len(exp) == 0:
                exp = [str(exp_to_check[0]), "^", "X"]
            else:
                exp.extend(["*", str(exp_to_check[0]), "^", "X"])
        elif len(exp_to_check) > 1:
            if len(exp) > 0:
                exp.append("*")
            for dig_index in range(0, len(exp_to_check)):
                exp.extend([str(exp_to_check[dig_index]), "^", "X"])
                if dig_index < len(exp_to_check) - 1:
                    exp.append("*")

        if const == 0:
            return ["0"]
        if len(exp) == 0:
            end = par
        elif len(par) == 0:
            end = exp
        else:
            end = exp + ["*"] + par
        if var_pow != 0:
            if len(end) > 0:
                end = ["*"] + end
            if not var_pow == 1:
                end = ["^", str(var_pow)] + end
            end = ["X"] + end
        if len(end) > 0:
            return [str(const), "*"] + end
        else:
            return [str(const)]
    a = sort_and_ungroup(group(expression_list))
    new_list = sort_and_ungroup(group(expression_list))
    if new_list in mem:
        return new_list
    else:
        return _simp_helper(new_list, mem)


def _is_float(string):
    if not isinstance(string, (str, int, float)):
        return False
    try:
        float(string)
        return True
    except ValueError:
        return False


def replace_var(expression, old_var, new_var):
    """Replaces old variable in expression with a new one, without changing built in functions.
    Args:
        expression (string): The expression that should be simplified.
        old_var (string): Old variable in expression
        new_var (string): New variable to be used
    Returns:
        string: updated expression
    """
    return _replace_helper(expression, old_var, new_var, 0)


def _replace_helper(expression, old_var, new_var, index):
    """Help function for replace_var."""
    if index == len(COMMON_OPERATORS):
        return expression.replace(old_var, new_var)
    else:
        sub_list = expression.split(COMMON_OPERATORS[index])
        for place in range(0, len(sub_list)):
            sub_list[place] = _replace_helper(sub_list[place], old_var, new_var, index + 1)
        return COMMON_OPERATORS[index].join(sub_list)


def _interp_expr(expression, variable, value=None):
    interp_expr = []
    curr = ""  # used to store numbers and common functions in one place
    prev_char = "{"  # signifies "character" before the first one
    add_par = 0
    to_check = replace_var(expression, variable, "X").replace("[", "(").replace("]", ")")
    for index in range(0, len(to_check)):
        char = to_check[index]
        if char == "(" and prev_char in "0123456789X" or char in "0123456789X" and prev_char == ")":
            while add_par > 0:
                interp_expr.append(")")
                add_par -= 1
            interp_expr.append("*")
        if char in "".join(COMMON_OPERATORS):
            if prev_char not in "".join(COMMON_OPERATORS).lower() + "{":
                if prev_char in "0123456789X":
                    while add_par > 0:
                        interp_expr.append(")")
                        add_par -= 1
                    interp_expr.append("*")
            curr += char
            if curr in COMMON_OPERATORS and (index + 1 == len(to_check) or (curr + to_check[index + 1]) not in
                                             COMMON_OPERATORS):
                interp_expr.append(curr)
                if not index + 1 == len(to_check) and not to_check[index + 1] == "(":
                    interp_expr.append("(")
                    add_par += 1
                curr = ""
                prev_char = "}"  # signifies a common function
                continue
        elif char in "0123456789.":
            if prev_char == "X":
                interp_expr.append("^")
            curr += char
            if index + 1 == len(to_check) or not to_check[index + 1] in "0123456789.":
                interp_expr.append(curr)
                curr = ""
        elif char == "X":
            if prev_char in "1234567890X":
                interp_expr.append("*")
            if value is not None:
                interp_expr.append(str(value))
            else:
                interp_expr.append(variable)
        elif char in "+-*/()^":
            if not char == "^":
                while add_par > 0:
                    interp_expr.append(")")
                    add_par -= 1
            interp_expr.append(char)
            curr = ""
        prev_char = char
    while add_par > 0:
        interp_expr.append(")")
        add_par -= 1
    return interp_expr


def evaluate(expression, variable, value):
    """Evaluates the expression with given variable at value.
    Args:
        expression (string): The expression that should be simplified.
        variable (string): Used variable in expression
        value (float, int): Value where function should be evaluated
    Returns:
        float: evaluation of function.
    Raises:
        TypeError: expression not recognisable as algebraic expression or variable name equal to protected function"""
    if not isinstance(value, (float, int)):
        raise TypeError("Input value must be float or int")
    _check_expression(expression, variable)
    interp = _interp_expr(expression, variable, value)
    for index in range(0, len(interp)):
        thing = interp[index]
        if thing == "^":
            interp[index] = "**"
        elif thing in COMMON_OPERATORS:
            interp[index] = "math." + thing
    try:
        return float(eval("".join(interp)))
    except ZeroDivisionError:
        raise ZeroDivisionError("float division by zero for expression: " + expression + " at " + variable + " = " +
                                str(value))


def _check_expression(expr, variable):
    """Checks whether the expr is a valid string expression of an arithmetic expression"""
    if not isinstance(expr, str):
        raise TypeError("Expression must be a string")
    if not isinstance(variable, str):
        raise TypeError("Variable must be a string")
    for char in variable:
        if char in ".0123456789()[]+-*^/{}\\\\":
            raise TypeError("Invalid variable " + variable)
    for thing in ["{", "}"]:
        if thing in expr:
            raise TypeError("Invalid character " + thing + " in expression " + expr)
    simple_expr = expr
    for op in COMMON_OPERATORS:
        if op == variable.lower():
            raise TypeError("Invalid variable name " + variable + ". Protected operator.")
        simple_expr = simple_expr.replace(op, "}")  # } signifies a common operator
    simple_expr = simple_expr.replace(variable, "x").replace(" ", "")
    parenthesis_list = []
    prev_char = "{"  # { signifies the "character" before the first character
    dot_allowed = True
    for char in simple_expr:
        if char not in ".0123456789()[]+-*^/x{}":
            raise TypeError("Invalid character: " + char + " in expression " + expr)
        if char in "([":
            parenthesis_list.append(char)
        elif char in ")]":
            if len(parenthesis_list) == 0:
                raise TypeError("Non matching parenthesis: " + char + " in expression " + expr)
            if char == ")":
                if not parenthesis_list.pop() == "(":
                    raise TypeError("Non matching parenthesis: [ ... )" + " in expression " + expr)
            else:
                if not parenthesis_list.pop() == "[":
                    raise TypeError("Non matching parenthesis: ( ... ]" + " in expression " + expr)
            if prev_char in ".+-*/^}":
                raise TypeError("Invalid syntax: " + prev_char.replace("}", "...") + char + " in expression " +
                                expr)
            elif prev_char in "([":
                raise TypeError("Empty parenthesis: " + char + prev_char + " in expression " + expr)
        elif char in "^*/" and prev_char == "{":
            raise TypeError("Invalid starting operator: " + char + " in expression " + expr)
        elif char in "+-*/^" and prev_char in "+-*/^([}.":
            raise TypeError("Invalid operator usage: " + prev_char.replace("}", "...") + char + " in expression "
                            + expr)
        elif char == ".":
            if not dot_allowed:
                raise TypeError("Two decimal points in one number in expression: " + expr)
            else:
                dot_allowed = False
        if char in "+-*^/()[]x}":
            dot_allowed = True
        prev_char = char
    if simple_expr[-1] in "+-*/^}.":
        raise TypeError("Invalid ending operator in expression " + expr)
    if not len(parenthesis_list) == 0:
        raise TypeError("Missing " + str(len(parenthesis_list)) + " ending parenthesis" + " in expression " + expr)


print(simplify("1*2x-x+x^2", "x"))
