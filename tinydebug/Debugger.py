import sys
import copy
import time


class Debugger:
    """
    Debugger class.

    Receives a function object and function arguments in a list, runs the function while tracing it and produces results.
    """

    def __init__(self, func, func_args):
        self.func = func
        self.func_name = func.__name__
        self.func_args = func_args

        self.curr_line = None
        self.prev_variables = {}
        self.variable_history = {}
        self.line_history = {}
        self.prev_time = time.time()
        self.step = 1

        self.results = {"code_info": {"function_name": self.func_name, "function_args": self.func_args}, "execution_log": [], "variable_history": [], "line_history": []}

    def run(self):
        """
        Runs the function, and traces it.
        :return: Analyzed tracing results.
        """
        sys.settrace(self.__trace_calls)
        self.prev_time = time.time()
        self.results["returned_value"] = self.func(*self.func_args)
        sys.settrace(None)

        self.results["variable_history"] = [var_obj.get_dict() for var_obj in self.variable_history.values()]
        self.results["line_history"] = [line_obj.get_dict() for line_obj in self.line_history.values()]

        return self.results

    def __trace_calls(self, frame, event, arg):
        """Trace function, used in sys.settrace."""
        self.curr_line = frame.f_lineno
        if frame.f_code.co_name == self.func_name:
            return self.__trace_lines

    def __trace_lines(self, frame, event, arg):
        """Runs every line executed in the traced function, and analyzes the changes in variables."""
        curr_execution_log = {"step": self.step, "timestamp": time.time(), "line_num": self.curr_line, "actions": []}
        self.results["execution_log"].append(curr_execution_log)

        if self.curr_line not in self.line_history:
            self.line_history[self.curr_line] = Line(self.curr_line)
        self.line_history[self.curr_line].run_line(time.time() - self.prev_time)
        curr_execution_log["line_runtime"] = self.line_history[self.curr_line].get_dict()

        self.is_first_print_for_this_line = True
        current_variables = frame.f_locals
        for var, val in current_variables.items():
            if var not in self.prev_variables:
                curr_execution_log["actions"].append({"action": "init_var", "var": var, "val": val})
                self.variable_history[var] = Variable(var, self.curr_line, self.step, copy.deepcopy(val))
            elif self.prev_variables[var] != val:
                prev_val = self.prev_variables[var]
                if isinstance(prev_val, list) and isinstance(val, list):
                    self.__compare_lists(var, prev_val, val)
                elif isinstance(prev_val, dict) and isinstance(val, dict):
                    self.__compare_dictionaries(var, prev_val, val)
                else:
                    curr_execution_log["actions"].append({"action": "change_var", "var": var, "prev_val": prev_val, "new_val": val})
                self.variable_history[var].add_value(self.step, self.curr_line, copy.deepcopy(val))

        self.prev_variables = copy.deepcopy(current_variables)
        self.prev_time = time.time()
        self.curr_line = frame.f_lineno
        self.step += 1

    def __compare_lists(self, var, prev_val, val):
        """Utility function that compares two lists, and adds the changes to the execution log."""
        curr_execution_log = self.results["execution_log"][-1]

        for i in range(min(len(val), len(prev_val))):
            if val[i] != prev_val[i]:
                curr_execution_log["actions"].append({"action": "list_change", "var": var, "index": i, "prev_val": prev_val[i], "new_val": val[i]})
        if len(val) > len(prev_val):
            for i in range(len(prev_val), len(val)):
                curr_execution_log["actions"].append({"action": "list_add", "var": var, "index": i, "val": val[i]})
        if len(val) < len(prev_val):
            for i in range(len(val), len(prev_val)):
                curr_execution_log["actions"].append({"action": "list_remove", "var": var, "index": i})

    def __compare_dictionaries(self, var, prev_val, val):
        """Utility function that compares two dictionaries, and adds the changes to the execution log."""
        curr_execution_log = self.results["execution_log"][-1]

        for elem in val:
            if elem not in prev_val:
                curr_execution_log["actions"].append({"action": "dict_add", "var": var, "key": elem, "val": val[elem]})
            elif prev_val[elem] != val[elem]:
                curr_execution_log["actions"].append({"action": "dict_change", "var": var, "key": elem, "prev_val": prev_val[elem], "new_val": val[elem]})
        for elem in prev_val:
            if elem not in val:
                curr_execution_log["actions"].append({"action": "dict_remove", "var": var, "key": elem})


class Variable:
    """
    Represents a variable, used in the Debugger class.
    Stores variable name, and log of values by line and step number.
    """

    def __init__(self, name, init_line, init_step, init_val):
        self.name = name
        self.line_value = []
        self.add_value(init_step, init_line, init_val)

    def add_value(self, step, line, value):
        """
        Add a value to the variable's log.

        :param int step: Step number this value was set in while running the program.
        :param int line: Line number this value was set in while running the program.
        :param value: Value of this variable in the corresponding step and line.
        """
        self.line_value.append({"step": step, "line": line, "value": value})

    def get_type(self):
        """
        Returns the variable's type, if it stayed constant throughout its lifetime. Otherwise, "undefined".
        """
        init_val = self.line_value[0]["value"]
        t = type(init_val)
        for lv in self.line_value:
            if type(lv["value"]) != t:
                return "undefined"  # Undefined type - changed during execution
        return t

    def get_range(self):
        """
        Returns the variable's range of values while running the program, if its type is int or float. Otherwise, None.
        """
        if self.get_type() in [int, float]:
            values = [lv["value"] for lv in self.line_value]
            return [min(values), max(values)]

    def get_dict(self):
        """
        Returns a dictionary representation of the variable, to store for use by reporters.
        """
        return {"var": self.name, "type": str(self.get_type()), "range": self.get_range(), "val_history": self.line_value}


class Line:
    """
    Represents a line, used in the Debugger class.
    Stores line number, number of times the line was executed and total time spent running the line.
    """

    def __init__(self, line_num):
        self.line_num = line_num
        self.times_executed = 0
        self.total_time = 0

    def run_line(self, time):
        """
        Stores an execution of the line, and updates the relevant variables.

        :param float time: Time in seconds the line took to execute.
        """
        self.times_executed += 1
        self.total_time += time

    def get_dict(self):
        """
        Returns a dictionary representation of the line, to store for use by reporters.
        """
        return {"line_num": self.line_num, "times_executed": self.times_executed, "total_time": self.total_time}
