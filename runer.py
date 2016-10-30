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
    if opts.maxDepth is not None and depth >= opts.maxDepth:
        children = None
    else:
        for ch in node.get_children():
            foreach_child(ch, op, depth + 1)


def main():
    from clang.cindex import Index
    from clang.cindex import CursorKind
    from pprint import pprint

    from optparse import OptionParser, OptionGroup

    global opts

    from clang.cindex import Config
    Config.set_library_file("/usr/local/opt/llvm/lib/libclang.dylib")

    parser = OptionParser("usage: %prog [options] {filename} [clang-args*]")
    parser.add_option("", "--show-ids", dest="showIDs",
                      help="Compute cursor IDs (very slow)",
                      action="store_true", default=False)
    parser.add_option("", "--max-depth", dest="maxDepth",
                      help="Limit cursor expansion to depth N",
                      metavar="N", type=int, default=None)
    parser.disable_interspersed_args()
    (opts, args) = parser.parse_args()

    if len(args) == 0:
        parser.error('invalid number arguments')

    index = Index.create()
    translation_unit = index.parse(None, args)
    if not translation_unit:
        parser.error("unable to load input")

    # pprint(('diags', map(get_diag_info, translation_unit.diagnostics)))
    # pprint(('nodes', get_info(translation_unit.cursor)))

    root = translation_unit.cursor

    def action(n):
        if n.kind == CursorKind.IF_STMT:
            print("%s @ %s" % (n.kind, n.location))

    foreach_child(root, action)

    # children = root.get_children()
    # for ch in children:
    #     print("%s @ %s" % (ch.kind, ch.location))


if __name__ == '__main__':
    main()
