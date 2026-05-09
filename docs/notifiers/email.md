# Notifier: Email

> **Status:** spec klaar; implementatie in milestone C.

Email als handoff-kanaal voor integer-modus. SMTP-out + lokaal
Flask-mini-portaal voor magic-link-respons. Geen IMAP, geen reply-parsing
— die zijn fragiel en geven ondoorzichtige audit-trails.

## Hoe het werkt

1. IntegerMode escaleert een hoog-risico Decision.
2. EmailNotifier verstuurt een SMTP-mail naar de auditor met vier
   magic-link-knoppen: `Goedkeuren`, `Afwijzen`, `Aanpassen`, `Afbreken`.
3. Auditor klikt op een knop in zijn mail-client; browser opent
   `http://localhost:8765/decision/<id>/<action>`.
4. Het lokale Flask-portaal valideert het token (single-use, TTL 24u),
   roept `DecisionResolver.resolve()` aan, en toont een
   bevestigingspagina.
5. Pipeline-thread hervat met het besluit.

## Configuratie

| Env-var | Verplicht | Beschrijving |
|---|---|---|
| `ISO_AUDIT_SMTP_HOST` | ja | SMTP-host voor outbound mail |
| `ISO_AUDIT_SMTP_PORT` | ja | SMTP-poort (587 voor STARTTLS, 465 voor SMTPS) |
| `ISO_AUDIT_SMTP_USER` | ja | SMTP-account |
| `ISO_AUDIT_SMTP_PASS` | ja | SMTP-wachtwoord (gebruik secrets-manager) |
| `ISO_AUDIT_SMTP_FROM` | ja | Afzender-adres |
| `ISO_AUDIT_AUDITOR_EMAIL` | ja | Ontvanger (de auditor die handoffs krijgt) |
| `ISO_AUDIT_PORTAL_PORT` | nee | Default `8765` |
| `ISO_AUDIT_PORTAL_TOKEN_TTL_HOURS` | nee | Default `24` |

## Acceptable-risk: HTTP zonder TLS

Het Flask-portaal draait standaard HTTP zonder TLS. Reden: het draait
lokaal op de pipeline-host, magic-link-tokens zijn single-use én
tijd-gelimiteerd. Bij multi-host-deployment SHALL TLS via reverse-proxy
verplicht worden — dat is dan eigen change-proposal.

Documenteer dit risico in elke deployment-omgeving expliciet. Een
audit-tool dat zelf op losse HTTP draait zonder dat ergens te benoemen
ondermijnt geloofwaardigheid bij externe certificeerder.

## Audit-trail

Outbound mail-headers (Message-ID, To, Subject, timestamp) én
HTTP-request-log van het portaal worden gelogd. Single-use-tokens worden
na consumptie gemarkeerd in een `email_tokens`-tabel; expired-tokens
laten een log-entry zien.

`decisions.notifier_naam = "email"` voor cross-channel-analyse.

## Aanroep

```bash
iso-audit pipeline --source drive --mode integer --notifier email
```
