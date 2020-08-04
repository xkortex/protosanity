import time
try:
    ns = time.time_ns()
    time_ns = time.time_ns
except AttributeError:
    def time_ns():
        return int(time.time() * 1e9)
