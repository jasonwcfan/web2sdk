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

Web2sdk is a set of tools for reverse engineering APIs by intercepting network requests. It processes HAR files exported from Chrome devtools into an OpenAPI schema, then automatically generates a python SDK based on the schema. Each method in the python SDK corresponds to an endpoint, and includes strongly typed arguments, requests, and responses.

https://github.com/user-attachments/assets/5a7f477d-76ab-46f2-9884-62dfc9f2715b


### Features
- Generates an OpenAPI/Swagger yaml schema from any web-based flow
- Automatically merges requests to the same endpoint
- Generates pydantic classes based on OpenAPI request and response schemas
- Supports `basic` and `bearer` auth schemes
- Supports overriding default headers

### Example output
```python
import json
import http.client
from urllib.parse import urlparse
from pydantic import BaseModel
from typing import Optional, Dict, List, Any

class GetConversationsRequestParameters(BaseModel):
  offset: Optional[float] = None
  limit: Optional[float] = None
  order: Optional[str] = None

class GetConversationsResponse(BaseModel):
  items: Optional[List] = None
  total: Optional[float] = None
  limit: Optional[float] = None
  offset: Optional[float] = None
  has_missing_conversations: Optional[bool] = None

class ChatGPTAPI(BaseModel):
  hostname: str
  token: str

  def get_conversations(self, request_parameters:
    GetConversationsRequestParameters, *, override_headers: dict={}
    ) ->GetConversationsResponse:
    conn = http.client.HTTPSConnection(self.hostname)
    params = '&'.join([(k + '=' + v) for k, v in request_parameters.
      items()])
    headers = {'User-Agent': 'Web2sdk/1.0', 'Authorization': 'Bearer ' +
      self.token}
    headers.update(override_headers)
    conn.request('GET', '/backend-api/conversations?' + params + '',
      headers=headers)
    res = conn.getresponse()
    data = res.read().decode('utf-8')
    return json.loads(data)

  def post_conversation(self, request_body: PostConversationRequestBody,
        *, override_headers: dict={}) ->Any
### ...etc
```

## Usage
**1. Export HAR file**
* Open Chrome devtools and go to "Network".
* Go through a flow on a website that triggers the requests you want to capture and reverse engineer. The more varied the requests the better, as a single request might not capture all the possible request and response schemas for a particular endpoint.
* Click the button shown below to export the HAR file. Don't worry about filtering out requests, that happens later.
* Also compatible with [mitmweb](https://mitmproxy.org/) exports.

    ![CleanShot 2024-08-27 at 21 11 53](https://github.com/user-attachments/assets/3453f33b-686b-476e-80e3-bd7df8c63f50)

**2. Install web2sdk**
```
$ pip install web2sdk
```

**3. Generate an OpenAPI spec and SDK**
```sh
$ web2sdk --requests-path <path/to/har/or/flow/file> --base-url <https://finic.ai/api/v1> --sdk-name FinicSDK --auth-type bearer
```
* `base-url` filters out requests that don't start with the url provided. This should include everything up until the endpoints you want to reverse engineer.
* For example, `https://finic.ai/api/v1` will match only requests to the v1 endpiont, but `https://finic.ai/api` will match requests from v1, v2, and any other paths after `/api`.
* Generated files will be saved to `generated/<sdk_name>.yaml` and `generated/<sdk_name>.py` in the current directory by default.

**4. Run your python SDK.**
```python
from generated.FinicSDK import FinicSDK

finic = FinicSDK(hostname="finic.ai", token="your_token_here")
finic.get_connectors({})
finic.post_message({ message: "hi there" }, override_headers={ "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" })
```
* Each method in the generated SDK corresponds to an endpoint
* You can pass in any headers you want. By default, only `Authorization` and `User-Agent` headers are included.
* Some methods accept parameters and/or request bodies. Inspect the function to see what arguments it takes.

### Other Options
```-- auth <basic|bearer>```
* Optional, defaults to `none`. If set, the generated SDK class will expect a username and password for basic auth or a token for bearer auth.

```--output```
* Optional, defaults to `generated/` in the current directory. Specify a directory for the generated `.yaml` and `.py` files to be saved.

```--interactive```
* Run in interactive mode. Not well supported.

## 🚧 Planned Improvements
- Support for oauth and custom auth schemes. In the mean
- Automatic auth token refresh
- Support for templated API paths (e.g. `https://api.claude.ai/api/organizations/{organization_id}/chat_conversations`)
- Use LLMs to generate more readable class names, example request payloads, and other tasks that require fuzzy reasoning
- Include a linter/formatter to make generated SDK more readable

### Acknowledgements
Web2sdk's includes a modified version of [mitmproxy2swagger](https://github.com/alufers/mitmproxy2swagger).
