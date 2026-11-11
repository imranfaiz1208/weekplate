# 🍽️ WeekPlate — The Meal Planner That Runs on Claude

> **Volopay Founder's Office Assignment**  
> Build a business on Claude with MCP (Model Context Protocol).  
> **100% Client-Side AI — Zero AI Inside the App.**

---

## ⚡ Submission Links (For Reviewers)

- **Live Web App:** `https://weekplate-mif2.vercel.app`
- **Reviewer Instant Login:** `https://weekplate-mif2.vercel.app/u/testtoken123/` *(no password needed)*
- **Claude MCP Connector URL:** `https://weekplate-mif2.vercel.app/u/testtoken123/mcp`
- **Family Public Share Page:** `https://weekplate-mif2.vercel.app/s/sample_family_plan`

---

## 🔌 How to Connect to Claude (30 Seconds)

1. Open **Claude.ai** → Click your name / Settings → **Connectors**.
2. Click **Add custom connector**.
3. Fill in:
   - **Name:** `WeekPlate`
   - **URL:** `https://weekplate-mif2.vercel.app/u/testtoken123/mcp`
4. Click **Save**.
5. Start a new chat, make sure the **WeekPlate** connector is enabled, and type:
   > *"Plan 5 vegetarian dinners for 4 people, under 45 minutes each, no mushrooms. Save it in WeekPlate."*
6. Claude will generate the recipes and call `save_meal_plan`.
7. Click the returned `edit_url` or open your live dashboard: your dinners are scheduled and your grocery shopping list is already consolidated!

---

## 🛡️ Zero AI Inside — Proof

This application contains **ZERO AI models, zero API keys, and zero machine learning libraries**.
All thinking and recipe planning is performed by the customer's own Claude subscription.
WeekPlate is a pure web app that manages structured data, persistence, and arithmetic.

```bash
# Verify no AI keys or SDKs in codebase:
grep -ri "openai"    weekplate/
grep -ri "anthropic" weekplate/
grep -ri "api_key"   weekplate/
grep -ri "sk-"       weekplate/
# (All results will be empty)
```

---

## 💡 What WeekPlate Does (That Claude Cannot Do Alone)

| Capability | Claude Alone | WeekPlate + Claude |
|---|---|---|
| **Recipe Ideation & Dietary Needs** | ✅ Great at writing recipes | 🧠 Claude does the thinking on customer's plan |
| **Persistence Across Days/Weeks** | ❌ Lost in long chat history | 💾 Saved in permanent database calendar |
| **Grocery List Consolidation** | ⚠️ Chat math can hallucinate counts | 🧮 Exact arithmetic merging (2 cans + 1 can = 3 cans) |
| **Interactive Shopping Checklist** | ❌ Cannot tap to check off in aisle | 📱 Mobile-friendly checklist with strikethrough |
| **Family Collaboration** | ❌ Partner cannot see your chat | 🔗 Public family share link for joint grocery shopping |

---

## 🚀 Quick Start (Local Setup)

```bash
# 1. Clone repository and navigate to folder
cd weekplate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed database with sample reviewer data
python seed_data.py

# 4. Start local development server
uvicorn main:app --reload --port 8000

# 5. Open browser
# Home page:        http://localhost:8000
# Reviewer Account: http://localhost:8000/u/testtoken123/
# MCP Endpoint:     http://localhost:8000/u/testtoken123/mcp
```

---

## 🌐 Deploy to Render in 3 Minutes

1. Push this folder to a GitHub repository.
2. In Render dashboard (`render.com`), choose **New > Web Service**.
3. Select your repository.
4. Set:
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt && python seed_data.py`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variable:
   - `BASE_URL`: `https://your-app-name.onrender.com`
6. Click **Deploy Web Service**.

---

## 💰 The Economics (Arithmetic & Margins)

### 1. Cost Per Customer per Month
- **Hosting (Render Web Service):** ~$7.00/mo (fixed, serves 1,000+ users)
- **Database (SQLite / Managed Postgres):** $0.00 – $5.00/mo
- **Bandwidth & Storage:** ~$0.05/user (text only, extremely lightweight)
- **AI Cost:** **$0.00** *(Customer pays Anthropic directly for Claude)*
- **Payment Processing (Stripe):** ~$0.45 per $5 transaction (2.9% + 30¢)
- **Total Variable Cost:** **~$0.50/month per customer**
- **Gross Margin:** **90%** on a $5/month subscription!

