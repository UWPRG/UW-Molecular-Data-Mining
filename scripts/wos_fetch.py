#!/usr/bin/env python

import click

from wos import WosClient
import wos.utils

@click.command()
@click.option('-o', '--output_file', 'output_file', type=str, required=True,
        help='name of the output file')
@click.option('-u', '--username', 'username', type=str, required=True,
        help='username for accessing the web of science API')
@click.option('-p', '--password', 'password', type=str, required=True,
        help='password for accessing the web of science API')
def wos_fetch(output_file, username, password):
    with WosClient(username, password) as client:
        print(wos.utils.query(client, 'AU=Beckner Wesley'))


if __name__ == '__main__':
    wos_fetch()
