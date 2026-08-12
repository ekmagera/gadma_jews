FROM mambaorg/micromamba:1.5.8-jammy
USER root
RUN apt-get update && apt-get install -y --no-install-recommends git bash ca-certificates build-essential && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /opt && chown mambauser:mambauser /opt
USER mambauser
COPY --chown=mambauser:mambauser envs/docker.yaml /tmp/docker.yaml
RUN micromamba create -y -n jews-demography -f /tmp/docker.yaml && micromamba clean --all --yes
RUN git clone --depth 1 https://github.com/isaacovercast/easySFS.git /opt/easySFS && \
    chmod +x /opt/easySFS/easySFS.py
COPY --chown=mambauser:mambauser docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
WORKDIR /work
ENV PATH="/opt/easySFS:$PATH"
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
