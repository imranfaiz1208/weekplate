"""
service.py — Core business logic for WeekPlate.
Used by both the web interface AND the MCP tools.
Contains zero AI: pure data storage, validation, and ingredient merging arithmetic.
"""

import os
import secrets
from datetime import datetime, timezone
from typing import Optional

import db

# Auto-detect base URL for Vercel, Render, or local development
if os.environ.get("BASE_URL"):
    BASE = os.environ.get("BASE_URL")
elif os.environ.get("VERCEL_URL"):
    BASE = f"https://{os.environ.get('VERCEL_URL')}"
else:
    BASE = "http://localhost:8000"

# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

VALID_DAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}


def _validate_day(day: str) -> str:
    """Normalise and validate a day-of-week string."""
    d = day.strip().lower()[:3]
    if d not in VALID_DAYS:
        # Fallback to Mon if unrecognised
        return "Mon"
    day_map = {
        "mon": "Monday",
        "tue": "Tuesday",
        "wed": "Wednesday",
        "thu": "Thursday",
        "fri": "Friday",
        "sat": "Saturday",
        "sun": "Sunday",
    }
    return day_map.get(d, "Monday")


def _validate_qty(qty) -> float:
    """Ensure quantity is a positive number."""
    try:
        q = float(qty)
    except (ValueError, TypeError):
        return 1.0
    if q < 0:
        raise ValueError(f"Quantity must be zero or more, got {q}")
    return round(q, 2)


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------

def new_user(email: str) -> dict:
    """Create a new user with a random secret token."""
    email = email.strip()
    if not email or "@" not in email:
        raise ValueError("A valid email address is required.")
    token = secrets.token_urlsafe(24)
    conn = db.get_conn()
    try:
        # If user with email already exists, return existing user
        existing = conn.execute(
            "SELECT id, email, token FROM users WHERE email = ?", (email,)
        ).fetchone()
        if existing:
            return dict(existing)

        cur = conn.execute(
            "INSERT INTO users (email, token) VALUES (?, ?)",
            (email, token),
        )
        conn.commit()
        return {"id": cur.lastrowid, "email": email, "token": token}
    finally:
        conn.close()


