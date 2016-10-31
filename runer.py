#!/usr/bin/env python3

# ===- cindex-dump.py - cindex/Python Source Dump -------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
# ===------------------------------------------------------------------------===#

"""
A simple command line tool for dumping a source file using the Clang Index
Library.
"""

def get_diag_info(diag):
    return {'severity': diag.severity,
            'location': diag.location,
            'spelling': diag.spelling,
            'ranges': diag.ranges,
            'fixits': diag.fixits}


def get_cursor_id(cursor, cursor_list=[]):
    if not opts.showIDs:
        return None

    if cursor is None:
        return None

    # FIXME: This is really slow. It would be nice if the index API exposed
    # something that let us hash cursors.
    for i, c in enumerate(cursor_list):
        if cursor == c:
            return i
    cursor_list.append(cursor)
    return len(cursor_list) - 1


def get_info(node, depth=0):
    if opts.maxDepth is not None and depth >= opts.maxDepth:
        children = None
    else:
        children = [get_info(c, depth + 1)
                    for c in node.get_children()]
    return {'id': get_cursor_id(node),
            'kind': node.kind,
            'usr': node.get_usr(),
            'spelling': node.spelling,
            'location': node.location,
            'extent.start': node.extent.start,
            'extent.end': node.extent.end,
            'is_definition': node.is_definition(),
            'definition id': get_cursor_id(node.get_definition()),
            'children': children}

def foreach_child(node, op, depth=0):
    op(node)
    for ch in node.get_children():
        foreach_child(ch, op, depth + 1)


def main():
    from clang.cindex import Index
    from clang.cindex import CursorKind

    from clang.cindex import Config
    Config.set_library_file("/usr/local/opt/llvm/lib/libclang.dylib")

    global opts
    import sys

    if len(sys.argv) == 1:
        print('please provide a path to a source file', file=sys.stderr)

    path = sys.argv[1]
    file = open(path)
    text = file.read()

    index = Index.create()
    translation_unit = index.parse(path, unsaved_files=[(path, text)])
    if not translation_unit:
        print("unable to load input", file=sys.stderr)

    # pprint(('diags', map(get_diag_info, translation_unit.diagnostics)))
    # pprint(('nodes', get_info(translation_unit.cursor)))

    root = translation_unit.cursor

    def action(n):
        if n.kind == CursorKind.IF_STMT:
            print("%s @ %s" % (n.kind, n.location))

    foreach_child(root, action)


if __name__ == '__main__':
    main()
