
import greg.bridge_builder
import greg.bridge_provider
# Conatins all functions used to respond to events

def repo(payload):
  # Parse payload
  # Get action (comment / push)
  # If comment, then:
  #    If "greg please" then start merge procedure
  #    If "greg OK?" then check merge prereqs, but answer "yes" or "no" in comment
  # If push, then
  #  Invoke test job if any
  print 'not yet'

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

