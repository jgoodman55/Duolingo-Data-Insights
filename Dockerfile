FROM kestra/kestra:v1.1

USER root

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
     jq \
     curl \
  && rm -rf /var/lib/apt/lists/*

USER kestra