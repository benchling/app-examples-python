FROM python:3.11

# Add non-root user for security
ARG USERNAME=nonroot
RUN groupadd --gid 1000 $USERNAME && useradd --uid 1000 --gid 1000 -m $USERNAME
## Make sure to reflect new user in PATH
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"
USER $USERNAME

# Install pre-requirements
RUN pip install pip~=23.3.2 setuptools~=69.0.3

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY dev_requirements.txt ./
RUN pip install -r dev_requirements.txt