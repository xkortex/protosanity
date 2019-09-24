# protosanity
## Protobufs / gRPC with less hair-pulling

gRPC is, in my humble opinion, fantastic. Given a set of `_pb2.py` stubs, decoupling chunks of software is a breeze. Load balancing is easy; with Swarm, it's practically free. Kittens and rainbows. 

Getting your stubs from `protoc` is the nightmare to gRPC's dream. Python in particular is a second class citizen it seems. It's fairly easy if you simply dump everything into the global package namespace (`from foo_pb2 import MyMsg`), but this is pretty gross. However, try to generate proto files that end up in python packages and [everything geos sideways](https://github.com/protocolbuffers/protobuf/issues/1491). Throw in `.proto` import statements and you get absolute mayhem, human sacrifice, dogs and cats living together... mass hysteria.

The goal of this humble project is to simplify the process of generating, packaging and maintaining `proto` and `grpc` files for multiple languages, in a way that ideally exists at the intersection of packaging best practices for each of those languages. Namely, python, go, and C++. 
