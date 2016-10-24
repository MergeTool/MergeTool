import argparse

from merge.choice import Choice


def parse_cli_args():
    parser = argparse.ArgumentParser(description='Resolves conflicts in a file')

    parser.add_argument('project_path', default='.', help='folder with the top-level Makefile')
    parser.add_argument('--verbose', dest='verbose', action='store_true')

    default_behaviour_group = parser.add_mutually_exclusive_group()
    default_behaviour_group.add_argument('-ours', action='store_true')
    default_behaviour_group.add_argument('-theirs', action='store_true')
    default_behaviour_group.add_argument('-union', action='store_true')

    args = parser.parse_args()

    if args.ours:
        args.choice = Choice.left
    elif args.theirs:
        args.choice = Choice.right
    if args.union:
        args.choice = Choice.both
    else:
        args.choice = Choice.undesided

    return args