#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import six
import google.protobuf.descriptor_pb2 as d
from google.protobuf import json_format
from google.protobuf.compiler import plugin_pb2 as plugin_pb2
from mypy_protobuf import  Descriptors, PkgWriter, HEADER


def generate_mypy_stubs(request, response, quiet):
    # type: (plugin_pb2.CodeGeneratorRequest, plugin_pb2.CodeGeneratorResponse, bool) -> None
    descriptors = Descriptors(request)
    for name, fd in six.iteritems(descriptors.to_generate):
        pkg_writer = PkgWriter(fd, descriptors)
        pkg_writer.write_enums(fd.enum_type)
        pkg_writer.write_messages(fd.message_type, "")
        pkg_writer.write_extensions(fd.extension)
        if fd.options.py_generic_services:
            pkg_writer.write_services(fd.service)

        assert name == fd.name
        assert fd.name.endswith(".proto")
        output = response.file.add()
        output.name = fd.name[:-6].replace("-", "_").replace(".", "/") + "_pb2.json"
        for i in range(len(request.proto_file)):
            request.proto_file[i].ClearField('source_code_info')
        output.content = json_format.MessageToJson(request)
        if not quiet:
            print("Writing json to", output.name, file=sys.stderr)


def main():
    # type: () -> None
    # Read request message from stdin
    # print("Deep within the machinations of the protobuf plugin...")
    data = sys.stdin.buffer.read()

    # Parse request
    request = plugin_pb2.CodeGeneratorRequest()
    request.ParseFromString(data)

    # print(request)
    # Create response
    response = plugin_pb2.CodeGeneratorResponse()
    generate_mypy_stubs(request, response, "quiet" in request.parameter)
    # with open('/tmp/peek.json', 'w') as fp:
    #     fp.write()

    # Serialise response message
    output = response.SerializeToString()

    # Write to stdout
    sys.stdout.buffer.write(output)


if __name__ == "__main__":
    main()
