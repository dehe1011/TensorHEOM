from .slurm import slurmShell

def commandsForSubmission(submissionParams, qpyName, path):
    """create commands for job submission

        params:
            submissionParams (dict):
                parameters for submissoin
                submissoinParams['schedulerName']: job scheduler name
                submissionParams['numNodes'] (int): the number of nodes
                submissionParams['tasksPerNode'] (int):
                    the number of tasks per node
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

    pythonScript = 'import sys\n'
    pythonScript += 'from heom.cui.run import run\n\n'
    pythonScript += 'run(sys.argv[1], sys.argv[2])\n'
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