#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Receives gRPC calls and converts them to subprocess calls"""

import sys
import time
import traceback
import subprocess as subp
from concurrent import futures

import grpc

from foolib.protobuf import myservice_pb2, myservice_pb2_grpc
from foolib.protobuf import common_pb2


DEFAULT_PORT = 45654


class Subprocesser(myservice_pb2_grpc.ProcessorServicer):

    def TestIO(self, request: myservice_pb2.ProcRequest,
              context) -> myservice_pb2.ProcResponse:
        print('Got request at {}'.format(time.ctime()), flush=True)
        result = myservice_pb2.ProcResponse()
        try:
            cmd = [request.name] + [a for a in request.args]
            print('$ {}'.format(' '.join(cmd)), flush=True)
            p = subp.run(cmd, stdout=subp.PIPE, stderr=subp.PIPE)
            result.stdout = p.stdout
            result.stderr = p.stderr
            result.status = p.returncode
        except Exception as e:
            exc_type, exc_val, exc_tb = sys.exc_info()
            # print('{}: {}'.format(exc_type, exc_val))
            print(traceback.format_exc())
            print('...___---')
            result.err = common_pb2.MyImportedError(
                exc_type=exc_type, exc_val=exc_val, traceback=traceback.format_exc()
            )
            raise

        print('Complete', flush=True)
        return result


def arg_parser():
    import argparse
    parser = argparse.ArgumentParser(description="""Run subprocess as RPC""")

    parser.add_argument(
        "-H", "--host", default=None, action="store", type=str,
        help="Host to run RPC service on")
    parser.add_argument(
        "-P", "--port", default=DEFAULT_PORT, action="store", type=str,
        help="start of port range to run RPC service on")
    return parser


def serve(host=None, port=DEFAULT_PORT):
    if host is None:
        host = '[::]'

    hostport = ':'.join([host, str(port)])

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    myservice_pb2_grpc.add_ProcessorServicer_to_server(
        Subprocesser(), server)
    server.add_insecure_port(hostport)
    print('starting server on {}'.format(hostport))
    server.start()
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    args = arg_parser().parse_args()
    serve(args.host, args.port)
