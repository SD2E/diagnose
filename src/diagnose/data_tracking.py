"""
storing information about data processing in the data files

tested for: py 3.5

:author: anastasia deckard (anastasia.deckard@geomdata.com)
:created: 2014 07 28
:copyright: (c) 2020, GDA
:license: see LICENSE for more details
"""

import os
from datetime import datetime


def get_doc_info_string(file, cmd, args):
    """
    Function to get doc info string including information on which script was run, what system it was run on,
    what cmd was run, and which params were passed to the script.

    ToDo: What is this doc_for_file thing?
    doc_for_file = data_tracking.get_doc_info_string(__file__, sys.argv, vars(parser.parse_args()))

    :param file: File run to get output
    :param cmd: Terminal command used to run code
    :param args: Either none or parser arguments ToDo: I'm not sure what this is
    :return: doc_for_file: list of strings with information about code run
    """

    script_version = datetime.fromtimestamp(os.path.getmtime(file)).strftime("%Y %m %d %H:%M:%S")
    script_executed = datetime.today().strftime("%Y %m %d %H:%M:%S")
    if args is not None:
        arg_list = args.items()
    else:
        arg_list = []

    doc_for_file = [
        "### script: " + os.path.basename(file) + " version: " + script_version,
        # "# run by:   " + os.getlogin(),
        "# run on:   " + script_executed,
        "# cmd:      " + ' '.join(cmd),
        "# params:   " + '\n#           '.join([str(x) + ": " + str(y) for x, y in arg_list]),
        "#\n"]

    return '\n'.join(doc_for_file)


def get_data_file_comments(filename, comment='#'):
    """
    get comment lines from a data file

    :param filename: path to file
    :param comment: default is "#", symbol for comments
    :return: list of lines with comments
    """
    with open(filename, 'r') as file_handle:
        file_tmp = file_handle.read()
        file_tmp = file_tmp.splitlines()
        file_comments = [line for line in file_tmp if line.startswith(comment)]
        file_comments += ["#\n"]

    return '\n'.join(file_comments)


def add_suffix_to_file_path(input_file_path, suffix_ext):
    """
    adds new suffix and extension to a file path

    :param input_file_path: original file path
    :param suffix_ext: new suffix and extension, e.g. _annot.txt
    :return: output_file_path: new filename name with suffix
    """

    input_file_name, input_file_ext = os.path.splitext(os.path.basename(input_file_path))
    output_file_path = input_file_path.replace(input_file_ext, suffix_ext)

    return output_file_path


def make_output_dir_timestamp(output_dir, base_name):
    """
    create a new directory with timestamp information

    :param output_dir: original output directory
    :param base_name: base name for new output directory
    """

    datetime_stamp = datetime.now().strftime('%Y%m%d%H%M%S')
    run_id = base_name + '_' + datetime_stamp

    sub_output_dir = os.path.join(output_dir, run_id)
    if not os.path.exists(sub_output_dir):
        os.makedirs(sub_output_dir, exist_ok=True)

    return sub_output_dir
