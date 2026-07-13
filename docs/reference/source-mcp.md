---
status: draft
last_reviewed: 2026-07-13
---

# Source: MCP

> **Status:** placeholder. Implementatie via eigen change-proposal
> `iso-audit-mcp-source` na milestone C.

Generieke Model Context Protocol-adapter zodat iso-audit elk
MCP-server-aangeboden bron kan consumeren (Asana, Linear, Notion,
Confluence, GitHub, …) zonder per-bron een eigen Source-implementatie.

## Naamgeving

Adapters geregistreerd onder `mcp:<server-naam>`, e.g. `mcp:asana`,
`mcp:notion`. De dubbele-punt-conventie is parallel aan hoe MCP-tool-IDs
zelf werken.

## TODO

- Adapter generaliseert MCP-tool-calls naar `Source.list_documents` /
  `list_findings`
- Configuratie via `MCP_<SERVER>_*` env-vars
- Open vraag: hoe mapt MCP-tool-call-respons op `Document` versus `Finding`?
  Sommige MCP-servers leveren beide door elkaar.

Wachten op concrete vraag-vanuit-praktijk voordat dit gebouwd wordt.
