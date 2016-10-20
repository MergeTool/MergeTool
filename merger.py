#!/usr/bin/env python3
import argparse
from pathlib import Path

from merge.choice import Choice
from merge.project_merge import ProjectMerge


### changes `conflicts`
def resolve_conflicts_event_loop(project_merge: ProjectMerge):
    # file_index = 0
    # file_merge = project_merge.files[file_index]
    for file_merge in project_merge.files:

        if file_merge.is_resolved():
            continue

        unresolved_conflicts = list(range(len(file_merge.conflicts)))
        unresolved_conflict_index = 0
        while True:
            if not unresolved_conflicts:
                print("All conflicts have been resolved")
                project_merge.compile_print()
                break

            unresolved_conflict_index %= len(unresolved_conflicts)
            conflict = file_merge.conflicts[unresolved_conflicts[unresolved_conflict_index]]

            print("\n left = ")
            print(conflict.left)
            print("\n right = ")
            print(conflict.right)

            response = input(
                "Choose what to leave ('R' = right, 'L' = left, 'B' = both, "
                "'N' = next conflict, 'P' = previous conflict 'C' = compile, 'Q' = quit): \n")

            if not response:
                continue

            switch = response.lower()[0]

            if switch == 'l':
                conflict.select(Choice.left)
                unresolved_conflicts.pop(unresolved_conflict_index)
                unresolved_conflict_index += 1
            elif switch == 'r':
                conflict.select(Choice.right)
                unresolved_conflicts.pop(unresolved_conflict_index)
                unresolved_conflict_index += 1
            elif switch == 'b':
                conflict.select(Choice.both)
                unresolved_conflicts.pop(unresolved_conflict_index)
                unresolved_conflict_index += 1
            elif switch == 'p':
                unresolved_conflict_index -= 1
            elif switch == 'n':
                unresolved_conflict_index += 1
            elif switch == 'c':
                project_merge.compile_print()
            elif switch == 'q':
                print("Left unresolved %d conflicts" % len(unresolved_conflicts))
                return
            else:
                continue


def parse_cli_args():
    parser = argparse.ArgumentParser(description='Resolves conflicts in a file')

    parser.add_argument('project_path', default='.', help='folder with the top-level Makefile')
    parser.add_argument('--verbose', dest='verbose', action='store_true')

    defaul_behaviour_group = parser.add_mutually_exclusive_group()
    defaul_behaviour_group.add_argument('-ours', action='store_true')
    defaul_behaviour_group.add_argument('-theirs', action='store_true')
    defaul_behaviour_group.add_argument('-union', action='store_true')

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


if __name__ == "__main__":
    args = parse_cli_args()
    project_path = Path(args.project_path)

    if not project_path.is_dir():
        print("%s is not a folder" % project_path)
        quit()

    makefile_path = project_path / "Makefile"
    if not makefile_path.is_file():
        print("Could not find a Makefile at %s" % makefile_path)
        print("Unable to build the project")
        quit()

    tmp_path = project_path.parent / ("~" + str(project_path.parts[-1]))
    merge = ProjectMerge.parse(project_path, tmp_path)

    if merge.is_resolved():
        print("The project %s has no conflicts to resolve" % project_path)
        quit()

    if [f for f in merge.files if f.path == makefile_path and not f.is_resolved()]:
        print("Makefile cannot be in the merging state")
        quit()

    merge.select_all(args.choice)

    resolve_conflicts_event_loop(merge)  # changes `merge`

    merge.compile_print()
