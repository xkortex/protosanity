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
from foolib.util import time_ns


DEFAULT_PORT = 45654


def beat():
    print('.', end='', flush=True)
    time.sleep(0.48)


def add_time_to_pb(msg: common_pb2.TimeMsg) -> common_pb2.TimeMsg:
    msg.time_ns_dst = time_ns()
    return msg


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

    def Timeit(self, request: common_pb2.Empty, context) -> common_pb2.TimeMsg:
        # time.sleep(0.01)
        return common_pb2.TimeMsg(time_ns=time_ns())

    def TimeBurst(self, request: common_pb2.TimeMsg, context):
        for i in range(3):
            yield common_pb2.TimeMsg(time_ns_src=request.time_ns_src, time_ns_dst=time_ns())

    def TimeStream(self, request_iterator, context):
        yield from map(add_time_to_pb,
                       map(lambda _: common_pb2.TimeMsg(),
                           request_iterator()))

    def TimeBidiStream(self, request_iterator, context):
        yield from map(add_time_to_pb, request_iterator())

    def StrBidiStream(self, request_iterator, context):
        i = 0
        for req in request_iterator:
            print(req, flush=True)
            beat()
            beat()
            beat()
            beat()
            print('? REPLY', flush=True)
            yield common_pb2.SomeMessage(msg='!Howdy, this is server {}!'.format(i))
            print(i)
            beat()
            beat()
            beat()
            beat()
            print('! RECEIVE', flush=True)
            i +=1

    def CauseError(self, request, context):
        raise Exception('OOPS OMG WTF did what you asked, boss')

    def SomeReply(self, request, context: grpc.ServicerContext):

        print(context.peer(), flush=True)
        time.sleep(5)
        return common_pb2.SomeMessage(msg='bar')


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

    # Disable port reuse cause it can lead to weird bugs if you leave a process running
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=3), options=(('grpc.so_reuseport', 0),))
    servicer = Subprocesser()
    myservice_pb2_grpc.add_ProcessorServicer_to_server(
        servicer, server)
    server.add_insecure_port(hostport)
    print('starting server on {}'.format(hostport))
    print(servicer.__dict__)
    server.start()
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    args = arg_parser().parse_args()
    serve(args.host, args.port)
