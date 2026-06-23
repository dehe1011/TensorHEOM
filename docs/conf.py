import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(".."))

# Mock optional packages that may be unavailable in the docs build environment
_MOCK_MODULES = [
    "customtkinter",
    "tkinter",
    "tkinter.filedialog",
    "tkinter.scrolledtext",
    "PIL",
    "PIL.Image",
    "PIL.ImageTk",
    "matplotlib.backends.backend_tkagg",
    "baryrat",
    "paramiko",
    "tqdm",
    "qiskit",
    "qiskit.qpy",
    "qiskit.circuit",
    "qiskit.circuit.library",
    "qiskit.quantum_info",
    "qiskit.transpiler",
    "qutip",
    "scipy",
    "scipy.constants",
    "scipy.integrate",
    "scipy.linalg",
    "pandas",
    "matplotlib",
    "matplotlib.pyplot",
    "matplotlib.style",
]
for _mod in _MOCK_MODULES:
    sys.modules[_mod] = MagicMock()

import ttheom

project = "TensorHEOM"
copyright = "2026, Dennis Herb"
author = "Dennis Herb"
release = ttheom.__version__


extensions = [
    "sphinx_rtd_theme",
    "numpydoc",
    "sphinxcontrib.bibtex",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "nbsphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
]
autosummary_generate = True

autodoc_mock_imports = [
    "customtkinter",
    "tkinter",
    "PIL",
    "baryrat",
    "paramiko",
    "tqdm",
    "qiskit",
    "scipy",
    "pandas",
    "matplotlib",
    "nbsphinx",
]

# Indicate BibTex file
bibtex_bibfiles = ["biblio.bib"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Options for HTML output
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_logo = "figures/logo.png"
html_theme_options = {
    "logo_only": False,
    "prev_next_buttons_location": "bottom",
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 3,
}

html_context = {
    "display_github": True,
    "github_user": "dehe1011",
    "github_repo": "TensorHEOM",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

# Syntax highlighting for code blocks in the documentation
pygments_style = "sphinx"

# Do not add parentheses to function names in cross-references like :func:
add_function_parentheses = False

# Do not add full module names
add_module_names = False

numpydoc_show_class_members = False  # Suppress per-class method autosummary tables (avoids stub-not-found warnings)
numpydoc_show_inherited_class_members = False
numpydoc_show_property_with_doc = False

autodoc_default_options = {
    "members": True,  # Include all members of the class/module
    "undoc-members": False,  # Include undocumented members
    "inherited-members": False,  # Include inherited members
    "show-inheritance": True,  # Show inheritance in the documentation
}
