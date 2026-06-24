from .slurm import slurmShell, slurmStatus

def commandsForSubmission(submissionParams, qpyName, path):
    """Build the shell commands needed to submit a job to an HPC cluster.

    Parameters
    ----------
    submissionParams : dict
        Submission parameters with the following keys:

        ``'schedulerName'`` : str
            Job scheduler name (e.g. ``'slurm'``).
        ``'numNodes'`` : int
            Number of compute nodes.
        ``'cpusPerTask'`` : int
            Number of CPU cores per task.
        ``'maxTime'`` : str
            Wall-clock time limit in the form ``'D-H:MM:SS'``.
        ``'others'`` : str
            Additional scheduler directives.
        ``'venvPath'`` : str
            Path to the Python virtual environment.

    qpyName : str
        Name of the input QPY file.
    path : str
        Remote directory where the files will be placed.

    Returns
    -------
    commands : str
        Shell command string to be executed on the remote host.
    """
    SCRIPTNAME = 'run.py'
    SHELLNAME = 'job.sh'
    TASKSPERNODE = 1

    submissionParams['tasksPerNode'] = TASKSPERNODE

    pythonScript = 'import sys\n'
    pythonScript += 'from ttheom.cui import run_cui\n\n'
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
    """Check whether an HPC job has completed.

    Parameters
    ----------
    schedulerName : str
        Job scheduler name (e.g. ``'slurm'``).
    jobID : int or str
        Job ID of the simulation.
    client : paramiko.client.SSHClient
        Active SSH client connected to the HPC cluster.

    Returns
    -------
    bool
        ``True`` if the job has completed, ``False`` if it is still running.
    """

    if schedulerName == 'slurm':
        return slurmStatus(jobID, client)
