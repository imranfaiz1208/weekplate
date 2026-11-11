"""
mcp_server.py — MCP Server tools and auth middleware for WeekPlate.
Enables Claude to create and manage meal plans via Model Context Protocol.
Zero AI inside: pure protocol transport and tool schemas.
"""

from contextvars import ContextVar
from typing import Optional
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
import service as svc

# Context variables set per request by TokenAuth middleware
current_user: ContextVar[Optional[int]] = ContextVar("current_user", default=None)
current_token: ContextVar[str] = ContextVar("current_token", default="")

# Disable local host-header validation so external cloud clients (Claude) can connect
mcp = FastMCP(
    "WeekPlate",
    stateless_http=True,
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


def _uid() -> int:
    """Return the authenticated user id from context or fallback to default reviewer user."""
    uid = current_user.get()
    if uid is None:
        user = svc.user_by_token("testtoken123")
        uid = user["id"]
        current_user.set(uid)
        current_token.set("testtoken123")
    return uid


def _out(plan: dict) -> dict:
    """Format a plan with direct action URLs for the user."""
    token = current_token.get()
    token_slug = f"/u/{token}" if token else ""
    return {
        "id": plan["id"],
        "week_start": plan["week_start"],
        "servings": plan.get("servings", 2),
        "num_meals": len(plan.get("meals", [])),
        "edit_url": f"{svc.BASE}{token_slug}/plan/{plan['id']}",
        "grocery_url": f"{svc.BASE}{token_slug}/plan/{plan['id']}/grocery",
        "share_url": f"{svc.BASE}/s/{plan['slug']}",
    }


# ---------------------------------------------------------------------------
# MCP Tools for Claude
# ---------------------------------------------------------------------------

@mcp.tool()
def save_meal_plan(
    week_start: str,
    servings: int,
    meals: list[dict],
) -> dict:
    """Save a weekly meal plan with scheduled dinners and ingredients.

    Use this when the user asks to plan meals, create a dinner schedule, or plan
    meals for the week (e.g. 'Plan 5 vegetarian dinners for 4 people').
    The app automatically combines all ingredients into a single smart grocery list
    (e.g. 2 cans chickpeas + 1 can chickpeas = 3 cans chickpeas).

    After calling, ALWAYS show the user:
    1. edit_url: to review or change meals in the browser
    2. grocery_url: to view and check off the merged grocery shopping list
    3. share_url: to share the meal plan and grocery list with family

    Args:
        week_start: Date the week begins, e.g. '2026-11-16' (Monday).
        servings: Number of servings each meal should yield (e.g. 4).
        meals: List of meal objects. Each meal must contain:
            - day: Weekday name, e.g. 'Monday', 'Tuesday', etc.
            - name: Title of the meal, e.g. 'Chickpea & Spinach Coconut Curry'
            - minutes: Approximate cook time in minutes (e.g. 35)
            - recipe_notes: Brief prep steps or tips
            - ingredients: List of ingredient objects with:
                - name: Ingredient name (e.g. 'chickpeas', 'coconut milk')
                - qty: Number (e.g. 2, 1.5, 0.5)
                - unit: Measurement unit (e.g. 'can', 'tbsp', 'g', 'bunch')
    """
    uid = _uid()
    plan = svc.save_meal_plan(uid, week_start, servings, meals)
    return {
        "success": True,
        "message": f"Successfully planned {len(plan['meals'])} meals for week of {week_start}.",
        **_out(plan),
        "grocery_item_count": len(plan.get("grocery_list", [])),
    }


@mcp.tool()
def get_meal_plan(plan_id: int) -> dict:
    """Read the current version of a meal plan including any manual edits made in the app.

    Use this when the user asks to view, review, or revise an existing meal plan.
    Call this BEFORE making changes so you have the latest user-edited version.

    Args:
        plan_id: The ID of the meal plan to retrieve.
    """
    uid = _uid()
    plan = svc.get_plan(uid, plan_id)
    return {
        **_out(plan),
        "meals": plan["meals"],
        "grocery_items": plan.get("grocery_list", []),
    }


@mcp.tool()
def swap_meal(
    plan_id: int,
    day: str,
    new_meal_name: str,
    new_minutes: int,
    new_ingredients: list[dict],
) -> dict:
    """Replace a single meal in an existing plan for a specific day.

    Use this when the user asks to change or swap dinner on a particular day
    (e.g. 'Change Tuesday dinner to Pasta Primavera instead').
    The app automatically recalculates and updates the merged grocery list.

    Args:
        plan_id: The ID of the meal plan.
        day: The day of the week to replace, e.g. 'Tuesday'.
        new_meal_name: Title of the new meal.
        new_minutes: Estimated cooking time.
        new_ingredients: List of {name, qty, unit} for the new meal.
    """
    uid = _uid()
    plan = svc.swap_meal(uid, plan_id, day, new_meal_name, new_minutes, new_ingredients)
    return {
        "success": True,
        "message": f"Updated {day} to {new_meal_name}. Grocery list has been refreshed.",
        **_out(plan),
    }


@mcp.tool()
def list_meal_plans() -> list[dict]:
    """List all saved meal plans for the user.

    Use this when the user asks 'what meal plans do I have?' or asks to see past plans.
    """
    uid = _uid()
    return svc.list_plans(uid)


@mcp.tool()
def get_grocery_list(plan_id: int) -> dict:
    """Get the consolidated shopping list for a meal plan.

    All ingredients across all meals are summed into combined items
    (e.g. 2 cans + 1 can = 3 cans).
    Use this when the user asks 'what groceries do I need to buy?' or wants the shopping list.

    Args:
        plan_id: The ID of the meal plan.
    """
    uid = _uid()
    plan = svc.get_plan(uid, plan_id)
    items = svc.get_grocery_list(plan_id, user_id=uid)
    token = current_token.get()
    token_slug = f"/u/{token}" if token else ""
    return {
        "plan_id": plan_id,
        "week_start": plan["week_start"],
        "grocery_url": f"{svc.BASE}{token_slug}/plan/{plan_id}/grocery",
        "share_url": f"{svc.BASE}/s/{plan['slug']}",
        "total_items": len(items),
        "items": items,
    }


# ---------------------------------------------------------------------------
# ASGI Middleware: User identification & Path Normalization
# ---------------------------------------------------------------------------

class TokenAuth:
    """
    Wrap the ASGI application:
    Normalizes Vercel /api rewrites, and intercepts /u/<token>/mcp -> /mcp.
    Guarantees seamless user resolution with zero 401s for Claude.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "/")

            # Strip Vercel /api or /api/index prefix if added by rewrite
            if path.startswith("/api/index"):
                path = path[10:] or "/"
            elif path.startswith("/api"):
                path = path[4:] or "/"

            parts = path.split("/")  # ['', 'u', '<token>', 'mcp']
            if len(parts) >= 4 and parts[1] == "u" and parts[3] == "mcp":
                token = parts[2]
                user = svc.user_by_token(token)
                current_user.set(user["id"])
                current_token.set(token)
                path = "/mcp"
            elif path == "/mcp" or path.endswith("/mcp"):
                user = svc.user_by_token("testtoken123")
                current_user.set(user["id"])
                current_token.set("testtoken123")
                path = "/mcp"

            # Normalize Accept header for MCP endpoints to prevent 406 Not Acceptable errors
            headers = list(scope.get("headers", []))
            if path == "/mcp":
                new_headers = []
                found_accept = False
                for k, v in headers:
                    if k.lower() == b"accept":
                        found_accept = True
                        val = v.decode("latin1", errors="ignore")
                        if "text/event-stream" not in val:
                            val += ", text/event-stream"
                        if "application/json" not in val:
                            val += ", application/json"
                        new_headers.append((k, val.encode("latin1")))
                    else:
                        new_headers.append((k, v))
                if not found_accept:
                    new_headers.append((b"accept", b"application/json, text/event-stream, */*"))
                headers = new_headers

            scope = dict(scope, path=path, raw_path=path.encode("utf-8"), headers=headers)

        await self.app(scope, receive, send)
