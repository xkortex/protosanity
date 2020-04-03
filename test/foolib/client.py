import sys
import socket
import shlex

import grpc
from foolib.protobuf import myservice_pb2, myservice_pb2_grpc


HOST = 'localhost'
PORT = 45654


def run_client(host=None, port=PORT, cmd=None):
    if host is None:
        # host = socket.gethostname()
        host = 'localhost'

    if cmd is None:
        cmd = ['ls']
    else:
        cmd = shlex.split(cmd)

    hostport = ':'.join([host, str(port)])
    channel = grpc.insecure_channel(hostport)
    stub = myservice_pb2_grpc.ProcessorStub(channel)
    req = myservice_pb2.ProcRequest(name=cmd[0], args=cmd[1:])

    response = stub.TestIO(req)

    # print('Client received: {}'.format(response.message))
    return str(response)


def arg_parser():
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument(
        "-H", "--host", default=None, action="store", type=str,
        help="Host to run RPC service on")
    parser.add_argument(
        "-P", "--port", default=PORT, action="store", type=str,
        help="start of port range to run RPC service on")
    parser.add_argument(
        "-+", "--health", action="store_true",
        help="Run a health check")
    parser.add_argument(
        'cmd', nargs='?', default='ls', type=str,
        help="Command to run"
    )

    return parser


if __name__ == '__main__':
    # print('vprint on {}'.format(socket.gethostname()))
    args = arg_parser().parse_args()
    # print('{}'.format(args))

    if args.health:
        raise NotImplementedError('not ready')

    out = run_client(args.host, args.port, args.cmd)
    print(out)



