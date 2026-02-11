import copy
import numpy as np
from scipy.linalg import qr

from ..tt.tt import zTT

def zGetSegLeftSt(rhoSt, HSt):
    """
        args:
            rhoSt (tt.zTT): MPS [0:level-1, 0:rhoRR-1]
            HSt (tt.zTT): MPO [0:level-1, 0:level-1, 0:HRR-1]

        returns:
            segLeft (numpy.ndarray): [0:rhoRR-1 (before operation of H),
                                      0:rhoRR-1 (after operation of H),
                                      0:HRR-1]
    """

    rhoCore = rhoSt.core.reshape([rhoSt.level, rhoSt.bondDimR], order='F').T
    HCore = HSt.core.reshape([HSt.level, HSt.level*HSt.bondDimR], order='F')

    tmp1 = np.matmul(rhoCore, HCore) # [rhoRR, level*HRR]

    tmp1 = tmp1.T # [level*HRR, rhoRR]
    tmp1 = tmp1.reshape([rhoSt.level, HSt.bondDimR*rhoSt.bondDimR], order='F')

    rhoCore = rhoSt.core.conj().reshape([rhoSt.level, rhoSt.bondDimR],
                                        order='F').T

    segLeft = np.matmul(rhoCore, tmp1) # [rhoRR (after), HRR*rhoRR (before)]
    segLeft = segLeft.reshape([rhoSt.bondDimR*HSt.bondDimR, rhoSt.bondDimR],
                              order='F')

    segLeft = segLeft.T.flatten(order='F')

    return segLeft

def zGetSegLeft(rho, H, segLeftIn):
    """
        args:
            rho (tt.zTT): MPS [0:rhoRL-1, 0:level-1, 0:rhoRR-1]
            H (tt.zTT): MPO [0:HRL-1, 0:level-1, 0:level-1, 0:HRR-1]
            segLeftIn (numpy.ndarray): [0:rhoRL-1 (before operation of H),
                                        0:rhoRL-1 (after operation of H),
                                        0:HRL-1]

        returns:
            segLeftOut (numpy.ndarray): [0:rhoRR-1 (before operation of H),
                                         0:rhoRR-1 (after operation of H),
                                         0:HRR-1]
    """

    rhoCore = rho.core.reshape([rho.bondDimL, rho.level*rho.bondDimR],
                               order='F').T
    segTmp = segLeftIn.reshape([rho.bondDimL, rho.bondDimL*H.bondDimL],
                               order='F')

    tmp1 = np.matmul(rhoCore, segTmp) # [level*rhoRR (before), rhoRL*HRL]

    tmp1 = tmp1.reshape([rho.level*rho.bondDimR*rho.bondDimL, H.bondDimL],
                        order='F')
    tmp1 = tmp1.T # [HRL, level*rhoRR (before)*rhoRL]
    tmp1 = tmp1.reshape([H.bondDimL*rho.level, rho.bondDimR*rho.bondDimL],
                        order='F')

    HCore = H.core.reshape([H.bondDimL*H.level, H.level*H.bondDimR],
                           order='F').T
    
    tmp2 = np.matmul(HCore, tmp1) # [level*HRR, rhoRR (before)*rhoRL]

    tmp2 = tmp2.reshape([rho.level*H.bondDimR*rho.bondDimR, rho.bondDimL],
                        order='F')
    tmp2 = tmp2.T # [rhoRL, level*HRR*rhoRR (before)]
    tmp2 = tmp2.reshape([rho.bondDimL*rho.level, H.bondDimR*rho.bondDimR],
                        order='F')

    rhoCore = rho.core.conj().reshape([rho.bondDimL*rho.level, rho.bondDimR],
                                      order='F').T

    segLeftOut = np.matmul(rhoCore, tmp2) # [rhoRR (after), HRR*rhoRR (before)]

    segLeftOut = segLeftOut.reshape([rho.bondDimR*H.bondDimR, rho.bondDimR],
                                    order='F')
    segLeftOut = segLeftOut.T

    segLeftOut = segLeftOut.flatten(order='F')

    return segLeftOut

