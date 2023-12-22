# Benchling App Example: Chemical Sync for Local Development

An example Benchling App written in Python which allows users to search for chemicals 
via [PubChem](https://pubchem.ncbi.nlm.nih.gov/) and create them in Benchling.

![image info](./docs/demo-full.gif)
_The App features branching flows and will also validate user inputs._

## Technical Prerequisites

This app is optimized as a minimal local development experience using [Docker](https://www.docker.com/) for reproducibility.

It relies on a few other tools that will be installed for you within Docker containers:
* [Localtunnel](https://localtunnel.me/) - expose a public webhook URL and forward the results locally. ⚠️ *Not for production or real data!*
* [Flask](https://flask.palletsprojects.com/) - A simple Python web application framework

## Getting Started

```bash
docker compose build
docker compose up
```

You can verify that Flask is up and running:

```bash
curl localhost:8000/health
```

If Flask is running, you should see `OK` printed.

Be sure to note the URL created for you by `localtunnel`. The log line should look something like this:

```
app-workshop-local-tunnel-1   | your url is: https://brave-wombats-poke.loca.lt
```

On *nix systems, you can easily obtain _just_ the URL via:

```
docker compose logs -n 1 local-tunnel | grep -o https://.*
```

Example Output:

```
https://brave-wombats-poke.loca.lt
```

## Setting Up Your App in Benchling

### Benchling Prerequisites
1. Access to a Benchling tenant, like `https://my-tenant.benchling.com`
2. Ensure you've been granted access to the [Benchling Developer Platform Capability](https://help.benchling.com/hc/en-us/articles/9714802977805-Access-the-Benchling-Developer-Platform).
3. This example also requires a [Lab Automation](https://www.benchling.com/resources/benchling-lab-automation) license.
4. [Molecule entities](https://help.benchling.com/hc/en-us/articles/9684254682893-Molecule-entity-overview) will need to be enabled on your tenant.

### Upload the App Manifest

Click the user icon in the bottom left corner to bring up the main menu. Select "Feature Settings" > "Developer Console"

Next, click the "Create app" button and choose "From manifest."

When prompted to upload a file, select `manifest.yaml` and click "Create."

![image info](./docs/create-app.gif)

### Update the Webhook URL

Every time we restart the `local-tunnel` Docker container, it will provision
a new public webhook URL.

Update the Benchling App's Webhook URL in the UI with the new server and
append the path our Flask route expects (see `local_app/app.py`).

For example, if our `localtunnel` generated URL is `https://hot-ideas-doubt.loca.lt`,
the webhook URL in Benchling should be:

```
https://hot-ideas-doubt.loca.lt/1/webhooks
```

![image info](./docs/update-webhook-url.gif)

### Generating a Client Secret

Generate a client secret in Benchling and be sure to copy the secret.

![image info](./docs/generate-secret.gif)

One easy way to set these environment variables for Docker is to add a `.env` file.

```bash
touch .env
```

Open it in an editor of your choice and set the values with the plaintext client ID 
and secret for your App. For example:

```
CLIENT_ID=42a0cd39-0543-4dd2-af02-a866c97f0c4d
CLIENT_SECRET=cs_****************oOkNhFPnfI7Uq9s
```

You'll then need to restart _just_ the `benchling-app` Docker service to pick up the changes:

```
docker-compose up -d
```

If you restart both containers, be sure to update your App in Benchling with the new webhook URL from localtunnel.

> ⚠️ In production, store the secret with a secure solution. Avoid placing it in plaintext anywhere in code or configuration.

### Create App Registry Dependencies

If you examine the `configuration` section of `manifest.yaml`, you'll see our App
expects a few configuration items:
1. A folder
2. A molecule entity schema with two decimal fields

The `features` section of `manifest.yaml` also states that our App will render
its UI on an `ASSAY_RUN`. So we'll also need:
1. An Lab Automation run schema

#### Folder

Create a new folder where the molecules created by the App will be placed.
An existing folder can also be used, if the App has permissions to it.

![image info](./docs/create-folder.gif)

#### Molecule Entity Schema

Create the entity schema in the tenant's registry. If you do not have access to
the registry, you can ask your tenant administrator to do this for you.

![image info](./docs/create-molecule-schema.gif)

The created molecule schema should look something like this:

![image info](./docs/schema-example.png)

_Note: The names can be different, and the schema is allowed to have additional fields.
As long as it's for a `Molecule` entity, and has at least two `Decimal` fields._

#### Lab Automation Run Schema

Create a new lab automation run schema in the registry.

![image info](./docs/create-run-schema.gif)

### Updating the App's Configuration

App Configuration gives us a stable code contract for referencing data mapped in a Benchling tenant.
The values of the data in Benchling can then be changed without updating App code.

Let's update our configuration to:
1. Specify a folder for syncing sequences
2. Link a molecule schema and fields for the synced chemicals
3. Select an assay run schema to associate with our Benchling App

![image info](./docs/update-app-config.gif)

### Permission the App

By default, Benchling Apps do not have permission to any data in Benchling.
Let's grant some access by adding the Benchling App to an organization.

![image info](./docs/permission-app.gif)

## Running the App - Syncing a Chemical

1. Create a new notebook entry
2. Insert a run of the schema linked in App Config
3. Create the Run
4. Enter a valid chemical name to search for, such as `acetaminophen`
5. Click "Search Chemicals"
6. After reviewing the preview, click "Create Molecule"
7. Click the linked entity to view it in Benchling

![image info](./docs/demo.gif)