from tinydebug.Debugger import Debugger
from tinydebug.ConsoleReporter import ConsoleReporter
from tinydebug.util import func_from_file, write_results
from pathlib import Path
import json
import os


def run_all_tests(output_directory):
    if output_directory:
        output_directory = Path(output_directory)
        if not output_directory.is_dir():
            output_directory.mkdir()

    test_suite_dir = Path(os.path.dirname(__file__))
    with open(test_suite_dir / "test_config.json") as f:
        test_config = json.load(f)
        for test_obj in test_config["test_files"]:
            file_path, func_name, func_args = Path(test_obj["file"]), test_obj["func"], test_obj["args"]

            func = func_from_file(test_suite_dir / file_path, func_name)
            debugger = Debugger(func, func_args)
            results = debugger.run()

            if output_directory:
                write_results(output_directory / (func_name + ".tinydebug"), results)
            else:
                reporter = ConsoleReporter(results)
                reporter.print_results()
                print()