def zGetSegRightEn(rhoEn, HEn):
    """
        args:
            rhoEn (tt.zTT): MPS [0:rhoRL-1, 0:level-1]
            HSt (tt.zTT): MPO [0:HRL-1, 0:level-1, 0:level-1]

        returns:
            segRight (numpy.ndarray): [0:rhoRL-1 (after operation of H),
                                      0:HRL-1
                                      0:rhoRL-1 (before operation of H)]
    """

    rhoCore = rhoEn.core.conj().reshape([rhoEn.bondDimL, rhoEn.level],
                                        order='F').T
    HCore = HEn.core.reshape([HEn.bondDimL*HEn.level, HEn.level], order='F')

    tmp1 = np.matmul(HCore, rhoCore) # [HRL*level, rhoRL (after)]

    tmp1 = tmp1.reshape([HEn.bondDimL, rhoEn.level*rhoEn.bondDimL], order='F')
    tmp1 = tmp1.T # [level*rhoRL (after), HRL]
    tmp1 = tmp1.reshape([rhoEn.level, rhoEn.bondDimL*HEn.bondDimL], order='F')

    rhoCore = rhoEn.core.reshape([rhoEn.bondDimL, rhoEn.level], order='F')
    
    segRight = np.matmul(rhoCore, tmp1) # [rhoRL (before), rhoRL (after)*HRL]

    segRight = segRight.T # [rhoRL (after)*HRL, rhoRL(before)]
    segRight = segRight.flatten(order='F')

    return segRight

def zGetSegRight(rho, H, segRightIn):
    """
        args:
            rho (tt.zTT): MPS [0:rhoRL-1, 0:level-1, 0:rhoRR-1]
            H (tt.zTT): MPO [0:HRL-1, 0:level-1, 0:level-1, 0:HRR-1]

        returns:
            segRightOut (numpy.ndarray): [0:rhoRL-1 (after operation of H),
                                          0:HRL-1
                                          0:rhoRL-1 (before operation of H)]
    """

    rhoCore = rho.core.conj().reshape([rho.bondDimL*rho.level, rho.bondDimR],
                                      order='F')
    segTmp = segRightIn.reshape([rho.bondDimR, H.bondDimR*rho.bondDimR],
                                order='F')

    tmp1 = np.matmul(rhoCore, segTmp) # [rhoRL (after)*level, HRR*rhoRR]

    tmp1 = tmp1.reshape([rho.bondDimL, rho.level*H.bondDimR*rho.bondDimR],
                        order='F')
    tmp1 = tmp1.T # [level*HRR*rhoRR, rhoRL (after)]
    tmp1 = tmp1.reshape([rho.level*H.bondDimR, rho.bondDimR*rho.bondDimL],
                        order='F')

    HCore = H.core.reshape([H.bondDimL*H.level, H.level*H.bondDimR],
                           order='F')

    tmp2 = np.matmul(HCore, tmp1) # [HRL*level, rhoRR*rhoRL (after)]

    tmp2 = tmp2.reshape([H.bondDimL, rho.level*rho.bondDimR*rho.bondDimL],
                        order='F')
    tmp2 = tmp2.T # [level*rhoRR*rhoRL (after), HRL]
    tmp2 = tmp2.reshape([rho.level*rho.bondDimR, rho.bondDimL*H.bondDimL],
                        order='F')

    rhoCore = rho.core.reshape([rho.bondDimL, rho.level*rho.bondDimR],
                               order='F')

    segRightOut = np.matmul(rhoCore, tmp2) # [rhoRL (before), rhoRL (after)*HRL]

    segRightOut = segRightOut.T # [rhoRL (after)*HRL, rhoRL (before)]
    segRightOut = segRightOut.flatten(order='F')

    return segRightOut

def zGetKSt(rhoSt, HSt, segRight):
    """
        args:
            rhoSt (tt.zTT): MPS [0:level-1, 0:rhoRR-1]
            HSt (tt.zTT): MPO [0:level-1, 0:level-1, 0:HRR-1]
            segRight (numpy.ndarray): [0:rhoRR-1 (after),
                                       0:HRR-1,
                                       0:rhoRR-1 (before)]

        returns:
            rhoOut (numpy.ndarray): [0:level-1, 0:rhoRR-1]
    """

    rhoCore = rhoSt.core.reshape([rhoSt.level, rhoSt.bondDimR], order='F').T
    segTmp = segRight.reshape([rhoSt.bondDimR*HSt.bondDimR, rhoSt.bondDimR],
                              order='F')

    tmp1 = np.matmul(segTmp, rhoCore) # [rhoRR (after)*HRR, level]

    tmp1 = tmp1.reshape([rhoSt.bondDimR, HSt.bondDimR*rhoSt.level],
                        order='F')

    HCore = HSt.core.reshape([HSt.level*HSt.level, HSt.bondDimR],
                             order='F').T # [HRR, level*level]
    HCore = HCore.reshape([HSt.bondDimR*HSt.level, HSt.level],
                          order='F') # [HRR*level, level]

    rhoOut = np.matmul(tmp1, HCore) # [rhoRR (after), level]

    rhoOut = rhoOut.T.flatten(order='F')

    return rhoOut

