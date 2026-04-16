"""
Super Connector MCP Server
Wraps the Railway API so Claude can query and write to Super Connector
from any session without network restrictions.
"""

import os
import json
import httpx
from typing import Optional
from mcp.server.fastmcp import FastMCP

# ── CONFIG ────────────────────────────────────────────────────────────────────

RAILWAY_BASE = os.environ.get("SC_RAILWAY_URL", "https://super-connector-api-production.up.railway.app")
SC_API_KEY   = os.environ.get("SC_API_KEY", "")
PORT         = int(os.environ.get("PORT", 8080))

mcp = FastMCP("super_connector_mcp", host="0.0.0.0", port=PORT)

# ── SHARED CLIENT ─────────────────────────────────────────────────────────────

def _headers() -> dict:
    return {"X-API-Key": SC_API_KEY, "Content-Type": "application/json"}

async def _get(path: str, params: dict = None) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{RAILWAY_BASE}{path}", headers=_headers(), params=params)
        r.raise_for_status()
        return r.json()

async def _post(path: str, body: dict) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(f"{RAILWAY_BASE}{path}", headers=_headers(), json=body)
        r.raise_for_status()
        return r.json()

async def _put(path: str, body: dict) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.put(f"{RAILWAY_BASE}{path}", headers=_headers(), json=body)
        r.raise_for_status()
        return r.json()

async def _patch(path: str, body: dict) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.patch(f"{RAILWAY_BASE}{path}", headers=_headers(), json=body)
        r.raise_for_status()
        return r.json()

async def _delete(path: str) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.delete(f"{RAILWAY_BASE}{path}", headers=_headers())
        r.raise_for_status()
        return r.json()

def _ok(data) -> str:
    return json.dumps(data, indent=2, default=str)

