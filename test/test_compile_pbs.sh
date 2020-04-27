#!/usr/bin/env bash

HEREDIR=$(cd "$(dirname $(realpath ${0}))" && pwd)
# should be protosanity/test
# pip install protosanity before running this script

ERRCOUNT=0
function mytest {
    "$@"
    local status=$?
    if [[ $status -ne 0 ]]; then
        echo "error with $@" >&2
    fi
    ERRCOUNT=$(($ERRCOUNT+$status))
    return $status
}

echo "Running from: ${HEREDIR}"
#cd "${HEREDIR}/test"
#echo "cding to: $(pwd)"
python -m protosanity.compile_pbs "${HEREDIR}/foolib/protobuf" "${HEREDIR}"

echo "testing imports..."
mytest python -c "import foolib.protobuf.common_pb2"
mytest python -c "import foolib.protobuf.myservice_pb2"
mytest python -c "import foolib.protobuf.myservice_pb2_grpc"
mytest python -c "from foolib.protobuf import myservice_pb2, myservice_pb2_grpc, common_pb2; a=common_pb2.MyImportedError; c=myservice_pb2_grpc.ProcessorServicer()"
echo "Errors: $ERRCOUNT"
if [[ $ERRCOUNT -ne 0 ]]; then
  exit 1
fi