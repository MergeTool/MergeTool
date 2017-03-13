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
import re
from pprint import pprint

import sys
from clang.cindex import CursorKind, Index, TranslationUnit, Cursor, conf, callbacks


def get_diag_info(diag):
    return {'severity': diag.severity,
            'location': diag.location,
            'spelling': diag.spelling,
            'ranges': diag.ranges,
            'fixits': diag.fixits}


def get_cursor_id(cursor, cursor_list=[]):
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
    children = [get_info(c, depth + 1)
                for c in get_children_r(node)]
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


def get_short_info(node, depth=0):
    children = [get_short_info(c, depth + 1)
                for c in get_children_r(node)]
    return [
            node.kind,
            node.extent.start.line,
            children]

def foreach_child(node, op, depth=0):
    op(node)
    if node.kind != CursorKind.INCLUSION_DIRECTIVE:
        for ch in node.get_children():
            foreach_child(ch, op, depth + 1)


def abstract_syntax_tree(path: str) -> TranslationUnit:
    file = open(path)
    text = file.read()
    text = re.sub(r'#include((<\w+>)|("\w+"))', '', text)

    index = Index.create()
    translation_unit = index.parse(path, unsaved_files=[(path, text)])

    if not translation_unit:
        print("unable to load input", file=sys.stderr)

    return translation_unit


def extract_children(root: Cursor, kind_list: [CursorKind]) -> [Cursor]:
    nodes = []
    try:
        if root.kind in kind_list:
            nodes.append(root)
    except ValueError:
        pass

    for ch in get_children_r(root):
        nodes.extend(extract_children(ch, kind_list))

    return nodes


def get_children_r(cursor: Cursor):
    def visitor(child, parent, children):
        assert child != conf.lib.clang_getNullCursor()

        # Create reference to TU so it isn't GC'd before Cursor.
        child._tu = cursor._tu
        children.append(child)
        return 2  # recurse

    children = []
    conf.lib.clang_visitChildren(cursor, callbacks['cursor_visit'](visitor), children)
    return iter(children)

def main():
    from clang.cindex import Config
    Config.set_library_file("/usr/local/opt/llvm/lib/libclang.dylib")

    path = "/Users/voddan/Programming/Parallels/MergeTool/prototype/~testproject/prog.cpp"
    ast = abstract_syntax_tree(path)
    root = ast.cursor

    # pprint(('nodes', get_info(root)))
    pprint(get_short_info(root))


    def action(n):
        # if n.kind == CursorKind.IF_STMT:
        print("%s @ %s" % (n.kind, n.location))

    # foreach_child(root, action)



if __name__ == '__main__':
    main()
