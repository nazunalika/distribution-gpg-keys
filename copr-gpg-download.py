#!/usr/bin/python3

from copr import create_client2_from_params
import requests
import argparse
import sys
from argparse import RawTextHelpFormatter

parser = argparse.ArgumentParser(description='Download GPG keys for COPR projects.', formatter_class=RawTextHelpFormatter)
parser.add_argument('-f', '--file', action='store',
                   help='store keys to a file instead of printing to stdout')
parser.add_argument('--feurl', action='store', default='http://copr.fedorainfracloud.org/',
                   help='use this url as baseurl to frontend instead of\nhttp://copr.fedorainfracloud.org/')
parser.add_argument('--beurl', action='store', default='https://copr-be.cloud.fedoraproject.org',
                   help='use this url as baseurl to backend instead of\nhttps://copr-be.cloud.fedoraproject.org')
parser.add_argument('--user', action='store',
                   help='only download gpg keys for projects of this user')
parser.add_argument('--project', action='store',
                   help='only download gpg keys for projects of this name')
parser.add_argument('project_ids', metavar='ID', type=int, nargs='*',
                   help='project id for which the gpg keys should be retrieved\n(by default all)')

args = parser.parse_args()

be_url_tmpl = args.beurl+'/results/{username}/{projectname}/pubkey.gpg'

cli = create_client2_from_params(root_url=args.feurl)

if args.file:
    output_file = open(args.file, 'w')
else:
    output_file = None

def get_gpg(project):
    url = be_url_tmpl.format(**{'username': project.owner, 'projectname': project.name})
    r = requests.get(url)
    return r.text

def gpg_out(gpg):
    if output_file:
        output_file.write(gpg)
    else:
        print(gpg)

if args.project_ids:
    for project_id in args.project_ids:
        project = cli.projects.get_one(project_id)
        gpg_out(get_gpg(project))
    sys.exit(0)

kwargs = {}

if args.user:
    kwargs['owner'] = args.user
if args.project:
    kwargs['name'] = args.project

_offset = 0
_limit = 100

while True:
    projects = cli.projects.get_list(offset=_offset, limit=_limit, **kwargs)
    if not projects:
        break
    for project in projects:
        gpg_out(get_gpg(project))
    _offset += _limit