==================
token_supplier
==================

:Version: 0.5.0
:Source: https://github.com/maykinmedia/zds-token-issuer
:Keywords: auth, tokens, zgw-api, zaken
:PythonVersion: 3.7

|build-status| |requirements|

A tool to generate and register credentials for Zaakgericht werken APIs.

Developed by `Maykin Media B.V.`_ for VNG Realisatie


Introduction
============

This tool generates a pair of client ID + secret to authenticate against
APIs implemented with vng-api-common. It provides an interface to manage the
authorizations of an application.

Documentation
=============

See ``INSTALL.rst`` for installation instructions, available settings and
commands.

Management command
------------------

``generate_fixtures`` generates fixture files that can be loaded into each
component (ZRC, DRC...)

Usage:

.. code-block:: bash

    python src/manage.py generate_fixtures

The command will interactively ask for Client ID and Secret. The resulting
fixtures set up a superuser client that can connect to all services.

References
==========

* `Issues <https://taiga.maykinmedia.nl/project/token_supplier>`_
* `Code <https://bitbucket.org/maykinmedia/token_supplier>`_


.. |build-status| image:: http://jenkins.maykin.nl/buildStatus/icon?job=bitbucket/token_supplier/master
    :alt: Build status
    :target: http://jenkins.maykin.nl/job/token_supplier

.. |requirements| image:: https://requires.io/bitbucket/maykinmedia/token_supplier/requirements.svg?branch=master
     :target: https://requires.io/bitbucket/maykinmedia/token_supplier/requirements/?branch=master
     :alt: Requirements status


.. _Maykin Media B.V.: https://www.maykinmedia.nl
