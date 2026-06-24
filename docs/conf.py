import os
import sys

sys.path.insert(0, os.path.abspath(".."))

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
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "nbsphinx",
]

autosummary_generate = True

autodoc_mock_imports = [
    "customtkinter",
    "tkinter",
    "PIL",
    "PIL.Image",
    "PIL.ImageTk",
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
    "matplotlib.backends.backend_tkagg",
]

# Keep type hints readable and avoid evaluated MagicMock annotations
autodoc_typehints = "description"
autodoc_typehints_format = "short"
autodoc_preserve_defaults = True

# Optional: avoid long module paths in signatures
python_use_unqualified_type_names = True

# Indicate BibTeX file
bibtex_bibfiles = ["biblio.bib"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Options for HTML output
html_theme = "sphinx_rtd_theme"
# html_static_path = ["_static"]
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

# Syntax highlighting
pygments_style = "sphinx"

# Cross-reference formatting
add_function_parentheses = False
add_module_names = False

# Numpydoc options
numpydoc_show_class_members = False
numpydoc_show_inherited_class_members = False
numpydoc_show_property_with_doc = False

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "inherited-members": False,
    "show-inheritance": True,
}