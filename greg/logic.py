import re
import collections
import greg.bridge_builder
import greg.bridge_provider
# Conatins all functions used to respond to events

# Whether a job is allowed to merge
def allowed_merge(payload):
  issues=[]
  ret_type = collections.namedtuple('merge_review', ['allowed','issues'])
  # Same repo (source and target)
  if not payload['event']['pr']['same_repo']:
      issues.append('Source repo isnt identical to target repo')
  # TODO My repo (not targeting foreign repo somehow)
  # All reviewers are OK with merging
  missing_approvers = set(payload['event']['pr']['reviewers']) - set(payload['event']['pr']['approvers'])
  if missing_approvers:
      issues.append('Missing approvals from: %s'%(missing_approvers))
  # Testing passed fine
  if not payload['event']['pr']['code_ok']:
      issues.append('Code did not pass validation')

  # Judgement
  return ret_type(not any(issues),issues)

# Called from the repository's webhooks
def repo(provider_type,payload,params={}):
  # Parse payload
  probri = greg.bridge_provider.locate_bridge(provider_type)
  payload = probri.parse_payload(payload,params)
  # Get action (comment / push)
  if payload['event']['type'] == 'pr:comment': # Comment
    escaped_string = re.sub('[^a-z]+','',payload['event']['text']).lower()
    if  escaped_string == 'gregplease': # Greg please
      pass
      # TODO Start merge procedure if existed and allowed
    elif escaped_string == 'gregok': # Greg OK
      # TODO Print merge prereqs and print message
      pass
    else:
      #TODO log ignoring
      pass
  elif payload['event']['type'] == 'push': # Commit push
      # TODO Invoke test job if any
      pass
  else:
      raise Exception('No such event type "%s"' % payload['event']['type'])
  print 'not yet'

# Called from the build server
def build(builder_type,body,params={}):
  # Find builder bridge and parse job
  bubri = greg.bridge_builder.locate_bridge(builder_type)
  job_result = bubri.parse_payload(body,params)
  #TODO find provider bridge
  probri = greg.bridge_provider.locate_bridge_by_url(job_result['source']['provider'])
  # return if job is not to be reported
  if not job_result['report']:
      #TODO log that skipping job
      return
  if job_result['context'] == 'merge':
      if job_result['good']:
        # TODO log that not reporting succesful merge
        return
      else:
        probri.post_pr_message(
          job_result['source']['organization'],
          job_result['source']['name'],
          job_result['pr'],
          ("Merge **failed**  \n%s" % (job_result['url']))
          )
  elif job_result['context'] == 'test':
    probri.post_commit_test(
      job_result['source']['organization'],
      job_result['source']['name'],
      job_result['source']['commit'],
      builder_type=builder_type,
      url=job_result['url'],
      result=job_result['good'],
    )
  else:
    raise Exception('No such job type "%s"' % job_result['context'])

