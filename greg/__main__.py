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
    # Reject when no url
    if not args.url:
        raise Exception('Must have URL to fix hooks')
    my_url = args.url
    #TODO complete
    # Enumerate all repo entries in config
    config = greg.config.get_config()
    print config.repos
    for repo_conf in config.repos:
        provider = greg.provider.locate_bridge(repo_conf.provider)
        # Enumerate over all organizations
        for org in repo_conf.organizations:
            # Find all repos that match the repo config
            all_repos = provider.list_repos(org)
            repos = filter(lambda repo: repo_conf.match(repo_conf.provider, org, repo), all_repos)
            for repo in repos:
                # Ensure webhooks on that repo
                #print repo_conf.provider,org,repo
                provider.ensure_webhook(org,repo,my_url)
                #pass

if __name__ == "__main__":
    main()
