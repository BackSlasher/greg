#!/usr/bin/env python
import argparse
import greg.config

def main():
    parser = argparse.ArgumentParser(description='Integrate your build server and source control')
    parser.add_argument('--config', default='config.yaml', help='Path to config file')
    parser.add_argument('--fix-hooks', action='store_const', const='fixhooks', dest='action', help='Ensure repos alert greg on changes')
    parser.add_argument('--url', help='Base URL for greg')
    args = parser.parse_args()
    print args

    # Establish config filename
    greg.config.get_config(args.config)

    if args.action == 'fixhooks':
        fix_hooks(args)
    #TODO handle http server using greg.server as well
    #import greg.server
    #greg.server.start()
    else:
      print 'Not doing anything'

def fix_hooks(args):
    import greg.provider
    import greg.builder
    from urlparse import urlparse
    import re
    # Reject when no url
    if not args.url:
        raise Exception('Must have URL to fix hooks')
    my_url = args.url
    # Enumerate all repo entries in config
    config = greg.config.get_config()
    for repo_conf in config.repos:
        provider = greg.provider.locate_bridge(repo_conf.provider)
        # Build proper URL
        provider_url = urlparse(my_url)
        provider_url = provider_url._replace(path=re.sub('/*$','/',provider_url.path)+'repo')
        provider_url = provider_url._replace(query='provider=%s&token=%s'%(repo_conf.provider,provider.incoming_token))
        # Enumerate over all organizations
        for org in repo_conf.organizations:
            # Find all repos that match the repo config
            all_repos = provider.list_repos(org)
            repos = filter(lambda repo: repo_conf.match(repo_conf.provider, org, repo), all_repos)
            for repo in repos:
                # Ensure webhooks on that repo
                provider.ensure_webhook(org,repo,provider_url.geturl())
    # Collect all jobs and builders
    jobs = set([(job.name,job.builder) for repo in config.repos for job in repo.jobs.values()])
    builders = set([job[1] for job in jobs])
    for builder_name in builders:
        builder_jobs = set([job[0] for job in jobs if job[1]==builder_name])
        builder = greg.builder.locate_bridge(builder_name)
        builder_url = urlparse(my_url)
        builder_url = builder_url._replace(path=re.sub('/*$','/',builder_url.path)+'builder')
        builder_url = builder_url._replace(query='builder=%s&token=%s'%(builder_name,builder.incoming_token))
        for job_name in builder_jobs:
            builder.ensure_webhook(job_name,builder_url.geturl())


if __name__ == "__main__":
    main()
