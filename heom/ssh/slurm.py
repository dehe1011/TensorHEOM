def slurmShell(submissionParams, qpyName, scriptName):
    """shell script for the Slurm system
    
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
            scriptName (str): name of python file
                
        returns:
            shell (str): schell script for job submission
            submissionCommand(str): submission command
    """

    # shell script for submission
    shell = '#!/bin/bash\n'
    shell += f"#SBATCH --nodes={submissionParams['numNodes']}\n"
    shell += '#SBATCH --ntasks-per-node=' \
        f"{submissionParams['tasksPerNode']}\n"
    shell += f"#SBATCH --cpus-per-task={submissionParams['cpusPerTask']}\n"
    shell += '#SBATCH -t ' + submissionParams['maxTime'] + '\n'
    shell += submissionParams['others'] + '\n\n'

    venvPath = submissionParams['venvPath']
    if venvPath[-1] == '/':
        venvPath = venvPath[:-1]

    shell += '. ' + submissionParams['venvPath'] + '/bin/activate\n\n'
    
    shell += 'qpyNew=qc${SLURM_JOB_ID}\n'
    shell += 'outName=${SLURM_JOB_ID}.csv\n\n'
    shell += 'mv ' + qpyName + ' $qpyNew\n\n'
    shell += 'python3 ' + scriptName + ' $qpyNew $outName \n'

    submissionCommand = 'sbatch'

    return shell, submissionCommand