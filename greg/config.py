import re
import yaml

# Holds configuration data for our application

class JobConfig:
  def __init__(self, dictionary):
    self.name = dictionary['name']
    self.builder = dictionary['builder']


class RepoConfig:
  # provider: One of github, bitbucket
  # organizations: List of organizations (users) to search repos in
  # names: List of names (possibly regexes) for repos
  # build job
  def __init__(self, provider, organizations, names,jobs):
    self.provider = provider
    self.organizations = organizations
    self.names = set()
    self.names_regexps = set()
    for n in names:
      if n[0]=='/' and n[-1]=='/': #regex
        self.names_regexps.add(re.compile(n[1:-1]))
      else:
        self.names.add(n)
    self.jobs = { k:JobConfig(v) for k,v in jobs.iteritems() }

  # Parses dictionary to a new repoconfig
  @staticmethod
  def parse(dict_piece):
     return RepoConfig(
         provider=dict_piece['provider'],
         organizations=set(dict_piece['organizations']),
         names=dict_piece['names'],
         jobs=dict_piece['jobs'],
         )

  # Whether a specific repo matches this
  def match(self, provider, organization, name):
    return (
            (self.provider == provider) and
            (organization in self.organizations) and
            (
             name in self.names or
             any((
               pattern.search(name) for pattern in self.names_regexps
               ))
            )
           )

class Config:
  def __init__(self, repos, providers, builders):
    self.repos=repos
    self.providers=providers
    self.builders=builders

  @staticmethod
  def parse(dict_piece):
    repos=map(lambda p: RepoConfig.parse(p), dict_piece['repos'])
    providers=dict_piece['providers']
    builders=dict_piece['builders']
    return Config(repos,providers,builders)

  @staticmethod
  def load_file(filename):
    with open(filename, 'r') as f:
      raw = f.read()
    dic = yaml.load(raw)
    return Config.parse(dic)

  def credentials(self, provider):
    provider_dict = self.providers[provider]
    return [provider_dict[x] for x in ['username', 'password']]

  def incoming_token(self, provider):
    provider_dict = self.providers[provider]
    return provider_dict['incoming_token']

  def provider_source(self,provider):
    provider_dict = self.providers[provider]
    return provider_dict['source']

  def get_repo_config(self, provider, organization, name):
    return next((rc for rc in self.repos if rc.match(provider, organization, name)),None)

  # Get job type for a repo.
  # Handle missing jobs by returning None
  def get_job(self, provider, organization, name, job_type):
    repo_config = self.get_repo_config(provider, organization, name)
    return repo_config.jobs.get(job_type,None)

config=None
#TODO make it a proper method?
def get_config(filename='config.yaml'):
    global config
    if config is None: config = Config.load_file(filename)
    return config
