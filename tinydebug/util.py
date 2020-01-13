import importlib.util
import pickle


def func_from_file(file_path, func_name):
    module_spec = importlib.util.spec_from_file_location("debugmodule", file_path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    func = getattr(module, func_name)
    return func


def write_results(file_path, results):
    with open(file_path, "wb") as f:
        pickle.dump(results, f)


def read_results(file_path):
    with open(file_path, "rb") as f:
        return pickle.load(f)
