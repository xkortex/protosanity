# Compile protobuf files in this directory for test example.

.PHONY: all python test fail cd_build cd_test clean

all: python

python:
	python foolib/compile_pb.py foolib/protobuf

# this works because we are in the correct directory
test: python
	python -c "import foolib.protobuf.myservice_pb2"
	python -c "import foolib.protobuf.myservice_pb2_grpc"
	python -c "from foolib.protobuf import myservice_pb2, myservice_pb2_grpc, common_pb2; a=common_pb2.MyImportedError; c=myservice_pb2_grpc.ProcessorServicer()"

# this compiles, but the python import fails!
cd_build:
	cd foolib/protobuf && \
	python -m grpc_tools.protoc --proto_path=. --proto_path=../../ --python_out=. --grpc_python_out=. common.proto && \
	python -m grpc_tools.protoc --proto_path=. --proto_path=../../ --python_out=. --grpc_python_out=. myservice.proto;

# this fails!
cd_test:
	python -c "import foolib.protobuf.myservice_pb2"
	python -c "import foolib.protobuf.myservice_pb2_grpc"
	python -c "from foolib.protobuf import myservice_pb2, myservice_pb2_grpc, common_pb2; a=common_pb2.MyImportedError; c=myservice_pb2_grpc.ProcessorServicer()"

# this fails!
fail:
	# works fine because no import
	python -m grpc_tools.protoc --proto_path=foolib/protobuf --python_out=. --grpc_python_out=. ./foolib/protobuf/common.proto
	#
	python -m grpc_tools.protoc --proto_path=foolib/protobuf --python_out=. --grpc_python_out=. ./foolib/protobuf/myservice.proto

clean:
	rm -f foolib/protobuf/*_pb2.py
	rm -f foolib/protobuf/*_pb2_grpc.py
