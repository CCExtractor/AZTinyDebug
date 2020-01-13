import os
from datetime import datetime


class ConsoleReporter:
    """Reporter class, reports program execution results to console."""

    def __init__(self, results):
        self.results = results

    def print_results(self):
        os.system('')  # Workaround to display console colors in the windows command prompt
        code_info = self.results["code_info"]

        if "filename" in code_info:
            print("\033[92mDisplaying results for file {}, running function {}({}).\033[0m".format(code_info["filename"], code_info["function_name"],
                                                                                                   ", ".join(str(arg) for arg in code_info["function_args"])))
        else:
            print("\033[92mDisplaying results for function {}({}).\033[0m".format(code_info["function_name"], ", ".join(str(arg) for arg in code_info["function_args"])))

        print("\033[92mExecution log:\033[0m")
        execution_log = self.results["execution_log"]
        for step in execution_log:
            print("\033[95m{} - Step {}, line {} - executed {} times so far, total time so far {}s, average time so far {}s\033[0m".format(
                datetime.utcfromtimestamp(step["timestamp"]).strftime('%Y-%m-%d %H:%M:%S'), step["step"], step["line_num"], step["line_runtime"]["times_executed"],
                "{0:0.5f}".format(step["line_runtime"]["total_time"]), "{0:0.5f}".format(step["line_runtime"]["total_time"] / step["line_runtime"]["times_executed"])))

            print("\033[94m", end="")
            if step["actions"]:
                is_first = True
                for action in step["actions"]:
                    if is_first:
                        is_first = False
                    else:
                        print(", ", end="")

                    action_desc = "illegal action"
                    if action["action"] == "init_var":
                        action_desc = "variable '{}' created and initiated with {}".format(action["var"], action["val"])
                    elif action["action"] == "change_var":
                        action_desc = "variable '{}' changed from {} to {}".format(action["var"], action["prev_val"], action["new_val"])
                    elif action["action"] == "list_add":
                        action_desc = "{}[{}] appended with value {}".format(action["var"], action["index"], action["val"])
                    elif action["action"] == "list_change":
                        action_desc = "{}[{}] changed from {} to {}".format(action["var"], action["index"], action["prev_val"], action["new_val"])
                    elif action["action"] == "list_remove":
                        action_desc = "{}[{}] removed".format(action["var"], action["index"])
                    elif action["action"] == "dict_add":
                        action_desc = "key {} added to {} with value {}".format(action["key"], action["var"], action["val"])
                    elif action["action"] == "dict_change":
                        action_desc = "value of key {} in {} changed from {} to {}".format(action["key"], action["var"], action["prev_val"], action["new_val"])
                    elif action["action"] == "dict_remove":
                        action_desc = "key {} removed from {}".format(action["key"], action["var"])
                    print(action_desc, end="")
                print(".\033[0m")

        print("\033[92mReturned value: {}\033[0m".format(self.results["returned_value"]))
        print()

        print("\033[92mVariable change analysis:\033[0m")
        variable_history = self.results["variable_history"]
        print("\033[95m", end="")
        for var in variable_history:
            print("Variable '{}' (type {}), initiated in step {}, line {}.".format(var["var"], var["type"], var["val_history"][0]["step"], var["val_history"][0]["line"]))
            if var["range"]:
                print("Value range: {} - {}. ".format(var["range"][0], var["range"][1]), end="")
            print("Value history: ", end="")
            print(", ".join("step {} line {}: {}".format(change["step"], change["line"], change["value"]) for change in var["val_history"]))
            print()
        print("\033[0m", end="")

        print("\033[92mLine runtime analysis:\033[0m")
        line_history = self.results["line_history"]
        print("\033[95m", end="")
        for line in line_history:
            print("Line {}: executed {} times, total runtime {}s, average runtime {}s".format(line["line_num"], line["times_executed"], "{0:0.5f}".format(line["total_time"]),
                                                                                              "{0:0.5f}".format(line["total_time"] / line["times_executed"])))
        print("\033[0m", end="")
