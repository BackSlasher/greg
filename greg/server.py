import greg.logic
from flask import Flask, request

app = Flask('application')

# Called by the repository (github / bitbucket) whenever there's a commit / comment
@app.route('/repo', methods=['POST'])
def repo():
  headers = {k:request.headers[k] for k in request.headers.keys()}
  querystring = {k:request.args[k] for k in request.args.keys()}
  payload = request.data
  if not querystring.has_key('provider'): return 'missing provider querystring',500
  greg.logic.repo(querystring['provider'],payload,headers,querystring)

# Called by the build server when it finished a job (and requires Greg's help in notifying)
@app.route('/build', methods=['POST'])
def build():
  headers = {k:request.headers[k] for k in request.headers.keys()}
  querystring = {k:request.args[k] for k in request.args.keys()}
  payload = request.data
  if not querystring.has_key('builder'): return 'missing builder querystring',500
  greg.logic.build(querystring['builder'],payload,headers,querystring)

@app.route('/')
def root():
  return 'I am Greg'

def run():
  import os
  if os.environ.has_key('DEBUG'): app.debug = True
  app.run()

if __name__ == '__main__':
    run()
