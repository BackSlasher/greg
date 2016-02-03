==========================
Greg
==========================

------------------------------------------------------
Integrates source providers, build servers and people
------------------------------------------------------

NOT FINISHED
============

Abstract
========
Greg is a small independent utility that helps connect your source code provider (e.g. GitHub), your build servers (e.g. Jenkins) and your code maintainers (e.g. developers).  

I started working on it because I wanted to automate my cookbook lifecycle and couldn't find any project that fit my needs

Basics
======
Greg runs as a flask server (in the future: Django and AWS Lambda support) and is configured using a ``config.yaml``.

It does 3 things:

1. Trigger a test build whenever new code is pushed
2. Trigger a "merge" build when someone asks for it on a PR comment, and several prerequisites exist
3. Report the success / failure of such test/merge builds to the source code provider, in case doing so from the build machine is too complicated

Structure
=========
Greg is designed to be modular. It contains multiple "bridge" modules that allow it to work with multiple build servers / code providers. I've only implemented what I require, but this should allow one to integreate Greg with other builders/providers

Hacking and testing
===================
- Clone
- (optional) Create virtualenv: ``virtualenv .``
- install in dev mode: ``pip install -e .``
- use ``make test`` for testing

External configuration
======================

Jenkins
-------
Credentials, root URL and incoming token go in the ``config.yaml``

Job configuration
`````````````````
Job should have the following parameters:

- SOURCE (string): git repo url
- COMMIT (string): commit to test/merge
- CONTEXT (string): job type (test/merge)
- REPORT (boolean): whether to report back to the provider (can be disabled for jobs invoked manually)
- PR (merge jobs only)(string): PR that is targeted (for reporting purposes)
- TARGET (merge jobs only)(string): Branch to merge to

Job reporting
`````````````
If Jenkins requires Greg's help in notifying the provider when the test/merge passed/failed (we currently use it):

Job should use the `notification plugin <https://wiki.jenkins-ci.org/display/JENKINS/Notification+Plugin>`__ to report its status:

TODO should be automatically configured according to ``config.yaml``

- Format: JSON
- Protocol: HTTP
- Event: Job Completed
- URL: <GREG>/build?builder=jenkins&token=<PRIVATE_TOKEN>
- Timeout: 30000
- Log: 0
