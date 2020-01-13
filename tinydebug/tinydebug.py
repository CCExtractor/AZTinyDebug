import argparse
from .Debugger import Debugger
from .ConsoleReporter import ConsoleReporter
from .TestSuite import TestSuite
from .VideoReporter import VideoReporter
from .util import func_from_file, read_results, write_results
from pathlib import Path


def parse_func_arg(arg):
    try:
        return int(arg)
    except ValueError:
        try:
            return float(arg)
        except ValueError:
            return arg


def main():
    parser = argparse.ArgumentParser(description="Python code analyzer and debugger created by AlephZero for CCExtractor, Google Code-In 2019.",
                                     formatter_class=argparse.RawTextHelpFormatter)

    debug_group = parser.add_argument_group(title="Analysis and Debugging", description="Analyzing and debugging Python programs.")
    debug_group.add_argument("--debug", help=".\n".join(["Path of a *.py file to debug", "Example: \"--debug script.py\" will run the file script.py."]), metavar="FILE")
    debug_group.add_argument("--func", help=".\n".join(
        ["If --debug FILE is present, optionally provide the name of a function to debug and function arguments", "(defaults to main with no arguments)",
         "Example: \"--func foo 1 \"Hello World\" 2\" will run foo(1, \"Hello World\", 2)."]), nargs='+', default=["main"], metavar=("FUNC", "PARAMETER"))
    debug_group.add_argument("--output", help=".\n".join(["If --debug FILE is present, optionally provide a file path to save analysis results to",
                                                          "Results are saved in video format if the extension is *.mp4 or *.gif, or in an internal format otherwise",
                                                          "(if --output FILE is not provided, the results are printed to console)",
                                                          "Example: \"--output result.tinydebug\" saves the results in an internal format to the file result.tinydebug",
                                                          "Example: \"--output video.mp4\" generates a video and saves it as video.mp4."]), metavar="FILE")

    parse_group = parser.add_argument_group(title="Parsing and Reporting", description="Parsing analysis results and reporting them in console in human-readable form.")
    parse_group.add_argument("--parse", help=".\n".join(["Path of a file generated by this program, to print in human-readable form",
                                                         "Example: \"--parse result.tinydebug\" will parse the results saved in result.tinydebug, and print them to console."]),
                             metavar="FILE")

    parser.add_argument("--test", help="\n".join(["Run the test suite, containing various algorithms.",
                                                  "If OUTPUT_DIRECTORY is present the results will be written there in separate files, otherwise they will be printed to console."]),
                        nargs="?", metavar="OUTPUT_DIRECTORY", const=False)

    video_group = parser.add_argument_group(title="Video Reporting", description="Generating a video displaying the program's flow and execution, given a result file.")
    video_group.add_argument("--video", help="\n".join(["Generate a video file with the program flow.",
                                                        "Example: \"--video prog.py foo result.tinydebug video.mp4\" creates a video of the results of running the function foo in prog.py,",
                                                        "assuming they were already analyzed using --debug and saved in result.tinydebug, and saves the video as video.mp4."]),
                             metavar=("PYTHON_FILE", "FUNCTION", "ANALYSIS_FILE", "VIDEO_OUTPUT"), nargs=4)

    args = parser.parse_args()

    if args.test is not None:
        TestSuite.run_all_tests(args.test)
    elif args.debug:
        debug_file_path = args.debug

        func_name = args.func[0]
        func = func_from_file(debug_file_path, func_name)
        func_args = [parse_func_arg(arg) for arg in args.func[1:]]

        debugger = Debugger(func, func_args)
        results = debugger.run()

        output_file_path = args.output

        if output_file_path:
            extension = Path(args.output).suffix
            if extension == ".mp4" or extension == ".gif":
                reporter = VideoReporter(func, results)
                reporter.generate_video(output_file_path)
            else:
                write_results(output_file_path, results)
        else:
            reporter = ConsoleReporter(results)
            reporter.print_results()
    elif args.parse:
        reporter = ConsoleReporter(read_results(args.parse))
        reporter.print_results()
    elif args.video:
        reporter = VideoReporter(func_from_file(args.video[0], args.video[1]), read_results(args.video[2]))
        reporter.generate_video(args.video[3])
    else:
        print("Whoops, you didn't provide any arguments! Run \"tinydebug --help\" for more info on how to use this program.")
