"""
seed_data.py — Pre-populates the database with a reviewer test account and sample meal plan.
Zero AI inside: pure test fixtures.
"""

import db
import service as svc

def seed():
    print("Initialising database...")
    db.init()

    test_email = "reviewer@weekplate.com"
    test_token = "testtoken123"

    conn = db.get_conn()
    try:
        user = conn.execute("SELECT * FROM users WHERE token = ?", (test_token,)).fetchone()
        if not user:
            print(f"Creating test reviewer user ({test_email})...")
            cur = conn.execute(
                "INSERT INTO users (email, token) VALUES (?, ?)",
                (test_email, test_token),
            )
            user_id = cur.lastrowid
            conn.commit()
        else:
            user_id = user["id"]
            print(f"Using existing test reviewer user (ID {user_id})...")
    finally:
        conn.close()

    # Sample vegetarian meal plan (matching the guide example)
    sample_meals = [
        {
            "day": "Monday",
            "name": "Chickpea & Spinach Coconut Curry",
            "minutes": 35,
            "recipe_notes": "One-pot curry with warm basmati rice.",
            "ingredients": [
                {"name": "chickpeas", "qty": 2, "unit": "can"},
                {"name": "coconut milk", "qty": 1, "unit": "can"},
                {"name": "spinach", "qty": 1, "unit": "bunch"},
                {"name": "garlic", "qty": 3, "unit": "cloves"},
                {"name": "onion", "qty": 1, "unit": "medium"},
                {"name": "curry powder", "qty": 2, "unit": "tbsp"},
            ]
        },
        {
            "day": "Tuesday",
            "name": "Black Bean & Corn Sheet-Pan Fajitas",
            "minutes": 30,
            "recipe_notes": "Roast peppers and beans on high heat, serve in warm tortillas.",
            "ingredients": [
                {"name": "black beans", "qty": 1, "unit": "can"},
                {"name": "corn", "qty": 1, "unit": "can"},
                {"name": "bell peppers", "qty": 3, "unit": "medium"},
                {"name": "onion", "qty": 1, "unit": "medium"},
                {"name": "tortillas", "qty": 8, "unit": "count"},
                {"name": "lime", "qty": 2, "unit": "count"},
            ]
        },
        {
            "day": "Wednesday",
            "name": "Creamy Tomato & Basil Chickpea Pasta",
            "minutes": 25,
            "recipe_notes": "Toss penne with crushed tomatoes and chickpeas for extra protein.",
            "ingredients": [
                {"name": "chickpeas", "qty": 1, "unit": "can"},  # Notice: merges with Monday (2+1 = 3 cans)!
                {"name": "penne pasta", "qty": 1, "unit": "box"},
                {"name": "crushed tomatoes", "qty": 1, "unit": "can"},
                {"name": "garlic", "qty": 2, "unit": "cloves"},  # Merges with Monday (3+2 = 5 cloves)!
                {"name": "fresh basil", "qty": 1, "unit": "bunch"},
                {"name": "olive oil", "qty": 2, "unit": "tbsp"},
            ]
        },
        {
            "day": "Thursday",
            "name": "Mediterranean Quinoa Salad Bowls",
            "minutes": 25,
            "recipe_notes": "Prep ahead cold bowl with crisp cucumbers and kalamata olives.",
            "ingredients": [
                {"name": "quinoa", "qty": 1, "unit": "cup"},
                {"name": "cucumber", "qty": 2, "unit": "medium"},
                {"name": "cherry tomatoes", "qty": 1, "unit": "pint"},
                {"name": "feta cheese", "qty": 1, "unit": "block"},
                {"name": "olive oil", "qty": 2, "unit": "tbsp"},
                {"name": "lemon", "qty": 1, "unit": "count"},
            ]
        },
        {
            "day": "Friday",
            "name": "Thai Coconut Butternut Squash Soup",
            "minutes": 40,
            "recipe_notes": "Smooth blended soup topped with toasted pumpkin seeds.",
            "ingredients": [
                {"name": "butternut squash", "qty": 1, "unit": "medium"},
                {"name": "coconut milk", "qty": 1, "unit": "can"},  # Merges with Monday (1+1 = 2 cans)!
                {"name": "vegetable broth", "qty": 4, "unit": "cups"},
                {"name": "ginger", "qty": 1, "unit": "thumb"},
                {"name": "garlic", "qty": 2, "unit": "cloves"},
            ]
        }
    ]

    print("Seeding sample meal plan...")
    plan = svc.save_meal_plan(
        user_id=user_id,
        week_start="2026-11-16",
        servings=4,
        meals=sample_meals,
    )

    print("\n✅ Seeding complete!")
    print(f"Reviewer Dashboard URL: {svc.BASE}/u/{test_token}/")
    print(f"Reviewer MCP Connector:  {svc.BASE}/u/{test_token}/mcp")
    print(f"Sample Plan Edit URL:    {plan['edit_url']}")
    print(f"Sample Grocery List URL: {plan['grocery_url']}")
    print(f"Family Public Share URL: {plan['share_url']}")
    print(f"Merged Groceries Count:  {len(plan['grocery_list'])} consolidated items")


if __name__ == "__main__":
    seed()