def _err(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        return f"Error {e.response.status_code}: {e.response.text}"
    return f"Error: {str(e)}"

# ════════════════════════════════════════════════════════════════════════════
# INITIATIVES
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool(name="sc_list_initiatives", annotations={"readOnlyHint": True})
async def sc_list_initiatives() -> str:
    """List all initiatives from Super Connector Railway API.
    Returns all initiatives with their status, priority, venture, goal, brain_dump, and sub-projects.
    Use this at the start of every Super Connector session to load current state.
    """
    try:
        return _ok(await _get("/initiatives"))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_get_initiative", annotations={"readOnlyHint": True})
async def sc_get_initiative(initiative_id: str) -> str:
    """Get a single initiative by ID including its sub-projects, stakeholders, action items, and buckets.

    Args:
        initiative_id: The initiative ID (e.g. 'INI-001', 'P009')
    """
    try:
        return _ok(await _get(f"/initiative/{initiative_id}"))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_create_initiative", annotations={"readOnlyHint": False, "destructiveHint": False})
async def sc_create_initiative(
    initiative_name: str,
    venture: str,
    goal: str,
    status: Optional[str] = "Brain Dump",
    priority: Optional[str] = "Medium",
    brain_dump: Optional[str] = "",
    core_question: Optional[str] = "",
    phoebe_cadence: Optional[str] = "Weekly",
    notes: Optional[str] = "",
) -> str:
    """Create a new initiative in Super Connector."""
    try:
        body = {
            "initiative_name": initiative_name,
            "venture": venture,
            "goal": goal,
            "status": status,
            "priority": priority,
            "brain_dump": brain_dump,
            "core_question": core_question,
            "phoebe_cadence": phoebe_cadence,
            "notes": notes,
        }
        return _ok(await _post("/initiative", body))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_update_initiative_status", annotations={"readOnlyHint": False, "idempotentHint": True})
async def sc_update_initiative_status(initiative_id: str, status: str) -> str:
    """Quickly update the status of an initiative.

    Args:
        initiative_id: The initiative ID
        status: Brain Dump / Planning / Active / Paused / Complete
    """
    try:
        return _ok(await _patch(f"/initiative/{initiative_id}/status", {"status": status}))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_delete_initiative", annotations={"readOnlyHint": False, "destructiveHint": True})
async def sc_delete_initiative(initiative_id: str) -> str:
    """Permanently delete an initiative by ID. Use for removing duplicates or retired initiatives.

    Args:
        initiative_id: The initiative ID to delete (e.g. 'INI-1775079223973674')
    """
    try:
        return _ok(await _delete(f"/initiative/{initiative_id}"))
    except Exception as e:
        return _err(e)


# ════════════════════════════════════════════════════════════════════════════
# SUB-PROJECTS
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool(name="sc_create_sub_project", annotations={"readOnlyHint": False, "destructiveHint": False})
async def sc_create_sub_project(
    initiative_id: str,
    sub_project_name: str,
    description: Optional[str] = "",
    status: Optional[str] = "Not Started",
    priority: Optional[str] = "Medium",
    owner: Optional[str] = "",
    notes: Optional[str] = "",
) -> str:
    """Create a sub-project under an existing initiative.

    Args:
        initiative_id: Parent initiative ID (required)
        sub_project_name: Name of the sub-project
        description: What this sub-project covers
        status: Not Started / In Progress / Blocked / Complete
        priority: Critical / High / Medium / Low / Parked
        owner: Who owns this sub-project
        notes: Any additional notes
    """
    try:
        body = {
            "initiative_id": initiative_id,
            "sub_project_name": sub_project_name,
            "description": description,
            "status": status,
            "priority": priority,
            "owner": owner,
            "notes": notes,
        }
        return _ok(await _post("/sub-project", body))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_list_sub_projects", annotations={"readOnlyHint": True})
async def sc_list_sub_projects(initiative_id: str) -> str:
    """List all sub-projects for a given initiative."""
    try:
        return _ok(await _get(f"/initiative/{initiative_id}/sub-projects"))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_delete_sub_project", annotations={"readOnlyHint": False, "destructiveHint": True})
async def sc_delete_sub_project(sub_project_id: str) -> str:
    """Permanently delete a sub-project by ID.

    Args:
        sub_project_id: The sub-project ID to delete (e.g. 'SUB-1234567890')
    """
    try:
        return _ok(await _delete(f"/sub-project/{sub_project_id}"))
    except Exception as e:
        return _err(e)


# ════════════════════════════════════════════════════════════════════════════
# CONTACTS
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool(name="sc_list_contacts", annotations={"readOnlyHint": True})
async def sc_list_contacts(limit: int = 50, offset: int = 0) -> str:
    """List all contacts from Super Connector."""
    try:
        return _ok(await _get("/contacts", params={"limit": limit, "offset": offset}))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_search_contacts", annotations={"readOnlyHint": True})
async def sc_search_contacts(query: str, semantic: bool = False, top_k: int = 10) -> str:
    """Search contacts by name/text or semantic similarity.

    Args:
        query: Search query — name, org, role, or descriptive phrase
        semantic: If True uses vector search (descriptive phrases). If False uses fast text search (names).
        top_k: Number of results to return
    """
    try:
        if semantic:
            return _ok(await _post("/search", {"query": query, "top_k": top_k}))
        else:
            return _ok(await _get("/contacts/search", params={"q": query, "limit": top_k}))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_get_contact", annotations={"readOnlyHint": True})
async def sc_get_contact(contact_id: str) -> str:
    """Get a single contact by ID including their initiative links and bucket memberships."""
    try:
        return _ok(await _get(f"/contact/{contact_id}"))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_upsert_contact", annotations={"readOnlyHint": False, "idempotentHint": True})
async def sc_upsert_contact(
    contact_id: str,
    full_name: str,
    title_role: Optional[str] = "",
    organization: Optional[str] = "",
    how_we_met: Optional[str] = "",
    venture: Optional[str] = "",
    what_building: Optional[str] = "",
    what_need: Optional[str] = "",
    what_offer: Optional[str] = "",
    relationship_health: Optional[str] = "",
    activation_potential: Optional[str] = "",
    notes: Optional[str] = "",
) -> str:
    """Create or update a warm contact. Cold outreach contacts go to Apollo/Pipedrive only."""
    try:
        body = {
            "contact_id": contact_id,
            "full_name": full_name,
            "title_role": title_role,
            "organization": organization,
            "how_we_met": how_we_met,
            "venture": venture,
            "what_building": what_building,
            "what_need": what_need,
            "what_offer": what_offer,
            "relationship_health": relationship_health,
            "activation_potential": activation_potential,
            "notes": notes,
        }
        return _ok(await _post("/contact", body))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_delete_contact", annotations={"readOnlyHint": False, "destructiveHint": True})
async def sc_delete_contact(contact_id: str) -> str:
    """Permanently delete a contact by ID. Use with caution — this cannot be undone.

    Args:
        contact_id: The contact ID to delete (e.g. 'C1234567890')
    """
    try:
        return _ok(await _delete(f"/contact/{contact_id}"))
    except Exception as e:
        return _err(e)


# ════════════════════════════════════════════════════════════════════════════
# STAKEHOLDERS
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool(name="sc_add_stakeholder", annotations={"readOnlyHint": False, "destructiveHint": False})
async def sc_add_stakeholder(
    initiative_id: str,
    full_name: str,
    contact_id: Optional[str] = "",
    sub_project_id: Optional[str] = "",
    role: Optional[str] = "Warm Path",
    action_needed: Optional[str] = "Outreach",
    engagement_status: Optional[str] = "Not Contacted",
    notes: Optional[str] = "",
) -> str:
    """Link a contact to an initiative as a stakeholder with a role and action needed."""
    try:
        body = {
            "initiative_id": initiative_id,
            "full_name": full_name,
            "contact_id": contact_id,
            "sub_project_id": sub_project_id,
            "role": role,
            "action_needed": action_needed,
            "engagement_status": engagement_status,
            "notes": notes,
        }
        return _ok(await _post("/stakeholder", body))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_list_stakeholders", annotations={"readOnlyHint": True})
async def sc_list_stakeholders(initiative_id: str) -> str:
    """List all stakeholders for a given initiative."""
    try:
        return _ok(await _get(f"/initiative/{initiative_id}/stakeholders"))
    except Exception as e:
        return _err(e)


# ════════════════════════════════════════════════════════════════════════════
# ACTION ITEMS
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool(name="sc_create_action_item", annotations={"readOnlyHint": False, "destructiveHint": False})
async def sc_create_action_item(
    description: str,
    initiative_id: Optional[str] = "SPRINT",
    action_type: Optional[str] = "Research",
    priority: Optional[str] = "Medium",
    due_date: Optional[str] = None,
    stakeholder_id: Optional[str] = "",
    sub_project_id: Optional[str] = "",
    source: Optional[str] = "Brain Dump",
) -> str:
    """Create an action item linked to an initiative and/or stakeholder."""
    try:
        body = {
            "description": description,
            "initiative_id": initiative_id,
            "action_type": action_type,
            "priority": priority,
            "due_date": due_date,
            "stakeholder_id": stakeholder_id,
            "sub_project_id": sub_project_id,
            "source": source,
            "status": "Open",
        }
        return _ok(await _post("/action-item", body))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_list_action_items", annotations={"readOnlyHint": True})
async def sc_list_action_items(due_before: Optional[str] = None) -> str:
    """List all open action items, optionally filtered by due date (YYYY-MM-DD)."""
    try:
        params = {"due_before": due_before} if due_before else {}
        return _ok(await _get("/action-items", params=params))
    except Exception as e:
        return _err(e)


# ════════════════════════════════════════════════════════════════════════════
# BUCKETS
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool(name="sc_list_buckets", annotations={"readOnlyHint": True})
async def sc_list_buckets() -> str:
    """List all contact buckets in Super Connector."""
    try:
        return _ok(await _get("/buckets"))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_create_bucket", annotations={"readOnlyHint": False, "destructiveHint": False})
async def sc_create_bucket(
    name: str,
    description: Optional[str] = "",
    color: Optional[str] = "",
    initiative_id: Optional[str] = "",
) -> str:
    """Create a named contact bucket (e.g. 'Network Initiators', 'Climate Tech Advisors')."""
    try:
        body = {"name": name, "description": description, "color": color, "initiative_id": initiative_id}
        return _ok(await _post("/bucket", body))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_add_contact_to_bucket", annotations={"readOnlyHint": False, "idempotentHint": True})
async def sc_add_contact_to_bucket(bucket_id: str, contact_id: str) -> str:
    """Add a contact to a bucket."""
    try:
        return _ok(await _post(f"/bucket/{bucket_id}/members", {"contact_id": contact_id}))
    except Exception as e:
        return _err(e)


# ════════════════════════════════════════════════════════════════════════════
# BRAIN DUMP (batch create)
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool(name="sc_brain_dump", annotations={"readOnlyHint": False, "destructiveHint": False})
async def sc_brain_dump(payload_json: str) -> str:
    """Batch create initiatives, contacts, and action items in one call.

    Args:
        payload_json: JSON string: {"initiatives": [...], "contacts": [...], "action_items": [...]}
    """
    try:
        body = json.loads(payload_json)
        return _ok(await _post("/brain-dump", body))
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON — {str(e)}"
    except Exception as e:
        return _err(e)


# ════════════════════════════════════════════════════════════════════════════
# FOLLOW-UPS
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool(name="sc_list_open_follow_ups", annotations={"readOnlyHint": True})
async def sc_list_open_follow_ups() -> str:
    """List all open follow-ups across all contacts."""
    try:
        return _ok(await _get("/follow-ups/open"))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_list_overdue_follow_ups", annotations={"readOnlyHint": True})
async def sc_list_overdue_follow_ups() -> str:
    """List all overdue follow-ups as of today."""
    try:
        return _ok(await _get("/follow-ups/overdue"))
    except Exception as e:
        return _err(e)


# ════════════════════════════════════════════════════════════════════════════
# EVENTS
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool(name="sc_list_events", annotations={"readOnlyHint": True})
async def sc_list_events(venture: Optional[str] = None) -> str:
    """List all events, optionally filtered by venture."""
    try:
        params = {"venture": venture} if venture else {}
        return _ok(await _get("/events", params=params))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_create_event", annotations={"readOnlyHint": False, "destructiveHint": False})
async def sc_create_event(
    event_name: str,
    venture: str,
    event_type: Optional[str] = "Hosted",
    status: Optional[str] = "Planning",
    event_date: Optional[str] = None,
    location: Optional[str] = "",
    description: Optional[str] = "",
    initiative_id: Optional[str] = "",
    notes: Optional[str] = "",
) -> str:
    """Create a new event in Super Connector."""
    try:
        body = {
            "event_name": event_name,
            "venture": venture,
            "event_type": event_type,
            "status": status,
            "event_date": event_date,
            "location": location,
            "description": description,
            "initiative_id": initiative_id,
            "notes": notes,
        }
        return _ok(await _post("/event", body))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_add_event_guest", annotations={"readOnlyHint": False, "destructiveHint": False})
async def sc_add_event_guest(
    event_id: str,
    full_name: str,
    contact_id: Optional[str] = "",
    role: Optional[str] = "Attendee",
    guest_status: Optional[str] = "Invited",
    notes: Optional[str] = "",
) -> str:
    """Add a guest to an event."""
    try:
        body = {
            "event_id": event_id,
            "full_name": full_name,
            "contact_id": contact_id,
            "role": role,
            "guest_status": guest_status,
            "notes": notes,
        }
        return _ok(await _post("/event-guest", body))
    except Exception as e:
        return _err(e)


# ════════════════════════════════════════════════════════════════════════════
# CONTENT ASSETS
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool(name="sc_log_content_idea", annotations={"readOnlyHint": False, "destructiveHint": False})
async def sc_log_content_idea(
    content_name: str,
    venture: str,
    content_type: Optional[str] = "Article",
    notes: Optional[str] = "",
    initiative_tags: Optional[str] = "",
    activation_angle: Optional[str] = "",
    asset_link: Optional[str] = "",
) -> str:
    """Log a content idea to the Super Connector assets registry. Status is always set to 'Idea'.
    Use this whenever a content idea surfaces mid-session — article, LinkedIn post, campaign concept, etc.
    Never let ideas live only in chat. Log them here immediately.

    Args:
        content_name: Short, clear name for the idea (e.g. 'ReRev article on AI audit for 10-person startups')
        venture: ReRev Labs / Prismm / BTC / Sekhmetic / Internal
        content_type: Article / Campaign Concept / Gifting Moment / Sequence Variant / Data Drop /
                      Collab Hook / Case Study / Demo / Newsletter Issue / Event Recap
        notes: 1-3 sentences capturing context, why it surfaced, and what the spark was
        initiative_tags: Comma-separated initiative IDs if relevant (e.g. 'INI-004,INI-002')
        activation_angle: The angle or hook this piece should use
        asset_link: URL if a draft or reference already exists
    """
    try:
        body = {
            "content_name": content_name,
            "content_type": content_type,
            "venture": venture,
            "status": "Idea",
            "notes": notes,
            "initiative_tags": initiative_tags,
            "activation_angle": activation_angle,
            "asset_link": asset_link,
        }
        return _ok(await _post("/content", body))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_list_content_ideas", annotations={"readOnlyHint": True})
async def sc_list_content_ideas(venture: Optional[str] = None, status: Optional[str] = "Idea") -> str:
    """List content assets from the Super Connector registry.
    Defaults to showing all Idea-status assets. Pass venture to filter by brand.
    Pass status=None to see all statuses.

    Args:
        venture: Filter by venture — ReRev Labs / Prismm / BTC / Sekhmetic / Internal (optional)
        status: Filter by status — Idea / Draft / In Review / Active / Archived (default: Idea)
    """
    try:
        params = {}
        if venture:
            params["venture"] = venture
        if status:
            params["status"] = status
        return _ok(await _get("/content", params=params))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sc_get_content_idea", annotations={"readOnlyHint": True})
async def sc_get_content_idea(content_id: str) -> str:
    """Fetch a single content asset by ID.

    Args:
        content_id: The content asset ID (e.g. 'C-1775324077811')
    """
    try:
        return _ok(await _get(f"/content/{content_id}"))
    except Exception as e:
        return _err(e)


# ════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool(name="sc_health_check", annotations={"readOnlyHint": True})
async def sc_health_check() -> str:
    """Check that the Super Connector Railway API is reachable and responding."""
    try:
        return _ok(await _get("/health"))
    except Exception as e:
        return _err(e)


# ── ENTRYPOINT ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
