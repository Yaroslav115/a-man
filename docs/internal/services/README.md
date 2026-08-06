# Service Documentation

Create one Markdown file per service, using a lowercase kebab-case filename:

```text
services/<service-name>.md
```

Copy `SERVICE_TEMPLATE.md` and replace every placeholder. Service documents must
describe the deployed current state, not only the intended design. Update the
`Last verified` field whenever the documented values are checked.

The service index will be maintained here:

| Service | Purpose | Status | Document |
|---|---|---|---|
| Voice Transcriber | Convert audio to text for an embedded Chat Widget and standalone demo | File backend implemented; WebSocket streaming planned | `voice-transcriber.md` |
