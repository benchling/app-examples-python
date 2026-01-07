# Benchling Python Examples

A collection of Python reference examples for the Benchling platform.

# Benchling Apps

## chem-sync-local-flask

Demonstrates creating a custom UI in Benchling allowing users to search for 
molecules from [PubChem](https://pubchem.ncbi.nlm.nih.gov/) and sync them into Benchling.

Uses [Cloudflare-tunnel](https://www.cloudflare.com/products/tunnel/) and [Docker](https://www.docker.com/) to receive webhooks 
in a local development environment running [Flask](https://flask.palletsprojects.com/) with the 
[Benchling SDK](https://docs.benchling.com/docs/getting-started-with-the-sdk).

![image info](./examples/benchling-apps/chem-sync-local-flask/docs/demo-short.gif)

**Code Includes:**
* Benchling App Authentication via [Client Credentials](https://docs.benchling.com/docs/getting-started-benchling-apps#getting-credentials)
* Custom UI via [App Canvas](https://docs.benchling.com/docs/introduction-to-app-canvas)
* User Feedback via [App Status](https://docs.benchling.com/docs/introduction-to-app-status)
* Data Mapping via [App Config](https://docs.benchling.com/docs/app-configuration)
* Receiving and verifying [Webhooks](https://docs.benchling.com/docs/getting-started-with-webhooks)
* Creating [molecule custom entities](https://benchling.com/api/reference#/Molecules/createMolecule)

# Custom Code in Automation Designer

This project contains example snippets of code that can be utilized in a Custom Code step of the Benchling Automation Designer within Benchling Analysis. 

#### [Example Snippets](./examples/custom-code-AD/README.md)

![image info](./examples/custom-code-AD/snippets/plot-chromatogram/docs/Example_Chromatogram_Plot.gif)

### Overview 
These examples demonstrate how to extend Benchling's native capabilities using Python scripts within the Automation Designer context. They cover common use cases such as data visualization, file handling, and complex data transformations.

### Key Capabilities
The code examples included in this directory cover the following functionalities:

- Visualizations: Create custom charts, graphs, and annotations (e.g., chromatograms).

- File Parsing: Logic to read and parse various file formats.

- File Creation: Generate new files, such as instruction lists for laboratory instruments.

- Data Transformation: Apply transformations, merge/join datasets, and perform complex calculations on data.

### Dependencies
See [requirements.txt](./examples/custom-code-AD/requirements.txt) for the specific library versions used in these examples.

### Constraints & Limitations
When adapting these examples for your tenant, please note the current beta limitations:

 - Runtime Limit: Execution is limited to 15 minutes per run.

 - No Network Access: The environment does not support general network access.

 - Fixed Packages: You cannot install custom libraries (e.g., via `pip`). You are limited to the pre-installed packages listed above

 - No API Access: The Benchling SDK/API is not currently supported within the execution environment.

 - Bring your own Container: BYOC is not supported; code runs in the standard Benchling runtime environment

 - Lifecycle Management: The feature does not currently support native GitHub integration or versioning within the UI.