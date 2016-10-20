#!/usr/bin/env python3
import argparse
from pathlib import Path

from merge.choice import Choice
from merge.project_merge import ProjectMerge


### changes `conflicts`
from ui.index import Index


def resolve_conflicts_event_loop(project_merge: ProjectMerge):
    files = Index(project_merge.files)
    conflicts = None

    while True:
        if files.is_empty():
            print("Project %s has no files to merge" % project_merge.path)
            return

        if not conflicts:
            conflicts = Index(files.value().conflicts)

        if conflicts.is_empty():
            print("File %s has no conflicts to resolve" % files.value().path)
            files.delete()
            conflicts = None
            continue

        print("\n left = ")
        print(conflicts.value().left)
        print("\n right = ")
        print(conflicts.value().right)

        response = input(
            "Choose what to leave ('L' = left, 'R' = right, 'B' = both, "
            "'N' = next conflict, 'P' = previous conflict, "
            "'NF' = next file, 'PF' = previous file, "
            "'V' = view the file, 'C' = compile, "
            "'W' = write to tmp, `WF` = override the project files, "
            "'Q' = quit): \n")

        switch = (response + "  ").lower()[0:2]

        if switch == 'l ':
            conflicts.value().select(Choice.left)
            conflicts.delete()
        elif switch == 'r ':
            conflicts.value().select(Choice.right)
            conflicts.delete()
        elif switch == 'b ':
            conflicts.value().select(Choice.both)
            conflicts.delete()
        elif switch == 'n ':
            conflicts.next()
        elif switch == 'p ':
            conflicts.prev()
        elif switch == 'nf':
            files.next()
            conflicts = Index(files.value().conflicts)
        elif switch == 'pf':
            files.prev()
            conflicts = Index(files.value().conflicts)
        elif switch == 'v ':
            print("=== [%d conflicts] === %s ==== " % (conflicts.size_left(), files.value().path))
            print(files.value().result())
        elif switch == 'c ':
            project_merge.compile_print()
        elif switch == 'w ':
            project_merge.write_result_tmp()
        elif switch == 'wf':
            project_merge.write_result(project_merge.path)
        elif switch == 'q ':
            print("Left unresolved %d files" % files.size_left())
            return
        else:
            print("Unsupported command %s" % response)


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

    merge.select_all(args.choice)

    if merge.is_resolved():
        print("The project %s has no conflicts to resolve" % project_path)
        quit()

    if [f for f in merge.files if f.path == makefile_path and not f.is_resolved()]:
        print("Makefile cannot be in the merging state")
        quit()

    resolve_conflicts_event_loop(merge)  # changes `merge`

    merge.compile_print()
