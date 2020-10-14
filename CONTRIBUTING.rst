Contribution
============

Thank you for contributing to PyQUBO.

**Propose a new feature and implement**

1. If you have a proposal of new features, send a pull request with your idea and we will discuss it.
2. Once we agree with the new feature, implement the feature. If you implement a new module on top of PyQUBO, create your module inside the ``pyqubo/contrib`` directory.


**Implement a feature or bug-fix for an existing issue**

1. See the issue list of github.
2. Choose an issue and comment on the task that you will work on.
3. Send a pull request.

Implementing unittests for your feature helps a review process.

Installation
------------

If you already installed PyQUBO, uninstall it.

.. code-block:: shell

    pip uninstall pyqubo

Install PyQUBO with development mode

.. code-block:: shell

    python setup.py develop


Coding Conventions
------------------

* Follow PEP8.
* Write docstring with `Google docstrings convention <https://google.github.io/styleguide/pyguide.html>`_.
* Write unit tests.
* Write comments when the code is complicated. But the best documentation is clean code with good variable names.

Unit Testing
------------

To run unit tests, you have two options. One option is to run with unittest or coverage command.
To run all tests with unittest, execute

.. code-block:: shell

    python -m unittest discover tests

To generate coverage reports, execute

.. code-block:: shell

    coverage run -m unittest discover
    coverage html

You will see html files of the report in ``htmlcov`` directory.

Second option is to run test using docker container with circleci CLI locally.
To run test with circleci CLI, execute

.. code-block:: shell

    circleci build --job $JOBNAME

$JOBNAME needs to be replaced with a job name such as `test-3.6`, listed in ``.circleci/config.yml``.
To install circleci CLI, refer to https://circleci.com/docs/2.0/local-cli/.


Documentation
-------------

Documents are created by sphinx from the docstring in Python code. When you add a new class, please create a new rst file in ``docs/reference`` directory. If the information of the class is not important for library users, create a file under
``internal`` directory. To build html files of document locally, execute

.. code-block:: shell

    make clean html

You can see built htmls in ``docs/_build`` directory.
When you write an example code in docstring, you can test the code with doctest. To run doctest, execute

.. code-block:: shell

    make doctest
