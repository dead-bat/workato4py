# workato4py
A Python library for Workato

workato4py is a small, simple library to facilitate faster TTL for pipelines that center around or otherwise incorporate Workato's Automation Platform-as-a-Service (APaaS). Ultimately, these pipelines can be used to construct a backend for an automation solutions marketplace that allows common automation solutions to be deployed ad-hoc for clients with little-to-no intervention by a person. Of course, this requires as much careful attention to how the automation solutions, themselves (known in Workato as "recipes"), are designed. There is a separate document that discusses "genericizing" automations efficiently for reusability.

## Summary

The workato4py library is fairly simple. It consists of two modules: one for the OEM Embedded API and one for the Developer API.

Each module has a class -- `Workato` -- that represents a connection to Workato's API. It's core functionality is to execute a request (options are GET, POST, PATCH, and DELETE) using the class's `.api_request()` function to interact with the API.

Why is this helpful? The `api_request()` function includes error checking (for both API functionality and response data) and exception handling, and other repetetive logic that usually goes into a natively-coded requests every time they have to be made. For a single API query, this isn't a big deal, but when you're building an automation pipeline that's heavily-dependent on an API as the only way to interface with your host, this can get a bit overwhelming. The `Workato.api_request()` function allows this to all be obfuscated by a single line of code, and eliminates the need for the pipeline developer to spend extensive amounts of time on repetitive logic. **{Examples to be added here.}**

### What workato4py can (and can't) do

There are a handful of methods available to the `Workato` class that can reduce more specific actions into a single line of code, similarly:

- `add_workspace_collaborator()` facilitates sending an invitation to a new collaborator for a given workspace.
- `create_workspace()` facilitates the creation of a new managed user workspace for a Workato OEM organization.
- `export_package()` will perform the export operation for a specific manifest in the Recipe Life Cycle Management (RLCM) utility.
- `download_package()` downloads the zip file of a specified package from the RLCM utility.
- `import_package()` imports a zip file package into a designated workspace.
- `get_log()` retrieves recipe and job logs.
- `access_audit()` executes a SOC2-compliant access audit that returns two sets of data for reporting
  - a table of user roles and their respective permissions 
  - table of all managed user workspaces within an organization with their collaborators and assigned roles.

Most importantly, while every effort is made to ensure this code is functional and usable, please remember that this project is in its early stages and should not be considered "production ready". You are more than welcome to implement it in production use cases (in accord with the terms of the [license](LICENSE)), but please keep in mind that it is still in beta and shouldn't be considered "stable".

### A note about the `requests` library

For simplicity and efficiency in initial development, I've built this library with the `requests` library. Eventually, I'll revise the codebase to use `urllib3` instead, so as not to have depndencies outside Python's standard library, but for the time being, `requests` ensures we can focus on building out functionality and structuring the data model without spending a lot of time up-front on networking.

### Multiple APIs

The Workato platform has two distinct APIs: the **Workato Embedded API** and the **Workato Developer API**. There is also Workato's own **API Platform** for front-end operations, which will eventually have a module in this library, too, but we're not there, yet. For the time being, interest is focused on facilitating interaction with the two back-end APIs for Workato for the purpose of building pipelines and scripting maintenance and administrative tasks.

- The **Workato Embedded** API is available for those Workato customers subscribed as "OEM Enterprise" customers. The API is documented [here](https://docs.workato.com/oem/oem-api.html).
- The **Workato Developer** API is a general-purpose API for all Workato clients at the workspace-level and exposes most common administrative and maintenance tasks. The API is documented [here](https://docs.workato.com/workato-api.html).

## Extras

In addition to the library modules for interacting with Workato's APIs, the `workato4py` package also include several samples and tools that may be useful for administrators and engineers.