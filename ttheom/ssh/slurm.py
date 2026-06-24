def slurmShell(submissionParams, qpyName, scriptName):
    """Generate a Slurm batch script for job submission.

    Parameters
    ----------
    submissionParams : dict
        Slurm submission parameters with the following keys:

        ``'schedulerName'`` : str
            Job scheduler name.
        ``'numNodes'`` : int
            Number of compute nodes.
        ``'tasksPerNode'`` : int
            Number of MPI tasks per node.
        ``'cpusPerTask'`` : int
            Number of CPU cores per task.
        ``'maxTime'`` : str
            Wall-clock time limit in the form ``'D-H:MM:SS'``.
        ``'emailAddress'`` : str
            Email address for Slurm job notifications.
        ``'others'`` : str
            Additional user-defined ``#SBATCH`` directives.
        ``'venvPath'`` : str
            Path to the Python virtual environment.

    qpyName : str
        Name of the input file in QPY format.
    scriptName : str
        Name of the Python runner script.

    Returns
    -------
    shell : str
        Slurm batch script content.
    submissionCommand : str
        Command used to submit the script (``'sbatch'``).
    """

    # shell script for submission
    shell = '#!/bin/bash\n'
    shell += f"#SBATCH --nodes={submissionParams['numNodes']}\n"
    shell += '#SBATCH --ntasks-per-node=' \
        f"{submissionParams['tasksPerNode']}\n"
    shell += f"#SBATCH --cpus-per-task={submissionParams['cpusPerTask']}\n"
    shell += '#SBATCH -t ' + submissionParams['maxTime'] + '\n'
    shell += f"#SBATCH --mail-user={submissionParams['emailAddress']}\n"
    shell += f"#SBATCH --mail-type=ALL,TIME_LIMIT\n"
    shell += submissionParams['others'] + '\n\n'

    venvPath = submissionParams["venvPath"].strip().rstrip("/")

    shell += 'module load numlib/python_scipy/1.16.0_numpy-1.26.4_python-3.12.11\n\n'
    shell += 'export MKL_NUM_THREADS=$SLURM_CPUS_PER_TASK\n'
    shell += 'export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK\n'
    shell += 'export OPENBLAS_NUM_THREADS=$SLURM_CPUS_PER_TASK\n'
    shell += 'export NUMEXPR_NUM_THREADS=$SLURM_CPUS_PER_TASK\n'
    shell += 'export VECLIB_MAXIMUM_THREADS=$SLURM_CPUS_PER_TASK\n'
    shell += 'export MKL_DYNAMIC=FALSE\n'
    shell += 'export OMP_DYNAMIC=FALSE\n'
    shell += f"source {venvPath}/bin/activate\n\n"

    shell += 'qpyNew=qc${SLURM_JOB_ID}\n'
    shell += 'outName=${SLURM_JOB_ID}.csv\n\n'
    shell += 'mv ' + qpyName + ' $qpyNew\n\n'
    shell += 'python3 ' + scriptName + ' $qpyNew $outName \n'

    submissionCommand = 'sbatch'

    return shell, submissionCommand

def slurmStatus(jobID, client):
    """Check whether a Slurm job has completed.

    Parameters
    ----------
    jobID : int or str
        Job ID of the simulation.
    client : paramiko.client.SSHClient
        Active SSH client connected to the HPC cluster.

    Returns
    -------
    bool
        ``True`` if the job has completed, ``False`` if it is still running.
    """

    command = f'squeue -j {jobID}'
    stdin, stdout, stderr = client.exec_command(command)
    outMessage = stdout.read().decode()

    return False if str(jobID) in outMessage else True
