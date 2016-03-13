==========================
Greg
==========================

------------------------------------------------------
Integrates source providers, build servers and people
------------------------------------------------------

Abstract
========
Greg is a small independent utility that helps connect your source code provider (e.g. GitHub), your build servers (e.g. Jenkins) and your code maintainers (e.g. developers).  

I started working on it because I wanted to automate my cookbook lifecycle and couldn't find any project that fit my needs

Basics
======
Greg runs as a flask server (ready for AWS Elastic Beanstalk, in the future: Django and AWS Lambda support) and is configured using a ``config.yaml``.

It does 3 things:

1. Trigger a test build whenever new code is pushed
2. Trigger a "merge" build when someone asks for it on a PR comment, and several prerequisites exist
3. Report the success / failure of such test/merge builds to the source code provider, in case doing so from the build machine is too complicated

Structure
=========
Greg is designed to be modular. It contains multiple "bridge" modules that allow it to work with multiple build servers / code providers. I've only implemented what I require, but this should allow one to integreate Greg with other builders/providers.

Every provider/builder should have an entry in the `config.yaml` file, containing the provider/builder URL, Greg's credentials and an "incoming token". This token is used as some sort of authentication - each message from the builder/provider should contain this token.

Basic Workflow
--------------

On code pushes (automatic testing):

1. User pushes code to PROVIDER
2. PROVIDER notifies Greg (via webhook)
3. Greg checks if referenced repository has a test job defined (assuming it does)
4. Greg invokes relevant job on BUILDER with parameters referring to the relevant commit in the repository.
5. BUILDER completes test job and notifies Greg
6. Greg notifies PROVIDER about the test success/failure

On managing pull requests:

1. User creates pull request
2. User wants to see if all clear, comments "Greg OK" on the PR
3. PROVIDER notifies Greg
4. Greg surveys the repository on PROVIDER and reports back whether the PR is mergable, and posts the result on the PR
5. User fixes stuff (or not) and tries to merge. Comments "Greg please" on the PR
6. Greg checks the PR. Assuming it's mergable, it invokes the matching merge job on BUILDER
7. BUILDER notifies Greg on job completion
8. If merge job was completed successfully, do nothing. If not, comment on the PR

"Mergable" PRs
---------------
a PR is considered mergable by Greg if:

- Source and destination repo are identical
- All of the reviewers approved the PR (actual implementation differs across providers)
- The head (commit to be merged) has to pass Greg's approval

Approvers and Reviewers
-----------------------
This idea started from BitBucket and got migrated to other providers.

Basically, each PR has a set (that can be empty) of "reviewers", which are users that should make sure the PR is a good idea.

Each PR also has a set (that can be empty) of "approvers", which are users that currently think this PR is a good idea.

One of Greg's requirements for merging PRs is having all of the reviewers approve.

The way for managing reviewers / approvers differs per provider

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
Jenkins is supported as a builder

General requirements
`````````````````````
- Greg and Jenkins should have HTTP access to each other.
- Greg should have a user (+password / API key) to Jenkins. This user should be able to lunch jobs. My working permission set: ::

    Jenkins.READ
    Item.DISCOVER
    Item.READ
    Item.BUILD
    
  Jenkins' URL, credentials and incoming token should be stored in Greg's config file.

Job configuration
`````````````````
Greg invokes jobs with the following parameters. If there are extra parameters, they'll have their default value.

- SOURCE (string): git repo url
- COMMIT (string): commit to test/merge
- CONTEXT (string): job type (test/merge)
- REPORT (boolean): whether to report back to the provider (can be disabled for jobs invoked manually)
- PR (merge jobs only)(string): PR that is targeted (for reporting purposes)
- TARGET (merge jobs only)(string): Branch to merge to

Job reporting
`````````````
Greg supports reporting the test/merge job result to the provider. To do so, we need to instruct Jenkins to report back to Greg.

If Jenkins requires Greg's help in notifying the provider when the test/merge passed/failed (we currently use it):

First, Jenkins should have the `notification plugin <https://wiki.jenkins-ci.org/display/JENKINS/Notification+Plugin>`__ installed.

**notice** config below is automatically handled with `--fix-hooks`

Second, the job should be configured to notify Greg when the job is completed. These are the required parameters, in case you want to do so manually:

- Format: JSON
- Protocol: HTTP
- Event: Job Completed
- URL: <GREG>/build?builder=jenkins&token=<PRIVATE_TOKEN>
- Timeout: 30000
- Log: 0


GitHub
------
GitHub is supported as a provider

General requirements
````````````````````

- Greg and GitHub should have HTTP access to each other
- Greg should have a user (+password / key) for GitHub. This user should be able to read the repository

Webhook configuration
`````````````````````

**notice** config below is automatically handled with `--fix-hooks`

Each repository should have a single webhook pointing to Greg. Parameters are as follows:

- Payload URL: `<GREG>/repo?provider=github&token=<PRIVATE_TOKEN>`
- Content Type: `application/json`
- Events sent:

  - Push
  - Issue comment

- Active: True

BitBucket
---------
BitBucket is supported as a provider

General requirements
````````````````````

- Greg and BitBucket should have HTTP acccess to each other
- Greg should have a user (+password / key) for BitBucket. This user should be able to read the repository

Webhook configuration
`````````````````````

**notice** config below is automatically handled with `--fix-hooks`

Each repository should have a single webhook pointing to Greg. Parameters are as follows:

- URL: `<GREG>/repo?provider=bitbucket&token=<PRIVATE_TOKEN>`
- Status: Active
- Triggers:

  - Repository: Push
  - Pull Request: Comment created

fix-hooks
=========
The Greg "binary" (entry point) contains a `--fix-hooks` mode. This command will make Greg go over all of the repositories and jobs detailed in the config file, and make sure they're configured to report back to Greg. For this to work, Greg must have permissions to modify the webhooks on relevant repos/jobs, and must also know its URL, specified with the `--url` argument.
