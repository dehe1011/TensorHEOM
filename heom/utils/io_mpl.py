import os
import shutil
import matplotlib as mpl
import matplotlib.pyplot as plt

from .. import ROOT_DIR

# ----------------------------------------------------------------------


def load_mpl_style(filepath=None):
    """Copy the mplstyle file to matplotlib's stylelib directory and reload."""

    config_dir = mpl.get_configdir()
    stylelib_dir = os.path.join(config_dir, "stylelib")
    os.makedirs(stylelib_dir, exist_ok=True)
    if filepath is None:
        filepath = os.path.join(ROOT_DIR, "heom", "heom-default.mplstyle")
    shutil.copy(filepath, stylelib_dir)
    plt.style.reload_library()


load_mpl_style()

# ----------------------------------------------------------------------