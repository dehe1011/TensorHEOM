import numpy as np
import matplotlib.pyplot as plt

from ..main import prepareTTs

def plotPulseSeq(fig=None, ax=None, **kwargs):
    """Plot the pulse sequences for the transpiled quantum circuit.

    Displays Rabi frequency, phase, and interaction strength for each qubit
    (and each qubit pair for multi-qubit systems).

    Parameters
    ----------
    fig : matplotlib.figure.Figure, optional
        Existing figure to draw into. If ``None``, a new figure is created.
    ax : matplotlib.axes.Axes or numpy.ndarray of Axes, optional
        Existing axes to draw into. If ``None``, new axes are created.
    **kwargs
        Keyword arguments forwarded to :func:`~ttheom.main.prepareTTs`.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object.
    ax : numpy.ndarray of matplotlib.axes.Axes
        The axes objects for the subplots.
    """

    # setup tensor trains
    TTs, params = prepareTTs(**kwargs)

    dtFB = params['dtFB']
    omegaQmax = params['omegaQmax']
    gateTime = [TTs.pulse[i][1].gateTime for i in range(2*TTs.numQ-1)]

    numQ = TTs.numQ
    x_size = 3.4
    if fig is None or ax is None:
        fig, ax = plt.subplots(2*numQ-1, 1, figsize=(x_size, (2*numQ-1) * 2.1/3 + 0.2), sharex=True)
    if numQ == 1:
        ax = [ax]
    for a in ax:
        a.spines["top"].set_visible(True)
        a.spines["right"].set_visible(True)
        a.grid(True, which="both", ls="--", lw=0.5, alpha=0.7)

    for i in range(numQ):
        pulseIdx = i
        ampSeq = TTs.pulse[pulseIdx][1].ampSeq
        phaseSeq = TTs.pulse[pulseIdx][1].phaseSeq

        t = np.arange(len(phaseSeq)) * dtFB / omegaQmax

        # --- left axis: amplitude ---
        ax_amp = ax[i]
        ax_amp.plot(t, ampSeq, color="#459DD9")
        ax_amp.set_ylabel(fr"$\Omega_{i+1}$", color="#064D99")
        ax_amp.tick_params(axis="y", labelcolor="#064D99")
        ax_amp.set_yticks([0, np.pi/gateTime[i]], [r'0', r'$\frac{\pi}{\omega t_G}$'])
        amp_diff = np.max(ampSeq) - np.min(ampSeq)
        ax_amp.set_ylim(np.min(ampSeq) - 0.1*amp_diff, np.max(ampSeq) + 0.1*amp_diff)

        # --- right axis: phase ---
        ax_phase = ax_amp.twinx()
        ax_phase.plot(t, phaseSeq, color="#B74244")
        ax_phase.set_ylabel(fr"$\phi_{i+1}$", color="#780B1C")
        ax_phase.tick_params(axis="y", labelcolor="#780B1C")

        A = np.array([-2*np.pi, -3/2*np.pi, -np.pi, -np.pi/2, 0, np.pi/2, np.pi, 3/2*np.pi, 2*np.pi])
        B = [r"$-2\pi$", r"$-\frac{3\pi}{2}$", r"$-\pi$", r"$-\frac{\pi}{2}$",
            r"$0$", r"$\frac{\pi}{2}$", r"$\pi$", r"$\frac{3\pi}{2}$", r"$2\pi$"]
        mask = (A >= np.min(phaseSeq)) & (A <= np.max(phaseSeq))
        A_ticks = A[mask]
        B_labels = [lbl for lbl, m in zip(B, mask) if m]
        ax_phase.set_yticks(A_ticks, B_labels)
        phase_diff = np.max(phaseSeq) - np.min(phaseSeq)
        ax_phase.set_ylim(np.min(phaseSeq) - 0.1*phase_diff, np.max(phaseSeq) + 0.1*phase_diff)
        ax_phase.grid(True, which="both", ls="--", lw=0.5, alpha=0.7)


    if numQ >= 2:
        for i in range(numQ-1):
            pulseIdx = i + numQ
            JSeq = TTs.pulse[pulseIdx][1].JSeq

            ax_J = ax[i + numQ]
            ax_J.plot(t, JSeq, color="#A546BD")
            ax_J.set_ylabel(rf"$J_{{{i+1}{i+2}}}$", color="#6C0B8D")
            ax_J.tick_params(axis="y", labelcolor="#6C0B8D")
            ax_J.set_yticks([0, np.pi/2/gateTime[numQ+i] ], [r'0', r'$\frac{\pi}{2\omega t_G}$'])
            J_diff = np.max(JSeq) - np.min(JSeq)
            ax_J.set_ylim(np.min(JSeq) - 0.1*J_diff, np.max(JSeq) + 0.1*J_diff)

    ax[-1].set_xlabel(r"$t$ [ns]")
    return fig, ax
