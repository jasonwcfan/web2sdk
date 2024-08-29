<h2 align="center">
🦊 web2sdk
</h2>

<p align="center">
  <p align="center">Automatically turn third party APIs into Python SDKs</p>
</p>
<p align="center">
<a href="https://github.com/jasonwcfan/web2sdk/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/static/v1?label=license&message=MIT&color=blue" alt="License">
</a>
<a href="https://github.com/jasonwcfan/web2sdk/issues?q=is%3Aissue+is%3Aclosed" target="_blank">
    <img src="https://img.shields.io/github/issues-closed/jasonwcfan/web2sdk?color=blue" alt="Issues">
</a>
</p>

Web2sdk is a set of tools for reverse engineering APIs. web2sdk records network requests tied to a particular URL, turns those requests into an OpenAPI schema, and converts the OpenAPI schema into a Python SDK using Python's abstract syntax trees (AST) module.


https://github.com/user-attachments/assets/5a7f477d-76ab-46f2-9884-62dfc9f2715b


### Features
- Generates an OpenAPI/Swagger yaml schema from any web-based flow
- Automatically merges requests to the same endpoint
- Generates pydantic classes based on OpenAPI request and response schemas
- Supports `basic` and `bearer` auth schemes

### Usage
1. Use [mitmweb](https://mitmproxy.org/) to record and export network traffic, or export a HAR file from Chrome devtools.
![CleanShot 2024-08-27 at 21 11 53](https://github.com/user-attachments/assets/3453f33b-686b-476e-80e3-bd7df8c63f50)

2. Install web2sdk
    ```sh
    $ pip install web2sdk
    ```
3. Generate an OpenAPI spec and SDK. Only requests to urls that included the `base-url` will be included.
    ```sh
    $ web2sdk --requests-path <path/to/har/or/flow/file> --base-url <https://finic.ai/api/v1> --sdk-name FinicAPI --output <path/to/output>
    ```
    Generated files will be saved in the current directory if the `--output` flag is not provided.

### 🚧 Futre Improvements
- Support for oauth and custom auth schemes that use header and url params
- Automatic auth token refresh
- Support for templated API paths (e.g. `https://api.claude.ai/api/organizations/{organization_id}/chat_conversations`)
- LLM integration to generate class names and example request payloads
- Include a linter/formatter to make generated SDK more readable

### Acknowledgements
Web2sdk's web2swagger module extends [mitmproxy2swagger](https://github.com/alufers/mitmproxy2swagger), but with some improvements to the OpenAPI schema generation.
