import copy
import numpy as np
from .TTs import TTs
from .opett import (zGetSegLeftSt, zGetSegLeft, zGetSegRightEn, zGetSegRight, zGetKSt,
                    zGetKEn, zGetK, zGetS, zGetSK, zGetKS, zQRLeft, zQRRight
                    )

class timeEvolution():
    """ class for time evolution

        attributes:
            dt (float): step width
            numCore (int): number of cores
            segArray (list): list of segments used for update of core
            ZNRK (int): stage number of Runge-Kutta
            zA, zB, zC (numpy.ndarray): parameters for Runge-Kutta
    """
    def __init__(self, TTsIni: TTs, dt: float, isRK13: bool):
        """
            params:
                TTsIni (TTs.TTs): initialized MPS and MPO
                dt (float): step witdh for forward/backward time integration
                isRK13 (bool): Runge-Kutta method
                    True: 13-stage 5th-order Runge-Kutta
                    False: 5-stage 4th-order Runge-Kutta
        """
        self.dt = dt
        self.numH = TTsIni.numH
        self.getPrefactors = TTsIni.getPrefactors


        self.segArray = self.zInitSegment(TTsIni)

        if isRK13: # RK13-5
            self.ZNRK = 13
            self.zA = np.array([
                0,
                -0.33672143119427413,
                -1.2018205782908164,
                -2.6261919625495068,
                -1.5418507843260567,
                -0.2845614242371758,
                -0.1700096844304301,
                -1.0839412680446804,
                -11.61787957751822,
                -4.5205208057464192,
                -35.86177355832474,
                -0.000021340899996007288,
                -0.066311516687861348
            ])

            self.zB = np.array([
                0.069632640247059393,
                0.088918462778092020,
                1.0461490123426779,
                0.42761794305080487,
                0.20975844551667144,
                -0.11457151862012136,
                -0.01392019988507068,
                4.0330655626956709,
                0.35106846752457162,
                -0.16066651367556576,
                -0.0058633163225038929,
                0.077296133865151863,
                0.054301254676908338
            ])

            self.zC = np.array([
                0,
                0.069632640247059393,
                0.12861035097891748,
                0.34083022189561149,
                0.54063706308495402,
                0.59927749518613931,
                0.49382042519248519,
                0.48207852767699775,
                0.82762865209834452,
                0.82923953914857933,
                0.67190565554748019,
                0.87194975193167848,
                0.94930216564503562
            ])
        else: # RK5-4
            self.ZNRK = 5
            self.zA = np.array([
                0,
                -567301805773 / 1357537059087,
                -2404267990393 / 2016746695238,
                -3550918686646 / 2091501179385,
                -1275806237668 / 842570457699
            ])

            self.zB = np.array([
                1432997174477 / 9575080441755,
                5161836677717 / 13612068292357,
                1720146321549 / 2090206949498,
                3134564353537 / 4481467310338,
                2277821191437 / 14882151754819
            ])

            self.zC = np.array([
                0,
                1432997174477 / 9575080441755,
                2526269341429 / 6820363962896,
                2006345519317 / 3224310063776,
                2802321613138 / 2924317926251
            ])

    def zInitSegment(self, TTsIni: TTs):
        """initialize 

            params:
                TTsIni (TTs.TTs): initialized MPS and MPO

            reutrns:
                segArray (list): list of segments used for update of core
        """

        segArray = [[None for _ in range(TTsIni.numCore)]
                    for _ in range(self.numH)]

        i = TTsIni.numCore-1
        for j in range(self.numH):
            segArray[j][i] = zGetSegRightEn(TTsIni.rho[i],
                                                  TTsIni.H[j, i])
            
        for i in range(TTsIni.numCore-2, 0, -1):
            for j in range(self.numH):
                segArray[j][i] = zGetSegRight(TTsIni.rho[i],
                                                    TTsIni.H[j, i],
                                                    segArray[j][i+1])
                
        i = 0
        for j in range(self.numH):
            segArray[j][i] = np.zeros(TTsIni.rho[i].bondDimL**2
                                      * TTsIni.H[j, i].bondDimL, 
                                      dtype = np.complex128)
            
        return segArray

    def zTTTimeEvo(self, rho, H, time, stepNum):
        """time evolution of rho with H at time

            params:
                rho (numpy.ndarray): 1d array of tt.zTT (MPS)
                            overwritten with output
                H (numpy.ndarray): 
                    2d array of tt.zTT (MPO), Hamiltonian
                time (float): current time
                stepNum (int): current step number
        """

        numCore = len(rho)

        intBonds = [0] * (self.numH)

        self.stepNum = stepNum

        # Forward sweep
        i = 0
        self.zKRK4St(rho[i], H[:, i], i, time)

        rhoTmp, S  = zQRLeft(rho[i])

        rho[i] = copy.deepcopy(rhoTmp)
        for j in range(self.numH):
            self.segArray[j][i] = zGetSegLeftSt(rho[i], H[j, i])
            intBonds[j] = H[j, i].bondDimR

        self.zSRK4(S, i, rho[i].bondDimR, intBonds, time)
        
        for i in range(1, numCore - 1):
            zGetSK(S, rho[i])

            self.zKRK4(rho[i], H[:, i], i, time)

            rhoTmp, S = zQRLeft(rho[i])
            rho[i] = copy.deepcopy(rhoTmp)

            for j in range(self.numH):
                self.segArray[j][i] = zGetSegLeft(
                    rho[i], H[j, i], self.segArray[j][i - 1])
                intBonds[j] = H[j, i].bondDimR

            self.zSRK4(S, i, rho[i].bondDimR, intBonds, time)

        i = numCore - 1
        zGetSK(S, rho[i])
        self.zKRK4En(rho[i], H[:, i], i, time)

        # Backward sweep
        self.zKRK4En(rho[i], H[:, i], i, time + self.dt)

        rhoTmp, S = zQRRight(rho[i])
        rho[i] = copy.deepcopy(rhoTmp)
        for j in range(self.numH):
            self.segArray[j][i] = zGetSegRightEn(rho[i], H[j, i])
            intBonds[j] = H[j, i].bondDimL

        self.zSRK4(S, i - 1, rho[i].bondDimL, intBonds, time + self.dt)

        for i in range(numCore - 2, 0, -1):
            zGetKS(rho[i], S)
            self.zKRK4(rho[i], H[:, i], i, time + self.dt)

            rhoTmp, S = zQRRight(rho[i])
            rho[i] = copy.deepcopy(rhoTmp)

            for j in range(self.numH):
                self.segArray[j][i] = zGetSegRight(
                    rho[i], H[j, i], self.segArray[j][i + 1])
                intBonds[j] = H[j, i].bondDimL

            self.zSRK4(S, i - 1, rho[i].bondDimL, 
                       intBonds, time + self.dt)

        i = 0
        zGetKS(rho[i], S)
        self.zKRK4St(rho[i], H[:, i], i, time + self.dt)

    def zKRK4St(self, rho, H, coreIdx, time):
        """RK integration of K at starting point

            params:
                rho (tt.zTT): MPS
                              overwritten with output
                H (numpy.ndarray): array of MPO
                coreIdx (int): index of the core
                time (float): current time
        """

        dumCore1 = np.zeros(rho.core.shape, dtype=np.complex128)

        for i in range(self.ZNRK):
            timeTmp = time + self.dt * self.zC[i]
            preFact = self.getPrefactors(self.dt, timeTmp, self.stepNum)

            dumCore1 *= self.zA[i]
            for j in range(self.numH):
                dumCore2 = zGetKSt(rho, H[j],
                                   self.segArray[j][coreIdx+1])
                dumCore1 += preFact[j] * dumCore2
            
            rho.core += self.zB[i] * dumCore1

    def zKRK4En(self, rho, H, coreIdx, time):
        """RK integration of K at ending point
        
            params:
                rho (tt.zTT): MPS
                              overwritten with output
                H (numpy.ndarray): array of MPO
                coreIdx (int): index of the core
                time (float): current time
        """

        dumCore1 = np.zeros(rho.core.shape, dtype=np.complex128)

        for i in range(self.ZNRK):
            timeTmp = time + self.dt * self.zC[i]
            preFact = self.getPrefactors(self.dt, timeTmp, self.stepNum)

            dumCore1 *= self.zA[i]
            for j in range(self.numH):
                dumCore2 = zGetKEn(rho, H[j],
                                         self.segArray[j][coreIdx-1])
                dumCore1 += preFact[j] * dumCore2
            
            rho.core += self.zB[i] * dumCore1

    def zKRK4(self, rho, H, coreIdx, time):
        """RK integration of K (intermediate)
        
            params:
                rho (tt.zTT): MPS
                              overwritten with output
                H (numpy.ndarray): array of MPO
                coreIdx (int): index of the core
                time (float): current time
        """

        dumCore1 = np.zeros(rho.core.shape, dtype=np.complex128)

        for i in range(self.ZNRK):
            timeTmp = time + self.dt * self.zC[i]
            preFact = self.getPrefactors(self.dt, timeTmp, self.stepNum)

            dumCore1 *= self.zA[i]
            for j in range(self.numH):
                dumCore2 = zGetK(rho, H[j],
                    self.segArray[j][coreIdx-1],
                    self.segArray[j][coreIdx+1])
                dumCore1 += preFact[j] * dumCore2
            
            rho.core += self.zB[i] * dumCore1

    def zSRK4(self, S, coreIdx, rhoR, HRs, time):
        """RK integration for S

            params:
                S (numpy.ndarray): matrix S
                                   overwritten with output
                coreIdx (int): core index
                rhoR (int): right bond dimension of rho
                HRs (list): list of right bond dimension of H
                time (float): current time
        """
        
        dumS1 = np.zeros(S.shape, dtype=np.complex128)

        for i in range(self.ZNRK):
            timeTmp = time + self.dt * self.zC[i]
            preFact = -self.getPrefactors(self.dt, timeTmp, self.stepNum)

            dumS1 *= self.zA[i]
            for j in range(self.numH):
                dumS2 = zGetS(rhoR, HRs[j], S,
                    self.segArray[j][coreIdx],
                    self.segArray[j][coreIdx+1])
                dumS1 += preFact[j] * dumS2

            S += self.zB[i] * dumS1

def zRightOrth(rho):
    """right-orthogonalization of cores (initalization)

        params:
            rho (numpy.ndarray): 1d array of tt.zTT
    """

    numCore = len(rho)
    
    # Start from the last core
    i = numCore - 1
    rhoTmp, S = zQRRight(rho[i])
    rho[i] = copy.deepcopy(rhoTmp)

    # Sweep from right to left
    for i in range(numCore - 2, 0, -1):
        zGetKS(rho[i], S)
        rhoTmp, S = zQRRight(rho[i])
        rho[i] = copy.deepcopy(rhoTmp)

    # Final propagation of S to the first core
    i = 0
    zGetKS(rho[i], S)
