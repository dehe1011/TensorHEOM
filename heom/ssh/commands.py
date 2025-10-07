from .slurm import slurmShell, slurmStatus

def commandsForSubmission(submissionParams, qpyName, path):
    """create commands for job submission

        params:
            submissionParams (dict):
                parameters for submissoin
                submissoinParams['schedulerName']: job scheduler name
                submissionParams['numNodes'] (int): the number of nodes
                submissionParams['cpusPerTask'] (int):
                    the number of cpus per task
                submissionParams['maxTime'] (str):
                    maximum time for calculation in the form 'D-H:MM:SS'
                submissionParams['others'] (str): user-defined parameters
                submissionParams['venvPath']:
                    path of venv (virtual environment)
            qpyName (str): name of input file (QPY format)
            path (str): path for files to submit
                
        returns:
            commands (str): commands for submission
    """
    SCRIPTNAME = 'run.py'
    SHELLNAME = 'job.sh'
    TASKSPERNODE = 1

    submissionParams['tasksPerNode'] = TASKSPERNODE

    pythonScript = 'import sys\n'
    pythonScript += 'from heom.cui.run import run_cui\n\n'
    pythonScript += 'run_cui(sys.argv[1], sys.argv[2])\n'
    pythonScript += 'EOF1\n'

    if submissionParams['schedulerName'] == 'slurm':
        shell, submissionCommand = \
            slurmShell(submissionParams, qpyName, SCRIPTNAME)
    
    shell += 'EOF2'


    commands = 'cd ' + path + ';'
    commands += 'cat << "EOF1" > ' + SCRIPTNAME + ';'
    commands += 'cat << "EOF2" > ' + SHELLNAME + ';'
    commands += submissionCommand + ' ' + SHELLNAME + '\n'
    commands += pythonScript
    commands += shell

    return commands

def getStatus(schedulerName, jobID, client):
    """return whether the job with jobID is completed

        params:
            schedulerName (str): job scheduler name
            jobID: job ID of the simulation
            client (paramiko.client.SSHClient): client for ssh connection

        returns:
            bool: whether the job is completed
    """

    if schedulerName == 'slurm':
        return slurmStatus(jobID, client)