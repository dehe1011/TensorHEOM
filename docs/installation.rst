
******************
Installation Guide
******************

Welcome to the installation guide for `TensorHEOM`. Follow the steps below to install the package, set up a virtual environment, and start using the Graphical User Interface.


Installation via PyPI
=====================

The easiest way to install `TensorHEOM` is through PyPI. For best results, we recommend creating a new virtual environment to avoid package conflicts.

Steps
-----

1. **Create a New Virtual Environment**:

   Open your terminal and navigate to your project folder. Run:

   .. code-block:: bash

      python -m venv .venv

2. **Activate the Virtual Environment**:

   - **Windows**:

     .. code-block:: bash

        .venv\Scripts\activate

   - **macOS/Linux**:

     .. code-block:: bash

        source .venv/bin/activate

3. **Install the `TensorHEOM` Package**:

   .. code-block:: bash

      pip install ttheom


Installation in editable mode via GitHub
========================================

If you plan to contribute to the development or make changes to the source code, install `TensorHEOM` in editable mode by cloning its GitHub repository.

Steps
-----

1. **Clone the GitHub Repository**:

   .. code-block:: bash

      git clone https://github.com/dehe1011/TensorHEOM.git

2. **Navigate to the Cloned Repository**:

   .. code-block:: bash

      cd TensorHEOM

3. **Run the Activation Script**:

   Use the provided activation script to complete the installation. Instructions vary by platform (see below).


Platform-Specific Instructions for Activation
=============================================

**Windows**
-----------

1. Navigate to the project directory:

   .. code-block:: powershell

      Set-Location -Path "C:\Users\<YourUsername>\TensorHEOM"

2. Run the activation script:

   .. code-block:: powershell

      powershell -ExecutionPolicy Bypass -File scripts\Activate.ps1

**macOS**
---------

1. Navigate to the project directory:

   .. code-block:: bash

      cd /Users/<YourUsername>/TensorHEOM

2. Run the activation script:

   .. code-block:: bash

      source scripts/activate

**Linux**
---------

1. Navigate to the project directory:

   .. code-block:: bash

      cd /home/<YourUsername>/TensorHEOM

2. Run the activation script:

   .. code-block:: bash

      source scripts/activate


Uninstallation
==============

To remove the package:

.. code-block:: bash

   pip uninstall TensorHEOM

If you cloned the GitHub repository, manually delete the `TensorHEOM` folder from your computer.
