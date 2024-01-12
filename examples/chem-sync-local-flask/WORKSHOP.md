# App Workshop - Building Live

## Prerequisites

Please come with the following pre-installed and configured on your machine:

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/)
    1. Example test: `docker run --rm -it python:3.11 bash`
1. [Git](https://github.com/git-guides/install-git)
    1. Example test: `git clone git@github.com:benchling/app-examples-python.git`
1. A Python IDE
    1. For the workshop, **we recommend [VSCode](https://code.visualstudio.com/Download) with the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) plugin installed if you don’t have an IDE preference**
    1. [PyCharm](https://www.jetbrains.com/pycharm/download/) users may have success with its [partial support for Dev Containers](https://www.jetbrains.com/help/pycharm/connect-to-devcontainer.html#create_dev_container_inside_ide)
    1. If you’d like to bring your own IDE, we ask that you come prepared to:
        1. Setup your own Python virtual environment for **Python 3.11** 
        1. Install requirements on your own (e.g., `pip install -r requirements.txt`)
1. Ensure that you have no other processes already running on **port 8000**.

Additionally, please:
1. You should received an email inviting you to https://dev-training.benchling.com/. Be sure to verify your account by clicking the link in the response email!

### Notes on Docker for Windows

> ℹ️ Some Windows machines may require extra configuration when running Docker. If you’re not able to run `docker-compose up –build` successfully on the example Git repository, you may need to configure Docker to “Use ContainerD for pulling and storing images" in `Docker > Settings > Features in development > Beta Features`.

If you encounter an error running any Docker commands that looks like `ERROR: request returned Bad Gateway for API route and version`, following these instructions may help: https://github.com/docker/for-mac/issues/6956#issuecomment-1876444658

## Setup Environments

1. Clone the repository: `git clone git@github.com:benchling/app-examples-python.git`
1. Checkout the workshop branch: `git checkout jan-2024-workshop`
1. Navigate to the example directory for **chem-sync-local-flask**:
    1. `cd app-examples-python/examples/chem-sync-local-flask/`
1. Create a `.client_secret` placeholder file required by Docker
    1. *nix: `touch .client_secret`
    1. Windows: `echo.> .client_secret`
1. Start building the Docker containers
`docker compose up --build -d`

## Setup IDE

In **VSCode**:
1. `File > Open Folder > app-examples-python/examples/chem-sync-local-flask/`
    1. It's important to open the `chem-sync-local-flask` folder, _not_ the root `app-examples-python` folder
1. Click **Reopen in Container** when prompted (you can also do this from the lower left corner menu)
1. You may need to click **Reload Window** to finish loading extensions. This is normal.

In PyCharm:
1. `File > Open > app-examples-python/examples/chem-sync-local-flask/`
1. Open the file `.devcontainer/devcontainer.json`
1. In the left tray, click the container icon and select **Create Dev Container and Mount Sources**
1. Accept the defaults, click **Build Container and Continue**

Any other IDE:
1. In `app-examples-python/examples/chem-sync-local-flask/`
1. Create a **Python 3.11** virtual environment, activate it, and install requirements (e.g., `pip install -r requirements.txt`)

### Check Existing Docker Setup
1. Once Docker has finished building and composing up:
`curl localhost:8000/health`

## Discuss App Layout
1. Observe the `benchling-sdk` dependency in `requirements.txt`

## Setup the App in Benchling
1. Open `manifest.yaml` and rename the App's `name`` attribute under `info` by suffixing your name to the end
    1. Example: `Sample Sync App` -> `Sample Sync App FirstName LastName`
1. Follow the instructions from the README to setup the App in Benchling:
    1. https://github.com/benchling/app-examples-python/tree/main/examples/chem-sync-local-flask#upload-the-app-manifest
    1. The workshop tenant URL is: https://dev-training.benchling.com/
    1. Stop at the section "Create App Registry Dependencies" and skip to: https://github.com/benchling/app-examples-python/tree/main/examples/chem-sync-local-flask#updating-the-apps-configuration
    1. Skip the "Permission the App" section. Our admins will do that for you.

## Receiving our First Webhook
Test the flow! In Benchling:
1. Create a new notebook entry
1. Insert a run of the schema linked in App Config
1. Create the Run
1. Observe our debug logging printing the webhook received:
    1. `docker compose logs benchling-app`

## Rebuild the App!
1. Start in `local_app/app.py`