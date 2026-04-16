# Super Connector MCP Server

Wraps the Super Connector Railway API so Claude can query and write to Super Connector from any Cowork session without network restrictions.

## Deployment

- **MCP endpoint:** `https://web-production-5fec3.up.railway.app/mcp`
- **Transport:** Streamable HTTP (`streamable-http`)
- **Railway API (source of truth):** `https://super-connector-api-production.up.railway.app`
- **Auth:** `SC_API_KEY` environment variable (set in Railway service config)

## Tools (29 total)

### Contacts
- `sc_list_contacts` — List all warm contacts
- `sc_search_contacts` — Text or semantic (vector) search
- `sc_get_contact` — Fetch one contact by ID
- `sc_upsert_contact` — Create or update a warm contact
- `sc_delete_contact` — Permanently remove a contact

### Initiatives
- `sc_list_initiatives` — List all initiatives
- `sc_get_initiative` — Fetch initiative with sub-projects, stakeholders, action items
- `sc_create_initiative` — Create new initiative
- `sc_update_initiative_status` — Quick status patch
- `sc_delete_initiative` — Permanently remove an initiative

### Sub-Projects
- `sc_create_sub_project` — Create sub-project under an initiative
- `sc_list_sub_projects` — List sub-projects for an initiative
- `sc_delete_sub_project` — Permanently remove a sub-project

### Stakeholders
- `sc_add_stakeholder` — Link contact to initiative with role
- `sc_list_stakeholders` — List stakeholders for an initiative

### Action Items
- `sc_create_action_item` — Create action item linked to initiative/stakeholder
- `sc_list_action_items` — List open action items, optionally by due date

### Content Assets (added April 16, 2026)
- `sc_log_content_idea` — Log a content idea (status always set to "Idea"). Use mid-session whenever an article, campaign concept, LinkedIn post, or any content idea surfaces.
- `sc_list_content_ideas` — List content assets, filterable by venture and status. Defaults to status=Idea.
- `sc_get_content_idea` — Fetch a single content asset by ID.

### Buckets
- `sc_list_buckets` — List all contact buckets
- `sc_create_bucket` — Create a named bucket
- `sc_add_contact_to_bucket` — Add contact to bucket

### Follow-Ups
- `sc_list_open_follow_ups` — All open follow-ups
- `sc_list_overdue_follow_ups` — Overdue follow-ups as of today

### Events
- `sc_list_events` — List events, optionally by venture
- `sc_create_event` — Create new event
- `sc_add_event_guest` — Add guest to event

### Utilities
- `sc_brain_dump` — Batch create initiatives, contacts, and action items
- `sc_health_check` — Confirm Railway API is reachable

## Progress Notes

| Date | Change | Commit |
|---|---|---|
| 2026-04-01 | Initial MCP server deployed with contacts, initiatives, sub-projects, stakeholders, action items, buckets, follow-ups, events, brain dump, health check | `31c322f` |
| 2026-04-01 | Added delete tools (initiative, contact, sub-project) | `d527eda` |
| 2026-04-16 | Added content asset tools: `sc_log_content_idea`, `sc_list_content_ideas`, `sc_get_content_idea`. Closes the gap where content ideas surfaced in Cowork sessions had no way to persist to Railway. | `1193bda` |
| 2026-04-16 | Backfilled 2 ReRev content ideas to Railway that were lost in prior sessions. Confirmed all 29 tools live on deployed MCP server. | N/A (data only) |

## Known Gaps

1. **Cowork tool cache** — After deploying new tools, existing Cowork sessions won't see them until a new session is started. No action needed; this is expected behavior.
2. **Content tab GAS sync** — Content rows added to the Super Connector Sheet don't auto-push to Railway. The `POST /content` endpoint exists but no GAS trigger is wired yet.
3. **Follow-up write tool** — The MCP server can list/read follow-ups but has no `sc_create_follow_up` tool. T018 writes follow-ups directly via GAS. Add if manual follow-up creation from Cowork is needed.
4. **No update/delete for content** — `PUT /content/{id}` and `DELETE /content/{id}` exist on Railway but aren't exposed as MCP tools yet. Add when content lifecycle management is needed.

## Related

- **Railway API repo:** `keyona-rerev/super-connector-api`
- **Tool Registry:** T014 (Super Connector CRM), T017 (Content Idea Capture System)
- **Super Connector Skill:** Loaded automatically in Cowork when SC work is referenced
