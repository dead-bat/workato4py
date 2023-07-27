# workato4py Developer Notes

Workato's documentation for their APIs can be found here:

- [Developer API](https://docs.workato.com/workato-api.html)
- [OEM Embedded API](https://docs.workato.com/oem/oem-api.html)

## General Info

Workato has four regional instances; accounts (for people and API clients) do not cross over between regional instances. Therefore, we need to account for which region the API client will be run for, and set the correct base URL, accordingly:

| Region | Code | Base URL |
| ------ | ---- | -------- |
| United States | `us` | `https://www.workato.com/api/` or `https://app.workato.com/api/` |
| Europe | `eu` | `https://app.eu.workato.com/api/` |
| Japan | `jp` | `https://app.jp.workato.com/api/` |
| Singapore | `sg` | `https://app.sg.workato.com/api/` |

When a new instance of the **Workato** class is initialized, the first parameter it requires is the region -- using one of the above codes -- which sets the base URL.

### Request Headers

Almost all requests require two primary headers: an authorization header and a content type header:

- The `Authorization` header contains a bearer token:
    `"Authorization": "Bearer <workato_api_token>"`
- The `Content-Type` header designates the content as JSON:
    `"Content-Type": "application/json"`

Both headers are configured at the time the **Workato** class object is initialized. The second parameter for the object is the token string (see [Workato's documentation](https://docs.workato.com/workato-api/api-clients.html) for details about setting up an API client and getting a token), and is used to populate the authorization header key. The content type value is statically assigned.

### HTTP Response Codes

The following response codes should be accounted for in all actions:

| Code | Description | Reply sample |
| ---- | ----------- | ------------ |
| 200  | Success | `{"Success": true}` |
| 400  | Bad Request | `{"message": "Bad request"}` |
| 401  | Unauthorized | `{"message": "Unauthorized"}` |
| 404  | Not found | `{"message": "Not found"}` |
| 500  | Server error | `{"message":"Server error","id":"3188c2d0-29a4-4080-908e-582e7ed82580"}` |


