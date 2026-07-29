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
| Voice Transcriber | Convert audio to text for embedded and standalone use | Structure created | `voice-transcriber.md` |
