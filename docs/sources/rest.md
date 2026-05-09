# Source: REST

> **Status:** placeholder. Implementatie via eigen change-proposal
> `iso-audit-rest-source` na milestone C.

Generieke REST-adapter voor bronnen die geen dedicated SDK hebben en niet
via MCP exposed zijn. OpenAPI-schema-driven mapping naar `Document` en
`Finding`.

## TODO

- Adapter consumeert OpenAPI-spec en config-bestand met endpoint-mapping
- Configuratie via `REST_<NAAM>_*` env-vars (base-url, token, paths)
- Pagination-handling, rate-limit-handling, retry-logica
- Open vraag: hoe ver kunnen we generiek gaan voordat de adapter
  onbruikbaar wordt? Eerst concrete bron identificeren.

Wachten op concrete vraag-vanuit-praktijk voordat dit gebouwd wordt.
