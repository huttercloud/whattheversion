#!/usr/bin/env python3

"""
    lambda function handler for git-api requests
"""

# if the lambda function is executed with sam locally the 
# git layer paths need to be setup manually!
import os
if os.getenv('AWS_SAM_LOCAL') == 'true':
    os.environ['PATH'] = ':'.join(['/opt/git/bin', os.environ.get('PATH')])
    os.environ['LD_LIBRARY_PATH'] = ':'.join(['/opt/git/lib', os.environ.get('LD_LIBRARY_PATH')])


from whattheversion import return_hallo
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
