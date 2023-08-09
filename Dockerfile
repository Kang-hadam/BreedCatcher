FROM public.ecr.aws/lambda/python:3.10-arm64 AS builder

RUN yum install openssh-clients -y && \
    pip3 install poetry && \
    poetry config virtualenvs.create false && \
    mkdir ~/.ssh

ARG SSH_PRIVATE_KEY

RUN echo -e "${SSH_PRIVATE_KEY}" > ~/.ssh/id_ed25519  && \
    ssh-keyscan github.com >> ~/.ssh/known_hosts && \
    chmod 600 ~/.ssh/id_ed25519

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction --no-ansi --only main && \
    yum remove openssh-clients -y && \
    rm -rf ~/.ssh && \
    find . -type f ! -name 'app' -delete
COPY ./app/ ./
RUN pybabel compile -d ./locales -D base && find locales -type f -name '*.po' -delete

FROM public.ecr.aws/lambda/python:3.10-arm64

COPY --from=builder ${LAMBDA_TASK_ROOT} ${LAMBDA_TASK_ROOT}
COPY --from=builder /var/lang/lib/python3.10/site-packages /var/lang/lib/python3.10/site-packages

CMD ["main.handler"]
