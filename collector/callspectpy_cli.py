import argparse
import os
import sys

from callspectpy import trace2file


OUTPUT_FILE = 'callspect.txt'


def _get_parser():
    arg_parser = argparse.ArgumentParser(
        description='Extracts data from python script required by `callspect` program'
    )
    arg_parser.add_argument('-i', '--input-script', required='True', help='Python script to be traced: eg: "my-script.py"')
    arg_parser.add_argument(
        '-o', '--output-file', default=OUTPUT_FILE,
        help='File where traces are stored (default: {})'.format(OUTPUT_FILE),
    )
    return arg_parser.parse_args()


def run():
    args = _get_parser()
    # make input-script imporatable
    sys.path.insert(0, os.getcwd())

    try:
        with open(args.input_script) as fptr:
            script_content = fptr.read()
    except Exception as e:
        print("Can't get content of file: {!r}".format(args.input_script))
        sys.exit(1)

    globals()['__name__'] = '__main__'

    # TODO: add running command with pipe: cat file.json | python -m json.tool
    # TODO: add running server: python -m http.server
    code = compile(script_content, args.input_script, 'exec')
    with trace2file(args.output_file):
        exec(code, globals())
