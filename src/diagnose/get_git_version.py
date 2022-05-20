"""
Script to get Git Version Information and save it to file
(Should only be used before deployment to TACC)

:author: Tessa Johnson (tessa.johnson@geomdata.com)
:created: 2021
:copyright: (c) 2021, GDA
:license: see LICENSE for more details
"""

import os


def get_git_version():
    """
    function to write the git version information to a .txt file
    """

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

    with open('git_version.txt', 'w') as file:
        file.write(version_info)
        file.close()


if __name__ == '__main__':
    get_git_version()
