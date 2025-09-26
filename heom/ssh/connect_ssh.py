"""For JUSTUS2

"""
import socket
import paramiko

def handlerWithValues(password, otp):
    def handler(title, instructions, prompt_list):
        answers = []

        for pr in prompt_list:
            query = pr[0]
            if query == 'Your OTP:':
                answers.append(otp)
            elif query == 'Password:':
                answers.append(password)

        return answers
    return handler

def getClient(hostname, username, password, otp):
    """get Client of paramiko

        params:
            hostname (str): server name to connect to
            username (str): user name
            password (str): password
            otp (str): one-time password

        returns:
            client (paramiko.client.SSHClient)
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