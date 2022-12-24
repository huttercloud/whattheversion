#!/usr/bin/env python3

"""
    lambda function handler for git requests
"""

from whattheversion import return_hallo
import os
import subprocess

# setup git paths before importing
os.environ['PATH'] = ':'.join(['/opt/git/bin', os.environ.get('PATH')])
os.environ['LD_LIBRARY_PATH'] = ':'.join(['/opt/git/lib', os.environ.get('LD_LIBRARY_PATH')])

print(os.environ['PATH'])
print(os.environ['LD_LIBRARY_PATH'])
# os.environ["GIT_PYTHON_REFRESH"] = "quiet"
# os.environ["GIT_PYTHON_GIT_EXECUTABLE"] = "/var/task/bin/git"

# print(os.environ)
print(os.environ)
print(os.listdir('/opt'))

from git.cmd import Git



def handler(event, context):
    print('weifniognioewnfonewiofnweionoifnweiofnionoi')
    g = Git()
    tags = list()
    # retrieve all tags, last element in list is the newest tag
    for r in g.ls_remote('--tags', f'https://github.com/clinton-hall/nzbToMedia').split('\n'):
        ti = r.find('refs/tags/') + len('refs/tags/')
        tags.append(r[ti:])
    
    return return_hallo(tags)
