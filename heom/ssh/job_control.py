from qiskit import qpy
from .connect_ssh import getClient
from .commands import commandsForSubmission

def submitJob(submissionParams, qc, idlingTime, gateList, rho,
              bath, V, dtFB, stride, isRK13=False):
    """submit a job to an HPC cluster

        params:
            submissionParams (dict):
                parameters for submissoin
                submissionParams['hostname'] (str): server name to connect to
                submissionParams['username'] (str): user name
                submissoinParams['schedulerName'] (str): job scheduler name
                submissionParams['numNodes'] (int): the number of nodes
                submissionParams['cpusPerTask'] (int):
                    the number of cpus per task
                submissionParams['maxTime'] (str):
                    maximum time for calculation in the form 'D-H:MM:SS'
                submissionParams['others'] (str): user-defined parameters
                submissionParams['venvPath']:
                    path of venv (virtual environment)
            qc (qiskit.QuantumCircuit): quantum circuit for simulation
            idlingTime (float): idling time, in the unit of omegaQ[0] 
            gateList (list): list for qubit gates
            rho (dict): properties of systems
                rho['numQ']: number of qubits
                rho['rhoIni'] (numpy.ndarray): initial reduced density matrix
                rho['omegaQ'] (list): list of qubit frequency                
            bath (list): list of bath name
            V (numpy.ndarray): 3d array of system-bath coupling
                V[j, :, :]: system operator coupled with j th bath
            dtFB (float): step width for forward + backward time integration
            stride (int): loops per output
            isRK13 (bool): Runge-Kutta method
                True: 13-stage 5th-order Runge-Kutta
                False: 5-stage 4th-order Runge-Kutta
    """

    QPYNAME = 'qcData'
    REMOTEPATH = 'python_HEOM'

    # output parameters for simulation
    params = {}
    params['idlingTime'] = idlingTime
    params['gateList'] = gateList
    params['bath'] = bath
    params['dtFB'] = dtFB
    params['stride'] = stride
    params['isRK13'] = isRK13

    rhoIni = rho.pop('rhoIni')
    rho['rhoReal'] = rhoIni.real.tolist()
    rho['rhoImag'] = rhoIni.imag.tolist()
    params['rho'] = rho

    VTmp = {}
    VTmp['real'] = V.real.tolist()
    VTmp['imag'] = V.imag.tolist()
    params['VTmp'] = VTmp

    qc.metadata = params

    with open(QPYNAME, 'wb') as file:
        qpy.dump(qc, file)

    # connect to an HPC server
    client = getClient(submissionParams['hostname'],
                       submissionParams['username'])

    # send parameters to the server
    sftp = client.open_sftp()
    remoteName = REMOTEPATH + '/' + QPYNAME
    sftp.put(QPYNAME, remoteName)
    sftp.close()

    # submit a job
    commands = commandsForSubmission(submissionParams, QPYNAME, REMOTEPATH)
    stdin, stdout, stderr = client.exec_command(commands)
    
    print(stdout.read().decode())
    print("Save the job ID! It is used for getting results.")

    client.close()