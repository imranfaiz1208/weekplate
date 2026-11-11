"""
web.py — Fast, clean, mobile-first Web UI for WeekPlate.
Serves HTML pages for the home page, dashboard, meal editor, grocery checklist,
and public family share page.
Zero AI inside: pure server-rendered HTML and CSS.
"""

import html
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import service as svc

router = APIRouter()
e = html.escape


def layout(title: str, content: str, token: str = "") -> HTMLResponse:
    """Standard responsive layout with clean modern aesthetic."""
    nav_links = ""
    if token:
        nav_links = f"""
        <div style="display:flex;gap:1rem;align-items:center;">
            <a href="/u/{token}/" style="color:#2d6a4f;text-decoration:none;font-weight:600;font-size:0.95rem;">📋 My Plans</a>
            <a href="/" style="color:#6c757d;text-decoration:none;font-size:0.85rem;">Logout</a>
        </div>
        """

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{e(title)} — WeekPlate</title>
    <style>
        :root {{
            --primary: #2d6a4f;
            --primary-hover: #1b4332;
            --accent: #52b788;
            --accent-light: #d8f3dc;
            --bg: #f8f9fa;
            --card-bg: #ffffff;
            --text: #212529;
            --text-muted: #6c757d;
            --border: #e9ecef;
            --radius: 12px;
            --shadow: 0 4px 12px rgba(0,0,0,0.06);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.5;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        header {{
            background: #fff;
            border-bottom: 1px solid var(--border);
            padding: 0.85rem 1.5rem;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .header-inner {{
            max-width: 960px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .logo {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }}
        main {{
            max-width: 960px;
            width: 100%;
            margin: 0 auto;
            padding: 1.5rem;
            flex: 1;
        }}
        .card {{
            background: var(--card-bg);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.4rem;
            padding: 0.65rem 1.25rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.95rem;
            border: none;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.15s ease;
        }}
        .btn-primary {{
            background: var(--primary);
            color: #fff;
        }}
        .btn-primary:hover {{
            background: var(--primary-hover);
        }}
        .btn-secondary {{
            background: #e9ecef;
            color: var(--text);
        }}
        .btn-secondary:hover {{
            background: #dee2e6;
        }}
        .btn-outline {{
            background: transparent;
            border: 1px solid var(--primary);
            color: var(--primary);
        }}
        .btn-outline:hover {{
            background: var(--accent-light);
        }}
        .btn-sm {{
            padding: 0.35rem 0.75rem;
            font-size: 0.85rem;
        }}
        input[type="text"], input[type="email"], input[type="number"], textarea, select {{
            width: 100%;
            padding: 0.65rem 0.85rem;
            border: 1px solid #ced4da;
            border-radius: 8px;
            font-size: 0.95rem;
            font-family: inherit;
        }}
        input:focus, textarea:focus {{
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(82,183,136,0.25);
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.65rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            background: var(--accent-light);
            color: var(--primary);
        }}
        footer {{
            text-align: center;
            padding: 2rem 1rem;
            color: var(--text-muted);
            font-size: 0.85rem;
            border-top: 1px solid var(--border);
            background: #fff;
        }}
        @media (max-width: 640px) {{
            main {{ padding: 1rem; }}
            .card {{ padding: 1.15rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-inner">
            <a href="/" class="logo">🍽️ WeekPlate</a>
            {nav_links}
        </div>
    </header>
    <main>
        {content}
    </main>
    <footer>
        <p><strong>WeekPlate</strong> — Built for Claude with Model Context Protocol (MCP).</p>
        <p style="margin-top:0.3rem;">Zero AI inside. All intelligence powered by your personal Claude subscription.</p>
    </footer>
</body>
</html>
"""
    return HTMLResponse(doc)


# ---------------------------------------------------------------------------
# Route 1: Home Page / Signup
# ---------------------------------------------------------------------------

@router.get("/debug-path")
def debug_path(request: Request):
    return {
        "url": str(request.url),
        "path": request.url.path,
        "scope_path": request.scope.get("path"),
        "headers": dict(request.headers),
    }

@router.get("/")
def home():
    content = f"""
    <div style="text-align:center;padding:2.5rem 1rem 2rem;">
        <span class="badge" style="font-size:0.9rem;padding:0.4rem 1rem;margin-bottom:1rem;">⚡ No AI Markup • 100% on Claude</span>
        <h1 style="font-size:2.4rem;color:#1b4332;margin:0.8rem 0 0.5rem;font-weight:800;letter-spacing:-0.5px;">
            Plan Dinners with Claude.<br>Shop Together with Family.
        </h1>
        <p style="font-size:1.15rem;color:#495057;max-width:580px;margin:0 auto 2rem;">
            Ask Claude to plan your meals. WeekPlate stores your weekly plan, automatically merges all ingredients into one smart grocery list, and lets your family check off items in the store.
        </p>
        
        <div class="card" style="max-width:480px;margin:0 auto;text-align:left;border-top:4px solid var(--primary);">
            <h3 style="margin-bottom:0.6rem;color:#1b4332;">Get Your Personal Claude MCP Link</h3>
            <p style="color:#6c757d;font-size:0.9rem;margin-bottom:1.2rem;">
                Enter your email to create a free account or sign into your existing meal planner.
            </p>
            <form method="POST" action="/signup" style="display:flex;flex-direction:column;gap:0.75rem;">
                <input type="email" name="email" placeholder="you@example.com" required style="padding:0.75rem 1rem;">
                <button type="submit" class="btn btn-primary" style="padding:0.75rem;font-size:1rem;">
                    🚀 Get My Claude Connector Link
                </button>
            </form>
        </div>
    </div>

    <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:1.5rem;margin-top:1.5rem;">
        <div class="card" style="margin:0;">
            <div style="font-size:2rem;margin-bottom:0.5rem;">🧠</div>
            <h3 style="color:#1b4332;margin-bottom:0.4rem;">1. Claude Plans Meals</h3>
            <p style="color:#495057;font-size:0.9rem;">
                Tell Claude: <em>"Plan 5 vegetarian dinners for 4 people under 45 mins."</em> Claude writes recipes tailored to your taste on your own plan.
            </p>
        </div>
        <div class="card" style="margin:0;">
            <div style="font-size:2rem;margin-bottom:0.5rem;">🛒</div>
            <h3 style="color:#1b4332;margin-bottom:0.4rem;">2. Smart Grocery Merging</h3>
            <p style="color:#495057;font-size:0.9rem;">
                WeekPlate combines ingredients across all recipes (2 cans + 1 can = 3 cans chickpeas). No duplicates, no forgotten items.
            </p>
        </div>
        <div class="card" style="margin:0;">
            <div style="font-size:2rem;margin-bottom:0.5rem;">📱</div>
            <h3 style="color:#1b4332;margin-bottom:0.4rem;">3. Shop Live Together</h3>
            <p style="color:#495057;font-size:0.9rem;">
                Open the checklist on your phone in the grocery store aisle. Share the link with your spouse so you can divide and conquer.
            </p>
        </div>
    </div>
    """
    return layout("Plan Meals with Claude", content)


@router.post("/signup")
def signup(email: str = Form(...)):
    user = svc.new_user(email)
    return RedirectResponse(f"/u/{user['token']}/", status_code=303)


# ---------------------------------------------------------------------------
# Route 2: User Dashboard
# ---------------------------------------------------------------------------

@router.get("/u/{token}/")
def dashboard(token: str):
    user = svc.user_by_token(token)
    if not user:
        return layout("Account Not Found", "<div class='card'><h2>Invalid or Expired Link</h2><p><a href='/'>Click here to sign up again</a></p></div>")

    plans = svc.list_plans(user["id"])
    mcp_url = f"{svc.BASE}/u/{token}/mcp"

    plans_html = ""
    if plans:
        for p in plans:
            plans_html += f"""
            <div class="card" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;padding:1.25rem;">
                <div>
                    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.3rem;">
                        <h3 style="color:#1b4332;font-size:1.15rem;">📅 Week of {e(p['week_start'])}</h3>
                        <span class="badge">{p['num_meals']} dinners</span>
                        <span class="badge" style="background:#e9ecef;color:#495057;">{p['servings']} servings</span>
                    </div>
                    <div style="font-size:0.85rem;color:#6c757d;">Created {e(p['created_at'][:10])}</div>
                </div>
                <div style="display:flex;gap:0.6rem;flex-wrap:wrap;">
                    <a href="/u/{token}/plan/{p['id']}" class="btn btn-outline btn-sm">🍽️ View & Edit Plan</a>
                    <a href="/u/{token}/plan/{p['id']}/grocery" class="btn btn-primary btn-sm">🛒 Grocery Checklist</a>
                    <a href="/s/{p['slug']}" target="_blank" class="btn btn-secondary btn-sm">🔗 Family Share</a>
                </div>
            </div>
            """
    else:
        plans_html = f"""
        <div class="card" style="text-align:center;padding:2.5rem 1.5rem;background:#fff;">
            <div style="font-size:3rem;margin-bottom:0.5rem;">🥗</div>
            <h3 style="color:#1b4332;margin-bottom:0.5rem;">No Meal Plans Yet</h3>
            <p style="color:#6c757d;max-width:500px;margin:0 auto 1.5rem;">
                Connect WeekPlate to Claude below, then ask Claude to plan your dinners. Your weekly schedule and consolidated shopping list will appear here automatically!
            </p>
        </div>
        """

    content = f"""
    <div style="margin-bottom:1.5rem;">
        <h1 style="font-size:1.85rem;color:#1b4332;font-weight:700;">Welcome, {e(user['email'])}</h1>
        <p style="color:#6c757d;">Here is your personal Claude connector and your saved meal plans.</p>
    </div>

    <!-- MCP Connection Card -->
    <div class="card" style="border-left:5px solid var(--accent);background:#fcfdfc;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.5rem;">
            <div>
                <h3 style="color:#1b4332;display:flex;align-items:center;gap:0.4rem;">
                    🔌 Your Personal Claude MCP Connector
                </h3>
                <p style="font-size:0.9rem;color:#495057;margin:0.25rem 0 0.75rem;">
                    Add this private link once into Claude to connect your account:
                </p>
            </div>
            <span class="badge" style="background:#e8f5e9;color:#2e7d32;">Ready for Claude</span>
        </div>

        <div style="background:#fff;border:1px solid #ced4da;border-radius:8px;padding:0.75rem 1rem;display:flex;justify-content:space-between;align-items:center;font-family:monospace;font-size:0.9rem;word-break:break-all;margin-bottom:0.75rem;">
            <span id="mcpLink">{mcp_url}</span>
            <button onclick="navigator.clipboard.writeText('{mcp_url}');this.innerText='Copied!';" class="btn btn-secondary btn-sm" style="margin-left:0.5rem;flex-shrink:0;">
                📋 Copy
            </button>
        </div>

        <details style="font-size:0.9rem;color:#495057;">
            <summary style="cursor:pointer;font-weight:600;color:var(--primary);">How to connect to Claude (30 seconds)</summary>
            <ol style="margin:0.75rem 0 0 1.25rem;line-height:1.6;">
                <li>Open <strong>Claude.ai</strong> → Click your profile / Settings → <strong>Connectors</strong></li>
                <li>Click <strong>Add custom connector</strong></li>
                <li>Name: <code>WeekPlate</code> • URL: paste the link above • Save</li>
                <li>Start a chat and say: <code>"Plan 5 vegetarian dinners for 4 people, under 45 minutes each. Add to WeekPlate."</code></li>
            </ol>
        </details>
    </div>

    <!-- Meal Plans Section -->
    <div style="display:flex;justify-content:space-between;align-items:center;margin:2rem 0 1rem;">
        <h2 style="font-size:1.35rem;color:#1b4332;">Your Weekly Plans</h2>
    </div>

    {plans_html}
    """
    return layout("My Dashboard", content, token=token)


# ---------------------------------------------------------------------------
# Route 3: Plan Viewer and Inline Editor
# ---------------------------------------------------------------------------

@router.get("/u/{token}/plan/{plan_id}")
def view_plan(token: str, plan_id: int):
    user = svc.user_by_token(token)
    if not user:
        return RedirectResponse("/")

    try:
        plan = svc.get_plan(user["id"], plan_id)
    except LookupError:
        return layout("Plan Not Found", "<div class='card'><h2>Plan Not Found</h2></div>", token=token)

    meals_cards = ""
    for idx, m in enumerate(plan.get("meals", [])):
        ings_html = "".join(
            f"<li><strong>{i['qty']} {e(i['unit'])}</strong> {e(i['name'])}</li>"
            for i in m.get("ingredients", [])
        )
        notes_p = f"<p style='color:#6c757d;font-size:0.85rem;margin-top:0.4rem;'>💡 {e(m['recipe_notes'])}</p>" if m.get("recipe_notes") else ""

        meals_cards += f"""
        <div class="card" style="margin-bottom:1rem;border-left:4px solid var(--primary);">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.5rem;">
                <div>
                    <span class="badge" style="margin-bottom:0.3rem;">{e(m['day'])}</span>
                    <h3 style="color:#1b4332;font-size:1.2rem;">{e(m['name'])}</h3>
                </div>
                <div style="display:flex;align-items:center;gap:0.5rem;">
                    <span style="font-size:0.85rem;color:#6c757d;">⏱️ {m['minutes']} mins</span>
                    <button onclick="document.getElementById('edit-form-{m['id']}').style.display = document.getElementById('edit-form-{m['id']}').style.display === 'none' ? 'block' : 'none';" class="btn btn-secondary btn-sm">
                        ✏️ Edit
                    </button>
                </div>
            </div>

            {notes_p}

            <div style="margin-top:0.75rem;padding-top:0.75rem;border-top:1px dashed #dee2e6;">
                <strong style="font-size:0.85rem;color:#495057;text-transform:uppercase;letter-spacing:0.5px;">Ingredients:</strong>
                <ul style="margin:0.4rem 0 0 1.25rem;font-size:0.9rem;color:#333;">
                    {ings_html}
                </ul>
            </div>

            <!-- Inline Edit Form (Hidden by default) -->
            <form id="edit-form-{m['id']}" method="POST" action="/u/{token}/plan/{plan_id}/meal/{m['id']}" style="display:none;margin-top:1rem;padding-top:1rem;border-top:1px solid #ced4da;">
                <h4 style="font-size:0.95rem;margin-bottom:0.6rem;color:#1b4332;">Edit {e(m['day'])} Dinner</h4>
                <div style="display:flex;flex-direction:column;gap:0.6rem;">
                    <div>
                        <label style="font-size:0.8rem;font-weight:600;">Meal Name</label>
                        <input type="text" name="name" value="{e(m['name'])}" required>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 2fr;gap:0.6rem;">
                        <div>
                            <label style="font-size:0.8rem;font-weight:600;">Cook Time (mins)</label>
                            <input type="number" name="minutes" value="{m['minutes']}" required>
                        </div>
                        <div>
                            <label style="font-size:0.8rem;font-weight:600;">Recipe Notes</label>
                            <input type="text" name="recipe_notes" value="{e(m.get('recipe_notes', ''))}">
                        </div>
                    </div>
                    <div style="display:flex;gap:0.5rem;margin-top:0.3rem;">
                        <button type="submit" class="btn btn-primary btn-sm">💾 Save Changes</button>
                        <button type="button" onclick="document.getElementById('edit-form-{m['id']}').style.display='none'" class="btn btn-secondary btn-sm">Cancel</button>
                    </div>
                </div>
            </form>
        </div>
        """

    content = f"""
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;margin-bottom:1.5rem;">
        <div>
            <a href="/u/{token}/" style="color:var(--primary);text-decoration:none;font-size:0.9rem;">← Back to All Plans</a>
            <h1 style="font-size:1.85rem;color:#1b4332;margin-top:0.25rem;">📅 Week of {e(plan['week_start'])}</h1>
            <p style="color:#6c757d;font-size:0.9rem;">{len(plan.get('meals', []))} meals planned • {plan.get('servings', 2)} servings</p>
        </div>
        <div style="display:flex;gap:0.6rem;flex-wrap:wrap;">
            <a href="/u/{token}/plan/{plan_id}/grocery" class="btn btn-primary">🛒 View Grocery Checklist</a>
            <a href="/s/{plan['slug']}" target="_blank" class="btn btn-outline">🔗 Public Family Link</a>
        </div>
    </div>

    <div>
        {meals_cards}
    </div>
    """
    return layout(f"Week of {plan['week_start']}", content, token=token)


@router.post("/u/{token}/plan/{plan_id}/meal/{meal_id}")
def update_meal(
    token: str,
    plan_id: int,
    meal_id: int,
    name: str = Form(...),
    minutes: int = Form(30),
    recipe_notes: str = Form(""),
):
    user = svc.user_by_token(token)
    if not user:
        raise HTTPException(401, "Invalid token")
    svc.update_meal_by_id(user["id"], plan_id, meal_id, name=name, minutes=minutes, recipe_notes=recipe_notes)
    return RedirectResponse(f"/u/{token}/plan/{plan_id}", status_code=303)


# ---------------------------------------------------------------------------
# Route 4: Smart Merged Grocery Checklist
# ---------------------------------------------------------------------------

@router.get("/u/{token}/plan/{plan_id}/grocery")
def grocery_checklist(token: str, plan_id: int):
    user = svc.user_by_token(token)
    if not user:
        return RedirectResponse("/")

    try:
        plan = svc.get_plan(user["id"], plan_id)
    except LookupError:
        return layout("Plan Not Found", "<div class='card'><h2>Plan Not Found</h2></div>", token=token)

    groceries = svc.get_grocery_list(plan_id, user_id=user["id"])
    total_items = len(groceries)
    checked_items = sum(1 for g in groceries if g["checked"])
    progress_pct = int((checked_items / total_items * 100)) if total_items > 0 else 0

    items_html = ""
    for g in groceries:
        is_checked = bool(g["checked"])
        item_style = "text-decoration:line-through;color:#adb5bd;" if is_checked else "color:#212529;font-weight:500;"
        check_icon = "✅" if is_checked else "⬜"

        items_html += f"""
        <div style="display:flex;align-items:center;justify-content:space-between;padding:0.75rem 0.5rem;border-bottom:1px solid #f1f3f5;">
            <div style="display:flex;align-items:center;gap:0.75rem;">
                <form method="POST" action="/u/{token}/plan/{plan_id}/grocery/{g['id']}/toggle" style="margin:0;">
                    <button type="submit" style="background:none;border:none;cursor:pointer;font-size:1.35rem;padding:0;line-height:1;">
                        {check_icon}
                    </button>
                </form>
                <span style="{item_style};font-size:1.05rem;">
                    {e(g['name'])}
                </span>
            </div>
            <span class="badge" style="background:#e9ecef;color:#495057;font-size:0.85rem;">
                {g['total_qty']} {e(g['unit'])}
            </span>
        </div>
        """

    content = f"""
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;margin-bottom:1.25rem;">
        <div>
            <a href="/u/{token}/plan/{plan_id}" style="color:var(--primary);text-decoration:none;font-size:0.9rem;">← Back to Meal Plan</a>
            <h1 style="font-size:1.85rem;color:#1b4332;margin-top:0.25rem;">🛒 Smart Grocery List</h1>
            <p style="color:#6c757d;font-size:0.9rem;">Consolidated ingredients for week of {e(plan['week_start'])}</p>
        </div>
        <a href="/s/{plan['slug']}" target="_blank" class="btn btn-outline">
            🔗 Family Share Link
        </a>
    </div>

    <!-- Shopping Progress -->
    <div class="card" style="padding:1rem 1.25rem;margin-bottom:1rem;background:#fff;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;font-weight:600;font-size:0.95rem;">
            <span>Shopping Progress</span>
            <span style="color:var(--primary);">{checked_items} of {total_items} items ({progress_pct}%)</span>
        </div>
        <div style="height:8px;background:#e9ecef;border-radius:4px;overflow:hidden;">
            <div style="width:{progress_pct}%;height:100%;background:var(--accent);transition:width 0.2s ease;"></div>
        </div>
    </div>

    <!-- Consolidated Checklist -->
    <div class="card" style="padding:1rem 1.25rem;">
        <div style="padding-bottom:0.5rem;margin-bottom:0.5rem;border-bottom:2px solid var(--border);color:#6c757d;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.5px;display:flex;justify-content:space-between;">
            <span>Item</span>
            <span>Quantity</span>
        </div>
        {items_html if items_html else "<p style='text-align:center;color:#6c757d;padding:1rem;'>No items in grocery list.</p>"}
    </div>
    """
    return layout("Grocery Checklist", content, token=token)


@router.post("/u/{token}/plan/{plan_id}/grocery/{item_id}/toggle")
def toggle_grocery_item_auth(token: str, plan_id: int, item_id: int):
    user = svc.user_by_token(token)
    if not user:
        raise HTTPException(401, "Invalid token")
    svc.toggle_grocery_item(plan_id, item_id)
    return RedirectResponse(f"/u/{token}/plan/{plan_id}/grocery", status_code=303)


# ---------------------------------------------------------------------------
# Route 5: Public Family Share Page (Zero login needed)
# ---------------------------------------------------------------------------

@router.get("/s/{slug}")
def public_shared_plan(slug: str):
    try:
        plan = svc.by_slug(slug)
    except LookupError:
        return layout("Shared Plan Not Found", "<div class='card'><h2>This shared meal plan does not exist.</h2></div>")

    groceries = plan.get("grocery_list", [])
    total_items = len(groceries)
    checked_items = sum(1 for g in groceries if g["checked"])
    progress_pct = int((checked_items / total_items * 100)) if total_items > 0 else 0

    meals_list = "".join(
        f"""
        <div style="padding:0.75rem 0;border-bottom:1px solid #f1f3f5;">
            <span class="badge" style="font-size:0.75rem;">{e(m['day'])}</span>
            <strong style="color:#1b4332;margin-left:0.4rem;font-size:1rem;">{e(m['name'])}</strong>
            <span style="font-size:0.85rem;color:#6c757d;margin-left:0.4rem;">(⏱️ {m['minutes']}m)</span>
        </div>
        """
        for m in plan.get("meals", [])
    )

    groceries_list = "".join(
        f"""
        <div style="display:flex;align-items:center;justify-content:space-between;padding:0.65rem 0;border-bottom:1px solid #f1f3f5;">
            <div style="display:flex;align-items:center;gap:0.6rem;">
                <form method="POST" action="/s/{slug}/grocery/{g['id']}/toggle" style="margin:0;">
                    <button type="submit" style="background:none;border:none;cursor:pointer;font-size:1.25rem;padding:0;line-height:1;">
                        {"✅" if g['checked'] else "⬜"}
                    </button>
                </form>
                <span style="{'text-decoration:line-through;color:#adb5bd;' if g['checked'] else 'color:#212529;font-weight:500;'}font-size:1rem;">
                    {e(g['name'])}
                </span>
            </div>
            <span class="badge" style="background:#e9ecef;color:#495057;">
                {g['total_qty']} {e(g['unit'])}
            </span>
        </div>
        """
        for g in groceries
    )

    content = f"""
    <div style="text-align:center;margin-bottom:1.5rem;">
        <span class="badge" style="margin-bottom:0.5rem;">👨‍👩‍👧 Shared Family Menu</span>
        <h1 style="font-size:2rem;color:#1b4332;">Dinner Plan • Week of {e(plan['week_start'])}</h1>
        <p style="color:#6c757d;">{len(plan.get('meals', []))} meals planned for {plan.get('servings', 2)} people</p>
    </div>

    <!-- Dinners -->
    <div class="card">
        <h3 style="color:#1b4332;margin-bottom:0.75rem;">🍽️ Planned Dinners</h3>
        {meals_list}
    </div>

    <!-- Live Shopping List -->
    <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
            <h3 style="color:#1b4332;">🛒 Interactive Grocery List</h3>
            <span style="color:var(--primary);font-weight:600;font-size:0.9rem;">{checked_items}/{total_items} done</span>
        </div>
        <p style="color:#6c757d;font-size:0.85rem;margin-bottom:1rem;">
            Anyone with this link can check off items while shopping together at the grocery store.
        </p>
        {groceries_list}
    </div>
    """
    return layout(f"Shared Menu - Week of {plan['week_start']}", content)


@router.post("/s/{slug}/grocery/{item_id}/toggle")
def public_toggle_grocery_item(slug: str, item_id: int):
    try:
        plan = svc.by_slug(slug)
    except LookupError:
        raise HTTPException(404, "Plan not found")
    svc.toggle_grocery_item(plan["id"], item_id)
    return RedirectResponse(f"/s/{slug}", status_code=303)
