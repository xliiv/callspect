import os
import sys
import textwrap

USAGE = textwrap.dedent("""
Usage example:

$ callspect ~/path-to-my-file/callspect.txt
""")


def run():
    if len(sys.argv) != 2:
        print("Missing system variable CALLSPECT_DATA_PATH")
        print(USAGE)
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.exists(path):
        print("File does not exists: {}".format(path))
        print(USAGE)
        sys.exit(2)

    from callspect import config
    config.config_dict = {
        'CALLSPECT_DATA_PATH': path,
    }
    from callspect.app import app  # this MUST be after config.config_dict set
    app.run()
