from merge.choice import Choice
from merge.project_merge import ProjectMerge
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