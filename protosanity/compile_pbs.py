#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from grpc_tools import protoc
import re
from glob import glob
import warnings

try:
    import mypy_protobuf
    HAS_MYPY_PROTOBUF = True
except ImportError:
    HAS_MYPY_PROTOBUF = False


def text_has_service(s):
    """Check if a line in a file matches protobuf service definition

    Example:
        >>> text_has_service('    service  foo {')
        True
        >>> text_has_service('// service nope')
        False
        >>> lines = ['//some file', 'junk', '...', ' service  foo {', '    rpc Timeit (Empty) returns (TimeMsg) {}', '}']
        >>> any(text_has_service(l) for l in lines)
        True

    """
    pat = re.compile("^\s*service\s+.+$")
    if re.search(pat, s):
        return True
    return False


def get_package(protofile_path):
    pat = re.compile(r"^\s*package\s(?P<package>[\w\.]+)+;$")
    with open(protofile_path) as fp:
        for line in fp.readlines():
            res = re.search(pat, line)
            if res:
                out = res.groupdict().get('package', None)
                if out is not None:
                    return out

    raise RuntimeError("Could not find package in proto file: {}".format(protofile_path))


def has_service(protofile_path):
    with open(protofile_path) as fp:
        return any(text_has_service(l) for l in fp.readlines())


def form_command(protofile_path, target_path='.'):
    commands = [
        '--proto_path=' + target_path,
        '--python_out=' + target_path,
        '--grpc_python_out=' + target_path,
    ]
    if HAS_MYPY_PROTOBUF:
        commands.append('--mypy_out=' + target_path)

    commands.append(protofile_path)
    return commands


def compile_protobufs(proto_path='pkgname/proto', relpath='', *args):
    """compile the protobuf files.
    A few notes:
        - Madness this way lies.
        - Protoc/protobuf is VERY TOUCHY when it comes to python, paths, and
            packages. This is likely a continuous WIP as I figure out better
            patterns and methods.
        - I think the dot matters, sometimes.
        - Running `python -m grpc_tools.protoc` seems to have different behavior
            than calling it through this function, because of the final
            ['-I{}'.format(proto_include)]
        - If you want typical package namespacing, you are kinda stuck with
            repodir/pkgname/foobar/qux.proto which generates
            repodir/pkgname/foobar/qux_pb2.py if you want
            from pkgname.foobar import qux
        - As such, I have yet to figure out a way to leverage built-in libs
            such as google/protobuf/wrappers.proto
        - `python setup.py bdist_wheel` seems to inevitably generate the
            _pb files in the source tree. Maybe this is telling me something

    We want to emulate this command:
    python -m grpc_tools.protoc --proto_path=pygrpc/proto --python_out=. \
        --grpc_python_out=. pygrpc/proto/pygrpc/*.proto
    """

    print('<compile_pb:proto_path> {}'.format(proto_path))
    basepath = os.getcwd()
    # proto_path = os.path.join(dirname, protod)
    if relpath:
        basepath = relpath
        proto_path = os.path.relpath(proto_path, basepath)
        os.chdir(basepath)
        print("Rooting at: {}".format(basepath))
    protofile_dir = os.path.join('.', proto_path)
    print('<compile_pb:protofile_dir> {}'.format(proto_path))
    if not os.path.exists(protofile_dir):
        raise FileNotFoundError("Unable to locate directory with protofiles")
    file_path = os.path.join(protofile_dir, '{filename}')

    filenames = glob(file_path.format(filename='*.proto'))
    print('<compile_pb> {}'.format(proto_path))
    print('<compile_pb> {}'.format(filenames))

    for fn in filenames:
        cmdf = form_command(fn)
        print('<compile_pb> protoc {}'.format(cmdf))
        pkg = get_package(fn)
        expected_dir = os.path.join('.', *pkg.split('.'))
        if expected_dir != os.path.dirname(fn):
            msg = '<!><!><!><!>\n' \
                  'Package did not match expected directory structure. This will probably fail.' \
                  '\nFile: {}\nPackage: {}\nExpected: {}\n[!][!][!][!]'
            warnings.warn(msg.format(fn, pkg, expected_dir))

        out = protoc.main(cmdf)
        if out:
            raise RuntimeError(
                'Protobuf failed. Run Setup with --verbose to see why'
            )


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        raise ValueError('Usage: python -m protosanity.compile_pbs path/to/proto/dir')
    compile_protobufs(*sys.argv[1:])