def zGetKEn(rhoEn, HEn, segLeft):
    """
        args:
            rhoEn (tt.zTT): MPS [0:rhoRL-1, 0:level-1]
            HEn (tt.zTT): MPO [0:HRL-1, 0:level-1, 0:level-1]
            segLeft (numpy.ndarray): [0:rhoRL-1 (before operation of H),
                                      0:rhoRL-1 (after operation of H),
                                      0:HRL-1]

        returns:
            rhoOut (numpy.ndarray): [0:rhoRL-1, 0:level-1]
    """

    rhoCore = rhoEn.core.reshape([rhoEn.bondDimL, rhoEn.level], order='F').T
    segTmp = segLeft.reshape([rhoEn.bondDimL, rhoEn.bondDimL*HEn.bondDimL],
                             order='F')

    tmp1 = np.matmul(rhoCore, segTmp) # [level, rhoRL (after)*HRL]

    tmp1 = tmp1.T # [rhoRL (after)*HRL, level]
    tmp1 = tmp1.reshape([rhoEn.bondDimL, HEn.bondDimL*rhoEn.level], order='F')

    HCore = HEn.core.reshape([HEn.bondDimL*HEn.level, HEn.level], order='F')

    rhoOut = np.matmul(tmp1, HCore)

    rhoOut = rhoOut.flatten(order='F')

    return rhoOut

def zGetK(rho, H, segLeft, segRight):
    """
        args:
            rho (tt.zTT): MPS [0:rhoRL-1, 0:level-1, 0:rhoRR-1]
            H (tt.zTT): MPO [0:HRL-1, 0:level-1, 0:level-1, 0:rhoRR-1]
            segLeft (numpy.ndarray): [0:rhoRL-1 (before operation of H),
                                      0:rhoRL-1 (after operation of H),
                                      0:HRL-1]
            segRight (numpy.ndarray): [0:rhoRR-1 (after),
                                       0:HRR-1,
                                       0:rhoRR-1 (before)]

        returns:
            rhoOut (numpy.ndarray):[0:rhoRL-1, 0:level-1, 0:rhoRR-1]
    """

    rhoCore = rho.core.reshape(rho.bondDimL, rho.level*rho.bondDimR,
                               order='F').T
    segTmp = segLeft.reshape([rho.bondDimL, rho.bondDimL*H.bondDimL],
                             order='F')

    tmp1 = np.matmul(rhoCore, segTmp) # [level*rhoRR (before), rhoRL (after)*HRL]

    tmp1 = tmp1.reshape([rho.level*rho.bondDimR*rho.bondDimL, H.bondDimL],
                        order='F')
    tmp1 = tmp1.T # [HRL, level*rhoRR (before)*rhoRL (after)]
    tmp1 = tmp1.reshape([H.bondDimL*rho.level, rho.bondDimR*rho.bondDimL],
                        order='F')
    tmp1 = tmp1.T # [rhoRR (before)*rhoRL (after), HRL*level]

    HCore = H.core.reshape([H.bondDimL*H.level, H.level*H.bondDimR],
                           order='F')

    tmp2 = np.matmul(tmp1, HCore) # [rhoRR (before)*rhoRL (after), level*HRR]

    tmp2 = tmp2.reshape([rho.bondDimR*rho.bondDimL*rho.level, H.bondDimR],
                        order='F')
    tmp2 = tmp2.T # [HRR, rhoRR (before)*rhoRL (after)*level]
    tmp2 = tmp2.reshape([H.bondDimR*rho.bondDimR, rho.bondDimL*rho.level],
                        order='F')

    segTmp = segRight.reshape([rho.bondDimR, H.bondDimR*rho.bondDimR],
                              order='F')

    rhoOut = np.matmul(segTmp, tmp2) # [rhoRR (after), rhoRL (after)*level]

    rhoOut = rhoOut.T
    rhoOut = rhoOut.flatten(order='F')

    return rhoOut

def zGetS(rhoR, HR, S, segLeft, segRight):
    """
        args:
            rhoR (int): bond dimension of rho
            HR (int): bond dimension of H
            S (numpy.ndarray): [0:rhoR-1, 0:rhoR-1]
            segLeft (numpy.ndarray): [0:rhoRL-1 (before operation of H),
                                      0:rhoRL-1 (after operation of H),
                                      0:HRL-1]
            segRight (numpy.ndarray): [0:rhoRR-1 (after),
                                       0:HRR-1,
                                       0:rhoRR-1 (before)]

        returns:
            SOut (numpy.ndarray): [0:rhoR-1, 0:rhoR-1]
    """

    STmp = S.reshape([rhoR, rhoR], order='F').T
    segTmp = segLeft.reshape([rhoR, rhoR*HR], order='F')

    tmp1 = np.matmul(STmp, segTmp) # [rhoR (before), rhoR (after)*HR]

    tmp1 = tmp1.reshape([rhoR**2, HR], order='F')
    tmp1 = tmp1.T # [HR, rhoR (before)*rhoR (after)]
    tmp1 = tmp1.reshape([HR*rhoR, rhoR], order='F')

    segTmp = segRight.reshape([rhoR, HR*rhoR], order='F')

    SOut = np.matmul(segTmp, tmp1) #[rhoR, rhoR]
    SOut = SOut.T.flatten(order='F')

    return SOut

