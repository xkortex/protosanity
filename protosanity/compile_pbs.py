#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from glob import glob
import warnings
from grpc_tools import protoc

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


def form_command(protofile_path, target_path='.', plugins=(), other_proto_paths=()):
    # todo: add switching for automatic grpc build, see `has_service`
    commands = [
        '--proto_path=' + target_path,
        '--python_out=' + target_path,
    ]
    commands += ['--proto_path=' + pp for pp in other_proto_paths]

    HAS_SERVICE = has_service(protofile_path)
    HAS_GO = any(x in plugins for x in ["go", "grpc_go"])

    if HAS_SERVICE:
        commands.append('--grpc_python_out=' + target_path)
        if 'grpc_go' in plugins:
            commands.append('--go_out=plugins=grpc:' + target_path)
    else:
        if HAS_GO:
            commands.append('--go_out=' + target_path)
    if HAS_GO:
        # if you don't have this option, protoc will put the file at
        # $BASEDIR/go/package/path
        commands.append('--go_opt=paths=source_relative')

    if HAS_MYPY_PROTOBUF:
        commands.append('--mypy_out=' + target_path)

    commands.append(protofile_path)
    print(commands)
    return commands


def compile_protobufs(proto_path='pkgname/proto', relpath='', plugins=(), other_proto_paths=(), *args):
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
        cmdf = form_command(fn, plugins=plugins, other_proto_paths=other_proto_paths)
        print('<compile_pb> protoc {}'.format(' '.join(cmdf)))
        pkg = get_package(fn)
        expected_dir = os.path.join('.', *pkg.split('.'))
        # todo: actually seems like this can work as long as the last part of the namespace matches
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


def arg_parser():
    import argparse
    parser = argparse.ArgumentParser(description="""Helper script for compiling protobuf files.
    Usage: python -m protosanity.compile_pbs path/to/proto_dir
    
    If proto_dir is absolute, you should specify -r /base/path such that the relpath of the
    proto dir matches the package structure. E.g. if you have the structure:
    /home/user/proj/foo/bar/*.proto
    each with `package "foo.bar"`, you should run
    
    `python -m protosanity.compile_pbs -r /home/user/proj /home/user/proj/foo/bar` 
    
    Plugin options:
     - go           - compile go protobufs
     - grpc_go      - compile go grpc (implies go protobuf) 
    
    """)

    parser.add_argument(
        "-r", "--relpath_start", default=None, action="store", type=str,
        help="Specify a base path of the proto dir. This may be needed if executing from"
        "other than the base directory. "
    )
    parser.add_argument(
        "-o", "--output_dir", default=None, action="store", type=str,
        help="Output directory")
    parser.add_argument('-p', '--plugin', action='append',
                        help='Specify any number of plugins with `-p plugname`')

    parser.add_argument("-I", "--proto_path", action="append", default=[],
                        help="Additional proto_path to add to commands")
    parser.add_argument(
        'input', nargs=1, type=str,
        help="Path to directory containing .proto files")
    return parser


if __name__ == '__main__':
    try:
        args = arg_parser().parse_args()
    except ValueError:
        msg = """Invalid arguments specified.
        Usage: python -m protosanity.compile_pbs path/to/proto/dir"""
        raise ValueError(msg)

    print(args)
    allowed_plugins = ['go', 'grpc_go']
    plugins = args.plugin or []
    bad_plugins = list(filter(lambda x: x not in allowed_plugins, plugins))
    if bad_plugins:
        raise ValueError('Not valid plugin(s): {}'.format(', '.join(bad_plugins)))
    compile_protobufs(args.input[0], args.relpath_start, plugins=plugins, other_proto_paths=args.proto_path)
