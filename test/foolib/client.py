import time
import shlex

import grpc
from foolib.protobuf import myservice_pb2, myservice_pb2_grpc, common_pb2
from foolib.util import time_ns


HOST = 'localhost'
PORT = 45654


def beat():
    print('.', end='', flush=True)
    time.sleep(0.48)


class Client(object):
    def __init__(self, host=None, port=PORT):
        if host is None:
            # host = socket.gethostname()
            host = 'localhost'
        self.host = host

        self.hostport = ':'.join([host, str(port)])
        self.channel = grpc.insecure_channel(self.hostport)
        self.stub = myservice_pb2_grpc.ProcessorStub(self.channel)


    def run_client(self, cmd=None):
        if cmd is None:
            cmd = ['ls']
        else:
            cmd = shlex.split(cmd)

        req = myservice_pb2.ProcRequest(name=cmd[0], args=cmd[1:])

        response = self.stub.TestIO(req)

        # print('Client received: {}'.format(response.message))
        return str(response)

    def cause_error(self):
        self.stub.CauseError(common_pb2.Empty())


    def test_latency(self):
        req = common_pb2.Empty()

        start = time_ns()
        response = self.stub.Timeit(req)
        end = time_ns()
        print('oneway: {:.6f} ms \nRTT   : {:.6f} ms'.format((response.time_ns - start)*1e-6, (end-start)*1e-6))

        # print('Client received: {}'.format(response.message))
        return str(response)


    def time_burst(self):
        msg = common_pb2.TimeMsg()
        msg.time_ns_src = time_ns()
        for res in self.stub.TimeBurst(msg):
            print('___')
            print(res)
            end = time_ns()
            print('oneway: {:.6f} ms \nRTT   : {:.6f} ms'.format((res.time_ns_dst - res.time_ns_src) * 1e-6, (end - res.time_ns_src) * 1e-6))


    def stream_some_times(self, count=5):

        def genny():
            for i in range(count):
                yield common_pb2.TimeMsg(time_ns_src=time_ns(),)

        for res in self.stub.TimeBidiStream(genny()):
            print(res)
            end = time_ns()
            print('oneway: {:.6f} ms \nRTT   : {:.6f} ms'.format((res.time_ns_dst - res.time_ns_src) * 1e-6, (end - res.time_ns_src) * 1e-6))

    def stream_chat(self, count=5):
        def genny():
            for i in range(count):
                print('__FIRE__', flush=True)
                yield common_pb2.SomeMessage(msg='?Hello, this is client {}?'.format(i))
                beat()
                beat()
                beat()
                beat()
                beat()
                beat()
                beat()
                beat()
                print('?', flush=True)

        for res in self.stub.StrBidiStream(genny()):
            print(res, flush=True)
            # beat()
            # beat()
            # beat()
            # beat()
            print('!', flush=True)


    def some_msg(self):
        print(self.stub.SomeReply(common_pb2.Empty()))

    def help(self):
        print(self.stub.__dict__)

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
        "--halp", action="store_true",
        help="dump diagnostics")
    parser.add_argument(
        "-M", "--msg", action="store_true",
        help="some message idk")
    parser.add_argument(
        "-S", "--stream_bidi", action="store_true",
        help="Run a bidirectional stream")
    parser.add_argument(
        "-b", "--burst", action="store_true",
        help="Run a burst stream")
    parser.add_argument(
        "-e", "--error", action="store_true",
        help="Run an error causing function")
    parser.add_argument(
        'cmd', nargs='?', default='ls', type=str,
        help="Command to run"
    )

    return parser


if __name__ == '__main__':
    args = arg_parser().parse_args()
    # print('{}'.format(args))
    c = Client(args.host, args.port)

    if args.halp:
        c.help()
        exit()

    if args.error:
        c.cause_error()
        exit()

    if args.msg:
        c.some_msg()
        exit()

    if args.health:
        c.test_latency()
        exit()

    if args.burst:
        c.time_burst()
        exit()

    if args.stream_bidi:
        c.stream_chat()
        exit()

    out = c.run_client(args.cmd)
    print(out)



