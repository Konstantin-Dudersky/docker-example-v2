ARG POETRY_VER
ARG PYTHON_VER

FROM python:${PYTHON_VER}-bullseye

ENV PATH="/root/.local/bin:$PATH"
ARG POETRY_VER

WORKDIR /root/code/

RUN apt-get -y update \
    # system tools
    && apt-get install -y htop nano ranger \
    # network tools
    iproute2 iputils-ping \
    # psycopg2 depends
    libpq-dev \
    # poetry depends
    python3-venv curl python3-dev build-essential

RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VER
RUN poetry config virtualenvs.in-project false

CMD ["tail", "-f", "/dev/null"]

# debugpy
EXPOSE 5678
