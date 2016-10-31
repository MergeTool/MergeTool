#!/usr/bin/env python3
from pathlib import Path

from ui.cli_args import parse_cli_args
from ui.cli_event_loop import resolve_conflicts_event_loop
from merge.project_merge import ProjectMerge


if __name__ == "__main__":
    from clang.cindex import Config
    Config.set_library_file("/usr/local/opt/llvm/lib/libclang.dylib")

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

    for file in merge.files:
        file.get_ast()

    merge.select_all(args.choice)

    if merge.is_resolved():
        print("The project %s has no conflicts to resolve" % project_path)
        quit()

    if [f for f in merge.files if f.path == makefile_path and not f.is_resolved()]:
        print("Makefile cannot be in the merging state")
        quit()

    resolve_conflicts_event_loop(merge)  # changes `merge`

    merge.compile_print()
