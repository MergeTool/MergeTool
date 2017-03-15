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

import itertools
from clang.cindex import CursorKind, Index, TranslationUnit, Cursor, conf, callbacks


def diag_info(diag):
    return {'severity': diag.severity,
            'location': diag.location,
            'spelling': diag.spelling,
            'ranges': diag.ranges,
            'fixits': diag.fixits}


def info(node):
    return {'id': get_cursor_id(node),
            'kind': node.kind,
            'usr': node.get_usr(),
            'spelling': node.spelling,
            'location': node.location,
            'extent.start': node.extent.start,
            'extent.end': node.extent.end,
            'is_definition': node.is_definition(),
            'definition id': get_cursor_id(node.get_definition()),
            'children': node.get_children}


def short_info_tree(node: Cursor, depth=0):
    children = [short_info_tree(c, depth + 1)
                for c in node.get_children()]
    return short_info(node) + [children]

def short_info(node):
    return [node.kind, node.extent.start.line]


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
    children = get_children_r(root)
    nodes = []
    for ch in children:
        try:
            if ch.kind in kind_list:
                nodes.append(ch)
        except ValueError:
            pass

    return nodes


def get_children_r(cursor: Cursor):
    for ch in cursor.get_children():
        yield ch
        for r_ch in get_children_r(ch):
            yield r_ch


def get_child(self: Cursor, n: int) -> Cursor:
    return list(self.get_children())[n]

Cursor.child = get_child


def main():
    from clang.cindex import Config
    Config.set_library_file("/usr/local/opt/llvm/lib/libclang.dylib")

    path = "/Users/voddan/Programming/Parallels/MergeTool/prototype/~testproject/prog.cpp"
    ast = abstract_syntax_tree(path)
    root = ast.cursor

    # [[CursorKind.USING_DIRECTIVE, 6], [CursorKind.FUNCTION_DECL, 8]]
    # [[CursorKind.COMPOUND_STMT, 9]]
    # [[CursorKind.DECL_STMT, 10], [CursorKind.IF_STMT, 13], [CursorKind.IF_STMT, 20], [CursorKind.FOR_STMT, 26], [CursorKind.RETURN_STMT, 55]]
    # [[CursorKind.BINARY_OPERATOR, 26], [CursorKind.BINARY_OPERATOR, 26], [CursorKind.COMPOUND_STMT, 27]]
    # [[CursorKind.BINARY_OPERATOR, 37], [CursorKind.BINARY_OPERATOR, 39], [CursorKind.IF_STMT, 40], [CursorKind.BINARY_OPERATOR, 45], [CursorKind.UNARY_OPERATOR, 46], [CursorKind.IF_STMT, 48]]

    main_8 = root.child(1).child(0)
    for_26 = main_8.child(3)
    for_28 = for_26.child(3).child(0)
    if_30 = for_28.child(3).child(0)
    if_40 = for_26.child(3).child(3)
    if_45 = if_40.child(1).child(1)

    node = if_30
    pprint([short_info(ch) for ch in node.get_children()])
    print('\n')

    pprint([short_info(ch) for ch in get_children_r(root)])
    print('\n')

    pprint([short_info(ch) for ch in extract_children(root, [CursorKind.IF_STMT, CursorKind.FOR_STMT])])
    print('\n')



if __name__ == '__main__':
    main()
