FROM apache/airflow:1.10.10

USER root

RUN apt-get update \
    && apt-get install -y patch software-properties-common \
    # Install docker client (for docker login):
    && curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - \
    && apt-key fingerprint 0EBFCD88 \
    && add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

COPY bin/* /usr/local/bin/
COPY patch/* /tmp/patches/



USER airflow

RUN pip install --user 'airflow-declarative==1.1' docker

RUN set -ex \
    && cd $(dirname `python -c 'import airflow; print(airflow.__file__)'`) \
    && cd .. \
    && for p in /tmp/patches/*.patch; do patch -p1 < $p; done


# USER is intentionally kept as `root`, otherwise it won't be possible
# to use the docker.sock
USER root

ENTRYPOINT ["entrypoint-root.sh"]
