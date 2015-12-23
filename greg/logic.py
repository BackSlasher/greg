import re
import collections
import greg.bridge_builder
import greg.bridge_provider
import greg.config
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
def repo(provider_type,payload,headers={},querystring={}):
  # Parse payload
  probri = greg.bridge_provider.locate_bridge(provider_type)
  payload = probri.parse_payload(payload,headers,querystring)
  config = greg.config.get_config()
  # Get action (comment / push)
  if payload['event']['type'] == 'pr:comment': # Comment
    escaped_string = re.sub('[^a-z]+','',payload['event']['text']).lower()
    if  escaped_string == 'gregplease': # Greg please
      merge_check = allowed_merge(payload)
      if merge_check.allowed:
          # Find the correct job to run
          merge_job = config.get_job(
                  payload['repo']['provider'],
                  payload['repo']['organization'],
                  payload['repo']['name'],
                  'merge'
                  )
          if merge_job:
              # Start merge job
              builbri = greg.bridge_builder.locate_bridge(merge_job.builder)
              #TODO document parameters better
              builbri.start_build(merge_job.name,{
                  'PROVIDER': payload['repo']['provider'],
                  'USER': payload['repo']['organization'],
                  'REPO': payload['repo']['name'],
                  # TODO merge from specifc commit and not branch name
                  'COMMIT': payload['event']['pr']['src_branch'],
                  'TARGET_BRANCH': payload['event']['pr']['dst_branch'],
                  'PR': payload['event']['pr']['id'],
                  'REPORT': True,
                  })
              #TODO write a message that build started?
          else:
              # Notify that we don't have a merge job
              probri.post_pr_message(payload['repo']['organization'], payload['repo']['name'], 'No merge job found. Merge manually?')
      else:
          # Notify that we won't merge because issues
          reason_list = '\n'.join([ '* '+i  for i in merge_check.issues])
          probri.post_pr_message(payload['repo']['organization'], payload['repo']['name'], '**Will not merge**  \n'+reason_list)
    elif escaped_string == 'gregok': # Greg OK
      merge_check = allowed_merge(payload)
      if merge_check.allowed:
          probri.post_pr_message(payload['repo']['organization'], payload['repo']['name'], '**Ready to merge**')
      else:
          reason_list = '\n'.join([ '* '+i  for i in merge_check.issues])
          probri.post_pr_message(payload['repo']['organization'], payload['repo']['name'], '**Not ready to merge**  \n'+reason_list)
    else:
      #TODO log ignoring
      pass
  elif payload['event']['type'] == 'push': # Commit push
      test_job = config.get_job(
              payload['repo']['provider'],
              payload['repo']['organization'],
              payload['repo']['name'],
              'test'
              )
      if test_job:
          builbri = greg.bridge_builder.locate_bridge(test_job.builder)
          for change in payload['event']['changes']:
              builbri.start_build(test_job.name, {
                  'PROVIDER': payload['repo']['provider'],
                  'USER': payload['repo']['organization'],
                  'REPO': payload['repo']['name'],
                  # TODO merge from specifc commit and not branch name
                  'COMMIT': change['commit'],
                  'REPORT': True,
                  })
      else:
          #TODO log ignoring because no test job
          pass

  else:
      # No matching event, can't do anything
      raise Exception('No such event type "%s"' % payload['event']['type'])

# Called from the build server
def build(builder_type,body,headers={},querystring={}):
  # Find builder bridge and parse job
  bubri = greg.bridge_builder.locate_bridge(builder_type)
  job_result = bubri.parse_payload(body,headers,querystring)
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

