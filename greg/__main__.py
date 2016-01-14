#!/usr/bin/env python
import argparse
import greg.config

def main():
    parser = argparse.ArgumentParser(description='Integrate your build server and source control')
    parser.add_argument('--config', default='config.yaml', help='Path to config file')
    parser.add_argument('--fixhooks', action='store_const', const='fixhooks', dest='action', help='Ensure repos alert greg on changes')
    parser.add_argument('-url', help='Base URL for greg')
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
    # Reject when no url
    if not args.url:
        raise Exception('Must have URL to fix hooks')
    #TODO complete

if __name__ == "__main__":
    main()