### 2. Pricing
- **$5/month per household** (or $48/year).
- *Value Anchor:* Eliminates daily dinner decision fatigue and cuts 15-20% off grocery waste by consolidating ingredients.

### 3. First 100 Customers Funnel
- **Parenting & Cooking Subreddits (r/MealPrepSunday, r/EatCheapAndHealthy):** 5 demo clips → 2,500 visits → 120 signups → 35 paying customers.
- **Claude & MCP Developer Communities:** 1 showcase post → 1,500 views → 60 signups → 25 paying customers.
- **Shared Family Link Viral Loop:** Every shared grocery link has a *"Made with WeekPlate"* footer → 30 customers.
- **Micro-influencer cooking TikTok/Reels:** 15 customers.
- **Total:** **105 paying customers** in Month 1.

### 4. 1-Year and 3-Year Projections
- **Year 1:** 400 paying households @ $5/mo = **$2,000 MRR ($24k ARR)** at 90% margin.
- **Year 3:** 4,500 paying households @ $6/mo (with Instacart integration) = **$27,000 MRR ($324k ARR)**.

---

## 🎙️ 5-Minute Pitch Script (Word-for-Word)

### Part 1: Who You Are (45 sec)
> "Hi, I'm [Your Name], founder of WeekPlate. I'm a software engineer with a background in full-stack development, cloud infrastructure, and product design. Over the past 24 hours, I built and deployed WeekPlate from scratch for the Volopay assignment. WeekPlate turns one sentence in Claude into an organized weekly dinner calendar and a consolidated grocery checklist that couples and families can shop with in real time."

### Part 2: Your Best Work (30 sec)
> "My best work so far is [Mention your strongest project / internship / hackathon win]. In that project, I [mention 1 metric, e.g., scaled to 500+ active users / reduced latency by 35% / won 1st place in hackathon], which proved to me the value of rapid execution and building tools that real people actually use."

### Part 3: Why This Business Will Win (1 min)
> "Every household asks the same stressful question every single evening: *'What's for dinner?'* Claude is incredible at suggesting personalized recipes in seconds. But a chat window is not a meal planner. You can't take a chat transcript to the grocery store, check off items as you walk down aisle 4, or share an editable checklist with your spouse.
> 
> That's where WeekPlate wins. We connect to Claude via the Model Context Protocol. Claude does 100% of the heavy language thinking on the customer's own subscription plan. WeekPlate has zero AI inside—meaning our marginal AI cost is literally zero. We store the weekly schedule, merge identical ingredients across all recipes using pure arithmetic, and provide a live checklist that syncs on your phone in the store. It's the missing half of what Claude already does best."

### Part 4: Demo Walkthrough (2 min)
- **0:00 – Claude Connector:** *"Here is my Claude chat. You can see the WeekPlate connector is active."*
- **0:20 – The Prompt:** *"I type: 'Plan 5 vegetarian dinners for 4 people, under 45 minutes each, no mushrooms. Add to WeekPlate.' Claude plans the menu and calls our `save_meal_plan` tool."*
- **0:50 – Live Web Dashboard:** *"Claude finishes and gives us our links. Let's switch over to the live web app. Here is our dashboard—the week of November 16th is saved with all 5 dinners."*
- **1:15 – Manual Edit Screen:** *"I can click 'View & Edit Plan'. Notice I can edit anything by hand. If I want to change Wednesday's cook time or swap the recipe, I click Edit, change it, and save. No AI needed."*
- **1:35 – Merged Grocery Checklist:** *"Now look at the magic: the smart grocery list. Notice that chickpeas appeared in both Monday's curry and Wednesday's pasta. WeekPlate automatically calculated 2 cans + 1 can = 3 cans chickpeas. Total math, zero hallucination."*
- **1:50 – Live Toggle & Public Share:** *"I can tap items to check them off as I buy them. And with our public family link, my partner can open this on their phone without logging in and check off items simultaneously."*

### Part 5: The Money (45 sec)
> "Our unit economics are unbeatable. Because the AI thinking runs on the customer's own Claude subscription, our hosting cost per user is under 50 cents a month. At $5 a month per household, we operate at a 90% gross margin.
> 
> To acquire our first 100 customers, we leverage food and meal-prep communities on Reddit, Claude user groups, and the viral footer on every shared family grocery link. By Year 1, we project 400 paying families generating $2,000 monthly recurring revenue. By Year 3, scaling into grocery delivery partnerships like Instacart, we reach 4,500 subscribers and $27,000 MRR. Thank you!"
