# Databricks App Proposal: EHR Clinical Explorer

**Idea:** A single Databricks app that surfaces your existing EHR data through two experiences—**Genie** (natural-language Q&A) and an **AI/BI dashboard** (pre-built charts and KPIs)—so users can explore patients, imaging, and clinical notes in one place.

---

## 1. App concept

| Component | Purpose |
|-----------|--------|
| **Genie** | Reuse your existing Genie space **build-con-mp** (ehr, lung_cancer_images, parsed_clinical_notes). Users type questions in plain language and get SQL-backed answers. |
| **Dashboard** | New AI/BI (Lakeview) dashboard with a few curated views: patient counts, diagnosis/stage breakdown, imaging counts per patient, recent clinical notes summary. All queries run on your three Delta tables. |

**User flow:** Open the app → choose “Ask Genie” or “View dashboard” → same underlying data, two ways to explore.

---

## 2. High-level architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Databricks App: EHR Clinical Explorer                           │
│  (Streamlit or Dash, single process)                             │
├─────────────────────────────────────────────────────────────────┤
│  [ Tab / Section 1: Ask Genie ]  [ Tab / Section 2: Dashboard ] │
│                                                                  │
│  • Embed or deep-link to           • Embed or deep-link to      │
│    Genie space "build-con-mp"        published AI/BI dashboard │
│  • Resource: genie-space (valueFrom) • Dashboard built in        │
│  • Optional: Genie Conversation      workspace, then embedded   │
│    API in-app (ask_genie)            via iframe / embed URL     │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  App resources (app.yaml):                                      │
│  • genie-space  → build-con-mp (Can view, Can run)                │
│  • sql-warehouse → for dashboard queries / optional in-app SQL   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Existing data (no change)                                       │
│  • melissap.melissa_pang.ehr                                    │
│  • melissap.melissa_pang.lung_cancer_images                     │
│  • melissap.melissa_pang.parsed_clinical_notes                  │
│  (Genie space already has these tables; dashboard uses same)     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. How to build it (high level)

### Step 1: Create the app and `app.yaml`

- **Framework:** Streamlit (fastest) or Dash (if you want more control over layout and interactivity).
- **App config** (`app.yaml`):
  - Add resource **Genie space** with key `genie-space`, bound to your existing space **build-con-mp** (or pass space ID via `valueFrom`).
  - Add resource **SQL warehouse** with key `sql-warehouse` (for dashboard execution and optional in-app queries).
- **Auth:** Use Databricks `Config()` (service principal or user auth as needed); no hardcoded tokens.

### Step 2: Genie in the app

- **Option A (simplest):** In the app UI, show a **deep link** to the Genie space (e.g. `https://<workspace>/genie?space_id=<id>`). User clicks and opens Genie in the same or new tab. Space ID comes from `valueFrom` env (e.g. `GENIE_SPACE_ID`).
- **Option B (embedded):** If your workspace supports embedding Genie, embed the Genie experience in an iframe in one tab/section. Embed URL format depends on Databricks (e.g. embed or app-run URL for the space).
- **Option C (API-driven):** Use the **Genie Conversation API** in the backend: user types a question in the app, app calls `ask_genie(space_id, question)`, and you display the returned SQL + result (or summary) in the app. No iframe; full control over UI.

### Step 3: Dashboard

- **Create the dashboard** in the workspace (AI/BI / Lakeview):
  - One dashboard, e.g. “EHR Clinical Summary”.
  - Datasets: your three tables (ehr, lung_cancer_images, parsed_clinical_notes).
  - Pages/widgets examples:
    - Patient count, diagnosis and stage breakdown (from `ehr`).
    - Image count by patient or by modality (from `lung_cancer_images`).
    - Recent notes or counts by chief_complaint (from `parsed_clinical_notes`).
  - **Publish** the dashboard so it has a stable embed URL.
- **In the app:** Add a second tab/section that embeds the published dashboard via **iframe** (Share → Embed dashboard). Use the embed URL; the app runs in the same workspace, so basic embedding with user login usually works. Pass the dashboard URL from config or env if you want to avoid hardcoding.

### Step 4: App layout and deployment

- **Layout:** Two main sections (tabs or sidebar): “Ask Genie” and “View dashboard”. Optional: short blurb and links to “Open Genie in new tab” / “Open dashboard in new tab” if embedding is limited.
- **Deployment:** Use Databricks Apps (CLI or Asset Bundles). Point the app at your repo or upload the app directory; set resources (genie-space, sql-warehouse) in the app config; deploy and test with a real user.

---

## 4. Suggested implementation order

| Order | Task | Notes |
|-------|------|--------|
| 1 | Create app directory, `app.yaml`, minimal Streamlit/Dash app | Add genie-space + sql-warehouse resources |
| 2 | Implement “Ask Genie” (deep link or Genie Conversation API) | Use `GENIE_SPACE_ID` from env |
| 3 | Build and publish one AI/BI dashboard on the three tables | Test all SQL in workspace first |
| 4 | Add “Dashboard” section (iframe or link to published dashboard) | Use embed URL from Share |
| 5 | Deploy app to Databricks, test with real users | Check logs and resource permissions |

---

## 5. Files you’ll end up with (example)

```
app/
├── app.py              # Streamlit or Dash entry (tabs: Genie, Dashboard)
├── app.yaml            # App config + resources: genie-space, sql-warehouse
├── requirements.txt    # streamlit or dash + databricks-sdk (if using API)
└── README.md           # How to run and deploy
```

Optional:

- `backend.py` – if you use Genie Conversation API or SQL warehouse for extra queries.
- Env/config for dashboard URL so you can switch dashboards without code changes.

---

## 6. Summary

- **Idea:** One app = **Genie** (your existing build-con-mp space) + **one new dashboard** on the same three Delta tables.
- **Build:** Create a thin app (Streamlit or Dash), wire Genie via link/embed or Conversation API, create and publish one AI/BI dashboard, embed or link it in the app, deploy with `app.yaml` resources (genie-space, sql-warehouse).
- **Data:** No change to your existing notebooks or tables; the app only consumes what you already have (Genie space + Delta tables).

---

## 7. Implemented: Streamlit + Genie Conversation API + in-app Dashboard

The app is implemented in the **`app/`** directory:

- **Streamlit** with two tabs: **Ask Genie** and **Dashboard**.
- **Ask Genie**: In-app chat using the [Genie Conversation API](https://docs.databricks.com/genie/conversation-api.html). Users type questions; the app calls `start_conversation` / `create_message` and displays Genie's text and SQL in the same page. No iframe. Sidebar: **Open Genie in new tab** (full Genie UI), **New conversation** (reset thread).
- **Dashboard**: In-app metrics and bar charts by running SQL on the app warehouse via the Statement Execution API (patient count, imaging studies, clinical notes; diagnosis breakdown, stage breakdown, images by modality). No iframe. If `DASHBOARD_EMBED_URL` is set, a link at the bottom opens the full Databricks AI/BI dashboard in a new tab.
- **app.yaml** uses `valueFrom`: `genie-space` → `GENIE_SPACE_ID`, `sql-warehouse` → `DATABRICKS_WAREHOUSE_ID`. Optional env `DASHBOARD_EMBED_URL` for the full-dashboard link.
- The app's **service principal** needs **USE CATALOG** / **USE SCHEMA** / **SELECT** on `melissap.melissa_pang` (ehr, lung_cancer_images, parsed_clinical_notes) for the Dashboard tab to show data. Find the principal in the app's **Configure** → **Authorization** tab.

See **`app/README.md`** for deploy steps, resource setup, permissions, and troubleshooting (e.g. dashboard not showing data).
