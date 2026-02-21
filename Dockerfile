# base Docker image that we will build on
FROM python:3.13.11-slim
# set environment variables to prevent Python from writing pyc files and to ensure that output is flushed immediately
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# set up the working directory inside the container
WORKDIR /code
# add virtual environment to path so we can use the installed packages
ENV PATH="/code/.venv/bin:$PATH"

# copy the dependency files to the container and install the dependencies
COPY pyproject.toml .python-version uv.lock ./
# install the dependencies using uv, which will create a virtual environment and install the packages there
RUN uv sync --locked

# copy the script to the container. 1st name is source file, 2nd is destination
COPY ingest_data.py .

# set the entry point to run the script when the container starts. This will execute the command `python ingest_data.py` when the container is run.
ENTRYPOINT ["python", "ingest_data.py"]