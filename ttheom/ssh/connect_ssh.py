"""SSH connection utilities for HPC clusters."""
import socket
import paramiko

def handlerWithValues(password, otp):
    """Create an interactive SSH authentication handler.

    Parameters
    ----------
    password : str
        SSH password.
    otp : str
        One-time password for two-factor authentication.

    Returns
    -------
    callable
        Handler function compatible with ``paramiko``'s interactive auth.
    """
    def handler(title, instructions, prompt_list):
        answers = []

        for pr in prompt_list:
            query = pr[0]
            if 'otp' in query.lower():
                answers.append(otp)
            elif 'password' in query.lower():
                answers.append(password)
            else:
                answers.append("")

        return answers
    return handler

def getClient(hostname, username, password, otp):
    """Open an authenticated SSH connection and return the client.

    Parameters
    ----------
    hostname : str
        Server hostname or IP address.
    username : str
        SSH username.
    password : str
        SSH password.
    otp : str
        One-time password for two-factor authentication.

    Returns
    -------
    paramiko.client.SSHClient
        Authenticated SSH client connected to ``hostname``.
    """

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, 22))
    ts = paramiko.Transport(sock)
    ts.start_client()
    ts.auth_interactive(username, handlerWithValues(password, otp))

    client._transport = ts

    return client
