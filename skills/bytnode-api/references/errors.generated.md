# BytNode error codes

> Generated from https://api.bytnode.com/openapi.json (contract **3.0.1**) by `tools/generate_references.py`. Do not edit by hand: regenerate.

Every error is `{status: "error", server_time, error: {code, message, param?, details?}}` (the WebSocket sends the same object under `op: "error"`). Branch on `error.code`; show `error.message`; read `error.details` (`suggestion`, `accepted`, `retry_after_s`, `window_s`, `earliest_ms`, `max_limit`…) for what to change. A code not listed here is a newer one: treat it as a generic error.

## Codes

- `depth_too_large`: A depth (snapshot field, WebSocket order book channel) exceeds its documented maximum.
- `edge_rate_limited`: Too many requests from this IP address at the edge (anti-flood: 20 per second per address, bursts of 40). Retry after 1 second.
- `history_depth`: The requested history goes further back than your plan allows.
- `https_required`: Plain HTTP is refused: call the same URL over https://. A key sent over http:// travelled unencrypted: rotate it.
- `insufficient_data`: Not enough history to compute the requested indicator.
- `internal_error`: Unexpected server error. A retry with backoff may succeed; if it persists, report it with the response's X-Request-Id header.
- `invalid_api_key`: The API key is invalid or revoked (or, on the WebSocket, the token is invalid, expired or already used).
- `invalid_asset`: The asset is not served by this family. The error lists the accepted values.
- `invalid_channel`: WebSocket: the channel name is malformed or unknown; the error lists the accepted forms.
- `invalid_depth`: A depth (snapshot field, WebSocket order book channel) is not a positive integer.
- `invalid_indicator`: The POST /v1/indicators body is invalid (id, type or parameters).
- `invalid_message`: WebSocket: the message is not a readable JSON object.
- `invalid_parameter`: A parameter has an invalid type or value.
- `invalid_series`: The macro series does not exist. See the family's /series catalogue.
- `invalid_symbol`: The symbol is not served. The error lists the accepted values (see /v1/symbols).
- `invalid_time_range`: since_ms / until_ms are not valid epoch milliseconds, or since_ms > until_ms (until_ms is inclusive).
- `invalid_timeframe`: The timeframe is not accepted by this route.
- `method_not_allowed`: The route exists but not with this HTTP method.
- `missing_api_key`: No API key was sent: put it in the X-API-KEY header (or api_key in the WebSocket URL).
- `missing_parameter`: A required parameter is missing.
- `not_applicable`: WebSocket: the channel has no meaning for this asset (a futures channel of a stablecoin). The REST API answers such a request with 200 and `unavailable: not_applicable`.
- `not_authenticated`: WebSocket: a message other than auth arrived on a session not yet authenticated (residual: the key is checked at the handshake, where a missing key answers 401 missing_api_key and an unknown or revoked one 401 invalid_api_key).
- `not_found`: Unknown route.
- `plan_family`: Your plan does not include this data family: the message names it, and GET /v1/limits lists the families of your key.
- `plan_websocket`: Your plan does not include the WebSocket stream.
- `quota_exceeded`: Your plan's monthly quota is exhausted. Retry-After (and retry_after) give the seconds until it resets, on the first day of the month (UTC).
- `rate_limited`: Your plan's per-minute rate is exceeded. Retry after Retry-After seconds.
- `repeated_parameter`: A parameter appears more than once.
- `service_unavailable`: Temporary unavailability. Retry after Retry-After seconds.
- `timeframe_not_served`: The series exists but does not serve this timeframe (a daily-only series asked in 1h). A timeframe the route never serves is invalid_timeframe.
- `unknown_field`: A ?fields= or snapshot field name does not exist.
- `unknown_parameter`: The route does not declare this parameter.
- `upstream_timeout`: The request took too long. Reduce the window or depth, then retry.

## By HTTP status

- **Unauthorized**: No API key was sent (`missing_api_key`), or it is invalid or revoked (`invalid_api_key`). Send it in the `X-API-KEY` header.
- **Forbidden**: The key is valid but your plan does not cover the request (`plan_family`, `plan_websocket`, `history_depth`).
- **NotFound**: Unknown route (`not_found`). The message suggests the closest route when there is one (`Did you mean`).
- **MethodNotAllowed**: The route exists, but not with this HTTP method (`method_not_allowed`). `Allow` lists the accepted ones.
- **Unprocessable**: A parameter is missing, unknown, repeated or has an invalid value (`missing_parameter`, `unknown_parameter`, `repeated_parameter`, `invalid_parameter`, `invalid_symbol`, `invalid_asset`, `invalid_series`, `invalid_timeframe`, `invalid_time_range`, `invalid_depth`, `depth_too_large`, `invalid_indicator`, `unknown_field`...).
- **TooManyRequests**: Your plan's per-minute rate (`rate_limited`) or monthly quota (`quota_exceeded`) is exhausted, or too many simultaneous requests from one IP (`edge_rate_limited`).
- **ServiceUnavailable**: Temporary unavailability (`service_unavailable`). Retry after `Retry-After` seconds.
- **InternalError**: Unexpected server error (`internal_error`), never caused by the request. Retry with backoff; if it persists, report it with the `X-Request-Id` header.
- **GatewayTimeout**: The query took too long for the window or depth asked (`upstream_timeout`): reduce `limit` or the time range, then retry.
