"""Deprecated.
    This module is kept for potential future use.

    Users can enter parameter values (password, OTP, etc.) interactively.
"""

import socket
import paramiko
import getpass

def handler(title, instructions, prompt_list):
    answers = []

    for pr in prompt_list:
        query = pr[0]
        ans = getpass.getpass(query)

        answers.append(ans)

    return answers

def getClient(hostname, username):
    """get Client of paramiko

        args:
            hostname (str): server name to connect to
            username (str): user name

        returns:
            client (paramiko.client.SSHClient)
    """

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, 22))
    ts = paramiko.Transport(sock)
    ts.start_client()
    ts.auth_interactive(username, handler)

    client._transport = ts

    return client