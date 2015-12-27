#!/usr/bin/env python
import greg.logic
from flask import Flask, request

application= Flask('application')

# Called by the repository (github / bitbucket) whenever there's a commit / comment
@application.route('/repo')
def repo():
  headers = {k:request.headers[k] for k in request.headers.keys()}
  querystring = request.args
  payload = request.data
  greg.logic.repo(querystring['provider'],payload,headers,querystring)

# Called by the build server when it finished a job (and requires Greg's help in notifying)
@application.route('/build')
def build():
  headers = {k:request.headers[k] for k in request.headers.keys()}
  querystring = request.args
  payload = request.data
  greg.logic.build(querystring['builder'],payload,headers,querystring)

@application.route('/')
def root():
  return 'I am Greg'

def run():
  global application
  application.run()

if __name__ == '__main__':
    run()
