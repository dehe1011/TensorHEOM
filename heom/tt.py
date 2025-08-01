import numpy as np
from dataclasses import dataclass, field


@dataclass
class zTT:
    core: np.ndarray = field(default_factory=lambda: np.array([], dtype=np.complex128)) # lexicographic order
    level: int = 0
    bondDimL: int = 0
    bondDimR: int = 0


@dataclass
class dTT:
    core: np.ndarray = field(default_factory=lambda: np.array([], dtype=np.float64))
    level: int = 0 # lexicographic order
    bondDimL: int = 0
    bondDimR: int = 0


# -------------------------------------------
# Complex-valued TT (zTT)
# -------------------------------------------
def zCreMPS(intNumCoreIn: int, intBondDimsIn: np.ndarray, intLevelsIn: np.ndarray) -> list[zTT]:
    cmpMPS = [zTT() for _ in range(intNumCoreIn)]

    # First core
    cmpMPS[0].bondDimL = 1
    cmpMPS[0].bondDimR = intBondDimsIn[0, 1]
    cmpMPS[0].level = intLevelsIn[0]
    cmpMPS[0].core = np.zeros(cmpMPS[0].level * cmpMPS[0].bondDimR, dtype=np.complex128)

    for i in range(1, intNumCoreIn - 1):
        cmpMPS[i].bondDimL = intBondDimsIn[i, 0]
        cmpMPS[i].bondDimR = intBondDimsIn[i, 1]
        cmpMPS[i].level = intLevelsIn[i]
        size = cmpMPS[i].level * cmpMPS[i].bondDimL * cmpMPS[i].bondDimR
        cmpMPS[i].core = np.zeros(size, dtype=np.complex128)

    # Last core
    i = intNumCoreIn - 1
    cmpMPS[i].bondDimL = intBondDimsIn[i, 0]
    cmpMPS[i].bondDimR = 1
    cmpMPS[i].level = intLevelsIn[i]
    cmpMPS[i].core = np.zeros(cmpMPS[i].level * cmpMPS[i].bondDimL, dtype=np.complex128)

    return cmpMPS


def zCreMPO(intNumCoreIn: int, intBondDimsIn: np.ndarray, intLevelsIn: np.ndarray) -> list[zTT]:
    cmpMPO = [zTT() for _ in range(intNumCoreIn)]

    # First core
    cmpMPO[0].bondDimL = 1
    cmpMPO[0].bondDimR = intBondDimsIn[0, 1]
    cmpMPO[0].level = intLevelsIn[0]
    cmpMPO[0].core = np.zeros(cmpMPO[0].level**2 * cmpMPO[0].bondDimR, dtype=np.complex128)

    for i in range(1, intNumCoreIn - 1):
        cmpMPO[i].bondDimL = intBondDimsIn[i, 0]
        cmpMPO[i].bondDimR = intBondDimsIn[i, 1]
        cmpMPO[i].level = intLevelsIn[i]
        size = cmpMPO[i].level**2 * cmpMPO[i].bondDimL * cmpMPO[i].bondDimR
        cmpMPO[i].core = np.zeros(size, dtype=np.complex128)

    # Last core
    i = intNumCoreIn - 1
    cmpMPO[i].bondDimL = intBondDimsIn[i, 0]
    cmpMPO[i].bondDimR = intBondDimsIn[i, 1]
    cmpMPO[i].level = intLevelsIn[i]
    cmpMPO[i].core = np.zeros(cmpMPO[i].level**2 * cmpMPO[i].bondDimL, dtype=np.complex128)

    return cmpMPO