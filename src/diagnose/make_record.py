"""
Helper functions for producing record.json

:author: Tessa Johnson (tessa.johnson@geomdata.com)
:created: 2020
:copyright: (c) 2020, GDA
:license: see LICENSE for more details
"""

import os
import hashlib
from datetime import datetime


def make_hash(file_path):
    """
    make a md5 hash for a file

    :param file_path: path to file
    :return: hash: md5 hash for a file
    """
    md5 = hashlib.md5()

    with open(file_path, 'rb') as file:
        # read in binary. chunks in case of big files
        while True:
            data = file.read(65536)
            if not data:
                break
            md5.update(data)

    hash_val = md5.hexdigest()
    print("MD5: {0}".format(hash_val))

    return hash_val


def make_hashes_for_files(file_list):
    """
    for each file in a directory, make path, call hash, and make a record with file name and hash

    :param file_list: list of file records [{"name": x}, ...]
    :return: list of file records [{"name": str, "hash_md5": str}, ...]
    """

    for file in file_list:
        hash_val = make_hash(file['name'])
        file['hash_md5'] = hash_val

    return file_list


def get_dev_git_version():
    """
    Function to get git version for debugging

    :return: version_info: git version
    """

    # Used for deploying code to TACC
    version_path = '/diagnose/git_version.txt'
    if os.path.exists(version_path):
        with open(version_path, 'r') as file:
            version_info = file.read()
            file.close()

    # Used for running code locally
    else:
        # need to be within git directory
        git_dir = os.path.dirname(os.path.abspath(__file__))

        stream = os.popen('cd {0:s}; git rev-parse --abbrev-ref HEAD'.format(git_dir))
        branch = stream.read().strip()
        if branch.startswith('-bash:'):
            branch = "NA"

        stream = os.popen('cd {0:s}; git show -s --format="gitinfo: %h %ci"'.format(git_dir))
        commit = stream.read().strip()
        if commit.startswith('gitinfo:'):
            commit = commit.replace('gitinfo: ', '')
        else:
            commit = "NA"

        version_info = branch + ' ' + commit

    return version_info


def make_product_record(out_dir, files, data_path, merge_file):
    """
     Function to make a record about each run of the code

    :param out_dir: Output directory
    :param files: List of file names associated with the output
    :param data_path:  Path to the data
    :param merge_file: location of separate metadata file (if applicable)
    :return: record: a dictionary with information about each run of the diagnose code (git version, datetime, etc.)
    """

    datetime_stamp = datetime.now().strftime('%Y%m%d%H%M%S')

    version_info = get_dev_git_version()

    for file in files:
        file['name'] = os.path.basename(file['name'])

    record = {
        "perform_metrics version": version_info,
        "date_run": datetime_stamp,
        "output_dir": out_dir,
        "data_path": data_path,
        "merge_files": merge_file,
        "files": files,
    }

    return record

if __name__ == '__main__':
    get_dev_git_version()