#!/usr/bin/env python
# -*- coding: utf-8 -*-

from grpc_tools import protoc


def protoc_main_minimal(command_arguments, proto_paths=()):
    """
    Same as `python -m grpc_tools.protoc` but without injecting
    ['-I{}'.format(proto_include)].
    This is a fix to be able to actually compile grpc proto files correctly when import is involved.
    """
    sys.exit(protoc.main(list(proto_paths) + command_arguments))


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        sys.stderr.write('Must provide arguments to protoc. Type `python -m protosanity.protoc -h` to show help\n')
        sys.exit(protoc.main(sys.argv[0]))

    protoc_main_minimal(sys.argv[1:])