def user_by_token(token: str) -> Optional[dict]:
    """Look up a user by their secret token. Returns None if not found."""
    if not token:
        return None
    conn = db.get_conn()
    try:
        row = conn.execute(
            "SELECT id, email, token FROM users WHERE token = ?", (token,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def user_by_id(user_id: int) -> Optional[dict]:
    """Look up a user by their numeric id."""
    conn = db.get_conn()
    try:
        row = conn.execute(
            "SELECT id, email, token FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Meal plan CRUD
# ---------------------------------------------------------------------------

def save_meal_plan(
    user_id: int,
    week_start: str,
    servings: int,
    meals: list[dict],
) -> dict:
    """
    Persist a full weekly meal plan.
    Meals format: list of dicts with keys:
      day (str), name (str), minutes (int), recipe_notes (str),
      ingredients (list of {name, qty, unit})
    """
    if servings < 1:
        servings = 2
    if not meals:
        raise ValueError("At least one meal is required to create a meal plan.")

    slug = secrets.token_urlsafe(12)
    now = datetime.now(timezone.utc).isoformat()
    conn = db.get_conn()
    try:
        # Insert plan
        cur = conn.execute(
            "INSERT INTO meal_plans (user_id, week_start, servings, slug, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, week_start.strip(), int(servings), slug, now),
        )
        plan_id = cur.lastrowid

        # Insert meals & ingredients
        for m in meals:
            day = _validate_day(m.get("day", "Monday"))
            name = m.get("name", "").strip() or "Untitled Dinner"
            minutes = int(m.get("minutes", 30))
            recipe_notes = m.get("recipe_notes", "").strip()

            meal_cur = conn.execute(
                "INSERT INTO meals (plan_id, day, name, minutes, recipe_notes) "
                "VALUES (?, ?, ?, ?, ?)",
                (plan_id, day, name, minutes, recipe_notes),
            )
            meal_id = meal_cur.lastrowid

            for ing in m.get("ingredients", []):
                qty = _validate_qty(ing.get("qty", 1))
                ing_name = ing.get("name", "").strip()
                if not ing_name:
                    continue
                unit = ing.get("unit", "item").strip().lower()
                conn.execute(
                    "INSERT INTO ingredients (meal_id, name, qty, unit) "
                    "VALUES (?, ?, ?, ?)",
                    (meal_id, ing_name, qty, unit),
                )

        conn.commit()

        # Generate merged grocery list (sums quantities across meals)
        _merge_grocery_list(plan_id, conn=conn)

        return _plan_response(plan_id, conn)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# Alias for compatibility
create_plan = save_meal_plan


def get_plan(user_id: int, plan_id: int) -> dict:
    """Return a full plan (meals + ingredients + grocery list) owned by user_id."""
    conn = db.get_conn()
    try:
        plan = conn.execute(
            "SELECT * FROM meal_plans WHERE id = ? AND user_id = ?",
            (plan_id, user_id),
        ).fetchone()
        if not plan:
            raise LookupError(f"Plan {plan_id} not found for this user.")
        return _plan_response(plan_id, conn)
    finally:
        conn.close()


def list_plans(user_id: int) -> list[dict]:
    """List all plans for a user with meal counts and URLs."""
    conn = db.get_conn()
    try:
        user = conn.execute("SELECT token FROM users WHERE id = ?", (user_id,)).fetchone()
        token = user["token"] if user else ""

        rows = conn.execute(
            "SELECT id, week_start, servings, slug, created_at "
            "FROM meal_plans WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        ).fetchall()

        out = []
        for r in rows:
            meal_count = conn.execute(
                "SELECT COUNT(*) FROM meals WHERE plan_id = ?", (r["id"],)
            ).fetchone()[0]
            out.append({
                "id": r["id"],
                "week_start": r["week_start"],
                "servings": r["servings"],
                "slug": r["slug"],
                "created_at": r["created_at"],
                "num_meals": meal_count,
                "edit_url": f"{BASE}/u/{token}/plan/{r['id']}",
                "grocery_url": f"{BASE}/u/{token}/plan/{r['id']}/grocery",
                "share_url": f"{BASE}/s/{r['slug']}",
            })
        return out
    finally:
        conn.close()


def update_meal_by_id(
    user_id: int,
    plan_id: int,
    meal_id: int,
    name: Optional[str] = None,
    minutes: Optional[int] = None,
    recipe_notes: Optional[str] = None,
) -> dict:
    """Update fields of a specific meal by meal_id."""
    conn = db.get_conn()
    try:
        _assert_plan_owner(conn, plan_id, user_id)
        updates, params = [], []
        if name is not None:
            updates.append("name = ?")
            params.append(name.strip())
        if minutes is not None:
            updates.append("minutes = ?")
            params.append(int(minutes))
        if recipe_notes is not None:
            updates.append("recipe_notes = ?")
            params.append(recipe_notes.strip())
        if updates:
            params.extend([meal_id, plan_id])
            conn.execute(
                f"UPDATE meals SET {', '.join(updates)} WHERE id = ? AND plan_id = ?",
                params,
            )
            conn.commit()
        return _plan_response(plan_id, conn)
    finally:
        conn.close()


def swap_meal(
    user_id: int,
    plan_id: int,
    day: str,
    new_meal_name: str,
    new_minutes: int,
    new_ingredients: list[dict],
) -> dict:
    """
    Replace a meal for a given day, then regenerate the grocery list.
    """
    norm_day = _validate_day(day)
    if not new_meal_name.strip():
        raise ValueError("New meal name is required.")
    conn = db.get_conn()
    try:
        _assert_plan_owner(conn, plan_id, user_id)

        # Delete existing meals for that day
        old_meals = conn.execute(
            "SELECT id FROM meals WHERE plan_id = ? AND day = ?",
            (plan_id, norm_day),
        ).fetchall()
        for om in old_meals:
            conn.execute("DELETE FROM ingredients WHERE meal_id = ?", (om["id"],))
        conn.execute("DELETE FROM meals WHERE plan_id = ? AND day = ?", (plan_id, norm_day))

        # Insert new meal
        cur = conn.execute(
            "INSERT INTO meals (plan_id, day, name, minutes, recipe_notes) "
            "VALUES (?, ?, ?, ?, '')",
            (plan_id, norm_day, new_meal_name.strip(), int(new_minutes)),
        )
        meal_id = cur.lastrowid

        for ing in new_ingredients:
            qty = _validate_qty(ing.get("qty", 1))
            ing_name = ing.get("name", "").strip()
            if not ing_name:
                continue
            unit = ing.get("unit", "item").strip().lower()
            conn.execute(
                "INSERT INTO ingredients (meal_id, name, qty, unit) "
                "VALUES (?, ?, ?, ?)",
                (meal_id, ing_name, qty, unit),
            )

        conn.commit()
        _merge_grocery_list(plan_id, conn=conn)
        return _plan_response(plan_id, conn)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Grocery list functions
# ---------------------------------------------------------------------------

def toggle_grocery_item(plan_id: int, item_id: int) -> dict:
    """Toggle the checked status of a grocery item."""
    conn = db.get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM grocery_items WHERE id = ? AND plan_id = ?",
            (item_id, plan_id),
        ).fetchone()
        if not row:
            raise LookupError(f"Grocery item {item_id} not found in plan {plan_id}.")
        new_checked = 0 if row["checked"] else 1
        conn.execute(
            "UPDATE grocery_items SET checked = ? WHERE id = ?",
            (new_checked, item_id),
        )
        conn.commit()
        return {**dict(row), "checked": new_checked}
    finally:
        conn.close()


def get_grocery_list(plan_id: int, user_id: Optional[int] = None) -> list[dict]:
    """Return the merged grocery list for a plan."""
    conn = db.get_conn()
    try:
        if user_id is not None:
            _assert_plan_owner(conn, plan_id, user_id)
        rows = conn.execute(
            "SELECT id, plan_id, name, total_qty, unit, checked "
            "FROM grocery_items WHERE plan_id = ? ORDER BY checked ASC, name ASC",
            (plan_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def by_slug(slug: str) -> dict:
    """Public access: look up a plan by its share slug."""
    conn = db.get_conn()
    try:
        plan = conn.execute(
            "SELECT * FROM meal_plans WHERE slug = ?", (slug,)
        ).fetchone()
        if not plan:
            raise LookupError("Shared meal plan not found.")
        return _plan_response(plan["id"], conn)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Smart Grocery Merging Algorithm (Pure Arithmetic, Zero AI)
# ---------------------------------------------------------------------------

def _merge_grocery_list(plan_id: int, *, conn=None):
    """
    Recalculate the merged grocery list from all meals' ingredients.
    Combines identical ingredient names across all meals:
    e.g. 2 cans chickpeas + 1 can chickpeas = 3 cans chickpeas.
    """
    close = False
    if conn is None:
        conn = db.get_conn()
        close = True
    try:
        # Preserve checked status for already-checked items
        old_checked = set()
        for row in conn.execute(
            "SELECT name, checked FROM grocery_items WHERE plan_id = ?",
            (plan_id,),
        ).fetchall():
            if row["checked"]:
                old_checked.add(row["name"].strip().lower())

        # Wipe old grocery list for this plan
        conn.execute("DELETE FROM grocery_items WHERE plan_id = ?", (plan_id,))

        # Fetch all ingredients across all meals in this plan
        rows = conn.execute(
            """
            SELECT i.name, i.qty, i.unit
            FROM ingredients i
            JOIN meals m ON m.id = i.meal_id
            WHERE m.plan_id = ?
            """,
            (plan_id,),
        ).fetchall()

        # Merge matching (name, unit) pairs
        merged: dict[tuple[str, str], dict] = {}
        for r in rows:
            clean_name = r["name"].strip()
            norm_name = clean_name.lower()
            unit = r["unit"].strip().lower()
            key = (norm_name, unit)
            if key in merged:
                merged[key]["total_qty"] += r["qty"]
            else:
                merged[key] = {
                    "display_name": clean_name.title(),
                    "norm_name": norm_name,
                    "total_qty": r["qty"],
                    "unit": unit,
                }

        # Insert consolidated items
        for (norm_name, unit), info in merged.items():
            checked = 1 if norm_name in old_checked else 0
            rounded_qty = round(info["total_qty"], 2)
            conn.execute(
                "INSERT INTO grocery_items (plan_id, name, total_qty, unit, checked) "
                "VALUES (?, ?, ?, ?, ?)",
                (plan_id, info["display_name"], rounded_qty, unit, checked),
            )

        conn.commit()
    finally:
        if close:
            conn.close()


def _assert_plan_owner(conn, plan_id: int, user_id: int):
    """Verify that a plan belongs to user_id."""
    row = conn.execute(
        "SELECT id FROM meal_plans WHERE id = ? AND user_id = ?",
        (plan_id, user_id),
    ).fetchone()
    if not row:
        raise PermissionError(f"Plan {plan_id} not found or access denied.")


def _plan_response(plan_id: int, conn) -> dict:
    """Build a complete plan dict with nested meals, ingredients, and URLs."""
    plan = conn.execute("SELECT * FROM meal_plans WHERE id = ?", (plan_id,)).fetchone()
    if not plan:
        raise LookupError(f"Plan {plan_id} not found.")

    user = conn.execute("SELECT token FROM users WHERE id = ?", (plan["user_id"],)).fetchone()
    token = user["token"] if user else ""

    plan_dict = dict(plan)
    plan_dict["edit_url"] = f"{BASE}/u/{token}/plan/{plan_id}"
    plan_dict["grocery_url"] = f"{BASE}/u/{token}/plan/{plan_id}/grocery"
    plan_dict["share_url"] = f"{BASE}/s/{plan['slug']}"

    # Meals
    meal_rows = conn.execute(
        "SELECT * FROM meals WHERE plan_id = ? ORDER BY id", (plan_id,)
    ).fetchall()
    meals_out = []
    for mr in meal_rows:
        meal = dict(mr)
        ings = conn.execute(
            "SELECT id, name, qty, unit FROM ingredients WHERE meal_id = ? ORDER BY id",
            (mr["id"],),
        ).fetchall()
        meal["ingredients"] = [dict(i) for i in ings]
        meals_out.append(meal)
    plan_dict["meals"] = meals_out

    # Groceries
    groceries = conn.execute(
        "SELECT id, name, total_qty, unit, checked FROM grocery_items WHERE plan_id = ? ORDER BY checked ASC, name ASC",
        (plan_id,),
    ).fetchall()
    plan_dict["grocery_list"] = [dict(g) for g in groceries]

    return plan_dict
