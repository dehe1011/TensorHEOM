import re
from .io_qc import saveQC
from .connect_ssh import getClient
from .commands import commandsForSubmission, getStatus

def submitJob(submissionParams, qcFilePath, omegaQmax, qc, idlingTime, gateList, rho,
              bath, V, dtFB, stride, depth, bondDim, isRK13=False,
              useRFPlus=False):
    """Submit a simulation job to an HPC cluster.

    Parameters
    ----------
    submissionParams : dict
        HPC connection and scheduler parameters with the following keys:

        ``'hostname'`` : str
            Server hostname to connect to.
        ``'username'`` : str
            SSH username.
        ``'password'`` : str
            SSH password.
        ``'otp'`` : str
            One-time password for two-factor authentication.
        ``'schedulerName'`` : str
            Job scheduler name (e.g. ``'slurm'``).
        ``'numNodes'`` : int
            Number of compute nodes.
        ``'cpusPerTask'`` : int
            Number of CPU cores per task.
        ``'maxTime'`` : str
            Wall-clock time limit in the form ``'D-H:MM:SS'``.
        ``'emailAddress'`` : str
            Email address for job notifications.
        ``'others'`` : str
            Additional scheduler directives.
        ``'venvPath'`` : str
            Path to the Python virtual environment on the cluster.

    qcFilePath : str
        Local file path where the quantum-circuit QPY data will be saved.
    omegaQmax : float
        Maximum qubit angular frequency (rad/ns).
    qc : qiskit.QuantumCircuit
        Quantum circuit for the simulation.
    idlingTime : float
        Idling time in units of ``omegaQ[0]``.
    gateList : list
        List of gate specifications.
    rho : dict
        System dictionary with keys ``'numQ'``, ``'rhoIni'``, ``'omegaQ'``.
    bath : list of dict
        Bath parameter dictionaries.
    V : numpy.ndarray
        3-D system-bath coupling array; ``V[j]`` is the operator for bath ``j``.
    dtFB : float
        Integration time step for forward/backward HEOM propagation.
    stride : int
        Number of integration steps between successive outputs.
    depth : list of int
        FP-HEOM hierarchy depths.
    bondDim : int
        Maximum MPS bond dimension.
    isRK13 : bool, optional
        Use the 13-stage 5th-order Runge-Kutta scheme. Default ``False``.
    useRFPlus : bool, optional
        Use the Redfield+ method. Default ``False``.

    Returns
    -------
    job_id : str or None
        The cluster job ID assigned by the scheduler, or ``None`` if it could
        not be parsed from the submission output.
    """

    QPYNAME = 'qcData'
    REMOTEPATH = 'python_HEOM'

    # output parameters for simulation
    filePath = QPYNAME
    saveQC(filePath, omegaQmax, qc, idlingTime, gateList, rho, bath, V, dtFB,
           stride, depth, bondDim, isRK13=isRK13, useRFPlus=useRFPlus)

    # connect to an HPC server
    client = getClient(submissionParams['hostname'],
                       submissionParams['username'],
                       submissionParams['password'],
                       submissionParams['otp'])

    # send parameters to the server
    sftp = client.open_sftp()
    remoteName = REMOTEPATH + '/' + QPYNAME
    sftp.put(qcFilePath, remoteName)
    sftp.close()

    # submit a job
    commands = commandsForSubmission(submissionParams, QPYNAME, REMOTEPATH)
    stdin, stdout, stderr = client.exec_command(commands)

    s = stdout.read().decode()
    print(s)
    m = re.search(r'\d+', s)
    job_id = m.group() if m else None
    print("Save the job ID! It is used for getting results.")

    client.close()
    return job_id

def downloadResult(downloadParams, jobID, fileName):
    """Download a simulation result CSV file from an HPC cluster.

    Parameters
    ----------
    downloadParams : dict
        Connection parameters with the following keys:

        ``'hostname'`` : str
            Server hostname.
        ``'username'`` : str
            SSH username.
        ``'password'`` : str
            SSH password.
        ``'otp'`` : str
            One-time password for two-factor authentication.
        ``'schedulerName'`` : str
            Job scheduler name (e.g. ``'slurm'``).

    jobID : int or str
        Job ID of the completed simulation; the remote file is named
        ``{jobID}.csv``.
    fileName : str
        Local file path where the result will be saved.
    """

    # connect to an HPC server
    client = getClient(downloadParams['hostname'],
                       downloadParams['username'],
                       downloadParams['password'],
                       downloadParams['otp'])

    # check whether the simulation is completed
    isCompleted = getStatus(downloadParams['schedulerName'], jobID, client)
    if not isCompleted:
        print('The job is not yet completed.')
        return

    # check whether the result file exists
    remoteName = f'{jobID}.csv'

    stdin, stdout, stderr = client.exec_command('find -name ' + remoteName)
    outMessage = stdout.read().decode()

    if len(outMessage) == 0:
        print('The job might have failed. ' +
              'The job is not running, ' +
              'but the corresponding output file cannot be found.')
        return

    # download
    remotePath = outMessage[2:-1] # remove './' and '\n'

    sftp = client.open_sftp()
    sftp.get(remotePath, fileName)

    sftp.close()

    client.close()