def zGetSK(S, rho):
    """compute TT-core times S (matrix obtained from QR decomposition, R)

        args:
            S (numpy.ndarray): [0:rhoRL-1, 0:rhoRL-1]
            rho (tt.zTT): MPS [0:rhoRL-1, 0:level-1, 0:rhoRR-1]
                          rho.core is overwritten
    """

    STmp = S.reshape([rho.bondDimL, rho.bondDimL], order='F')
    rhoCore = rho.core.reshape([rho.bondDimL, rho.level*rho.bondDimR],
                               order='F')

    tmp = np.matmul(STmp, rhoCore)

    rho.core = tmp.flatten(order='F')

def zGetKS(rho, S):
    """compute TT-core times S (matrix obtained from QR decomposition, R)

        args:
            rho (tt.zTT): MPS [0:rhoRL-1, 0:level-1, 0:rhoRR-1]
                          rho.core is overwritten
            S (numpy.ndarray): [0:rhoRR-1, 0:rhoRR-1]
    """
    
    rhoCore = rho.core.reshape([rho.bondDimL*rho.level, rho.bondDimR],
                               order='F')
    STmp = S.reshape([rho.bondDimR, rho.bondDimR], order='F')

    tmp = np.matmul(rhoCore, STmp)

    rho.core = tmp.flatten(order='F')

def zQRLeft(rho):
    """left-orthogonalization of middle cores

        args:
            rho (tt.zTT): MPS [0:rhoRL-1, 0:level-1, 0:rhoRR-1]
        
        returns:
            rhoOut (tt.zTT): left-orthogonalized MPS [0:rhoRL-1, 0:level-1, 0:rhoRR-1]
            S (numpy.ndarray): [0:rhoRR-1, 0:rhoRR-1]
    """

    rhoCore = rho.core.reshape(rho.bondDimL*rho.level, rho.bondDimR,
                               order='F')

    q, r = qr(rhoCore, mode='economic')

    rhoOut = zTT()
    rhoOut.bondDimL = int(q.shape[0]//rho.level)
    rhoOut.level = rho.level
    rhoOut.bondDimR = q.shape[1]
    rhoOut.core = q.flatten(order='F')

    S = r[0:q.shape[1], 0:q.shape[1]].flatten(order='F')

    return rhoOut, S

def zQRRight(rho):
    """right-orthogonalization of middle cores

        args:
            rho (tt.zTT): MPS [0:rhoRL-1, 0:level-1, 0:rhoRR-1]
        
        returns:
            rhoOut (tt.zTT): right-orthogonalized MPS [0:rhoRL-1, 0:level-1, 0:rhoRR-1]
            S (numpy.ndarray): [0:rhoRL-1, 0:rhoRL-1]
    """

    rhoCore = rho.core.conj().reshape([rho.bondDimL, rho.level*rho.bondDimR],
                                      order='F').T

    q, r = qr(rhoCore, mode='economic')

    q = q.conj().T

    rhoOut = zTT()
    rhoOut.bondDimL = q.shape[0]
    rhoOut.level = rho.level
    rhoOut.bondDimR = int(q.shape[1]//rho.level)
    rhoOut.core = q.flatten(order='F')

    r = r.conj().T
    S = r[0:q.shape[0], 0:q.shape[0]].flatten(order='F')

    return rhoOut, S

def __zOutMPS(rho, idx):
    """output MPS with the index (idx)

        args:
            rho (numpy.ndarray): 1d list of tt.zTT (MPS)
            idx (list): 1d list of index

        returns:
            val (complex): MPS value indicated with idx
    """

    numCore = len(rho)

    i = 0
    outTmp1 = rho[i].core.reshape([rho[i].level, rho[i].bondDimR],
                                  order='F')[idx[i], :]

    for i in range(1, numCore-1):
        coreTmp = rho[i].core.reshape([rho[i].bondDimL, 
                                      rho[i].level, 
                                      rho[i].bondDimR],
                                      order='F')[:, idx[i], :]
        coreTmp = coreTmp.reshape([rho[i].bondDimL, rho[i].bondDimR],
                                  order='F')
        outTmp2 = np.matmul(outTmp1, coreTmp)
        outTmp1 = copy.deepcopy(outTmp2)

    i = numCore-1
    coreTmp = rho[i].core.reshape([rho[i].bondDimL, rho[i].level],
                                  order='F')[:, idx[i]]

    val = np.matmul(outTmp1, coreTmp)

    return val