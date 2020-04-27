ARG BASE_IMAGE="ubuntu"
ARG BASE_TAG="18.04"
FROM ${BASE_IMAGE}:${BASE_TAG} as base_python

RUN apt-get update -qq && apt-get install -qq curl \
    && apt-get install -qq --no-install-recommends \
        git \
        python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN ln -svf $(which python3) /usr/local/bin/python

RUN curl --silent --show-error \
    https://bootstrap.pypa.io/get-pip.py | python3

## ==================== ====================

FROM base_python

WORKDIR /src

COPY build-require.txt ./

RUN pip install --no-cache-dir -r /src/build-require.txt

COPY . /src/protosanity

RUN pip install --no-cache-dir "/src/protosanity/"


