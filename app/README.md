# EHR Clinical Explorer (Databricks App)

Streamlit app with two tabs, both using your EHR data in **melissap.melissa_pang** (ehr, lung_cancer_images, parsed_clinical_notes):

- **Ask Genie** — In-app chat via the [Genie Conversation API](https://docs.databricks.com/genie/conversation-api.html): type questions, get answers and SQL in the same page. No iframe. Sidebar: "Open Genie in new tab" for the full Genie UI. "New conversation" starts a fresh thread.
- **Dashboard** — In-app metrics and bar charts (patient count, imaging studies, clinical notes; diagnosis breakdown, stage breakdown, images by modality) by running SQL on the app warehouse via the Statement Execution API. Optional link to open the full Databricks AI/BI dashboard in a new tab when `DASHBOARD_EMBED_URL` is set.

Resources (configure in Apps UI): **genie-space** (key `genie-space` → build-con-mp), **sql-warehouse** (key `sql-warehouse`). The app's service principal needs data permissions for the Dashboard tab to show data (see Permissions below).

## Workspace

Deploy this app to the workspace defined in the **tko** profile (`~/.databrickscfg`). The Genie space **build-con-mp** and the SQL warehouse must be in that same workspace so the app and Genie use the same data and host.

## Prerequisites

- **Notebooks 1–4** run in the **tko** workspace: volume + Genie space **build-con-mp**, synthetic data, Delta tables (ehr, lung_cancer_images, parsed_clinical_notes), and tables registered in the Genie space.
- A **SQL warehouse** in that workspace (for the app and for Genie/dashboard queries).

## App resources (configure in Apps UI)

When creating or editing the app, add:

| Resource type   | Key (default)   | Bind to                    | Permissions   |
|----------------|-----------------|----------------------------|---------------|
| Genie space    | `genie-space`  | **build-con-mp**           | Can view, Can run |
| SQL warehouse  | `sql-warehouse`| Warehouse id `e9b34f7a2e4b0561` (or your warehouse) | Can use       |

These are also documented in `app.yaml` and `app.py` (Genie space name and default warehouse id for local run).

Optional: set env var `DASHBOARD_EMBED_URL` to the published dashboard embed URL (Share → Embed dashboard) to show the Dashboard tab.

## Local run (optional)

```bash
cd app
pip install -r requirements.txt
export GENIE_SPACE_ID=<your-build-con-mp-space-id>
export DATABRICKS_WAREHOUSE_ID=<warehouse-id>
# Optional: export DASHBOARD_EMBED_URL=<embed-url>
streamlit run app.py --server.port=8000
```

Use the same Databricks profile (e.g. `~/.databrickscfg`) so `Config()` can resolve the workspace host.

## Deploy to Databricks

### 1. Install / configure Databricks CLI

- Install the [Databricks CLI](https://docs.databricks.com/dev-tools/cli/index.html) and configure the **tko** profile in `~/.databrickscfg` (see [WORKSPACE.md](../WORKSPACE.md) in the project root).
- Ensure the **tko** workspace has the Genie space **build-con-mp** and a SQL warehouse.

### 2. Create the app (once)

From the **project root** (parent of `app/`), using profile **tko** so the app is created in that workspace:

```bash
databricks apps create ehr-clinical-explorer --profile tko
```

Or in the **tko** workspace: **Apps** → **Create app** → name `ehr-clinical-explorer`.

### 3. Upload source code

Replace `<your-username>` with your username in the tko workspace (e.g. `melissa.pang@databricks.com`):

```bash
# From project root (claude-playground/) — use profile tko
databricks workspace mkdirs /Workspace/Users/<your-username>/apps/ehr-clinical-explorer --profile tko
databricks workspace import-dir ./app /Workspace/Users/<your-username>/apps/ehr-clinical-explorer --profile tko --overwrite
```

### 4. Add resources in the Apps UI

In the **tko** workspace:

1. **Apps** → **ehr-clinical-explorer** → **Configure** (or **Edit**).
2. Under **Resources**, add:
   - **Genie space**: key `genie-space`, select **build-con-mp** (in this workspace), **Can view**, **Can run**.
   - **SQL warehouse**: key `sql-warehouse`, select a warehouse in this workspace, **Can use**.
3. Save.

Both IDs are injected from resources (`valueFrom` in `app.yaml`). For local run, set `GENIE_SPACE_ID` and `DATABRICKS_WAREHOUSE_ID` in your environment before `streamlit run app.py`.

### 5. Deploy the app

```bash
databricks apps deploy ehr-clinical-explorer \
  --source-code-path /Workspace/Users/<your-username>/apps/ehr-clinical-explorer \
  --profile tko
```

### 6. Open the app

- In the **tko** workspace: **Apps** → **ehr-clinical-explorer** → **Open** (or use the URL from `databricks apps get ehr-clinical-explorer --profile tko`).
- **Ask Genie** tab: in-app chat using the Genie space; **Dashboard** tab: in-app metrics and charts from the same tables, plus an optional link to the full AI/BI dashboard when `DASHBOARD_EMBED_URL` is set.

### Redeploy after code changes

```bash
databricks workspace import-dir ./app /Workspace/Users/<your-username>/apps/ehr-clinical-explorer --profile tko --overwrite
databricks apps deploy ehr-clinical-explorer \
  --source-code-path /Workspace/Users/<your-username>/apps/ehr-clinical-explorer \
  --profile tko
```

### Check logs

```bash
databricks apps logs ehr-clinical-explorer --profile tko
```

Look for `Deployment successful` and `App started successfully`; any errors will appear in the log output.

## How Genie is used (no embedding)

- **In-app**: The **Ask Genie** tab uses the [Genie Conversation API](https://docs.databricks.com/genie/conversation-api.html): you type questions in the chat; the app calls `start_conversation` / `create_message` and displays Genie’s text and SQL in the same page. No iframe—the workspace does not need to allow embedding.
- **Full Genie UI**: Use **Open Genie in new tab** in the sidebar to open `https://<workspace>/genie/rooms/<space_id>` in a new tab for the full Genie experience (charts, suggested questions, etc.).
- **Dashboard**: The Dashboard tab shows **in-app** metrics and bar charts (patient count, diagnosis/stage/modality breakdowns) via the Statement Execution API. If `DASHBOARD_EMBED_URL` is set, a link at the bottom opens the full AI/BI dashboard in a new tab.

## Permissions

The app’s service principal needs:

- **Genie space**: Can view, Can run (via resource).
- **SQL warehouse**: Can use (via resource). Required for Dashboard data — add the `sql-warehouse` resource in Apps UI.
- **Data**: Grant the app's service principal **USE CATALOG** on `melissap`, **USE SCHEMA** on `melissap.melissa_pang`, and **SELECT** on the three tables (see below for how to find the principal).

### Finding the app's service principal

The app uses a **service principal** that Databricks creates for the app. To find it and grant data access:

1. **Open the app configuration**: **Apps** → **ehr-clinical-explorer** → **Configure** (or **Edit**).
2. **Open the Authorization step/tab**: In the configure flow, look for a step or tab named **Authorization**. The **service principal ID** (or "Application ID") is shown there — copy it. If you don't see it, try **Settings** → **Apps** → select **ehr-clinical-explorer** and look for an **Authorization** or **Access** section.
3. **Grant permissions in Unity Catalog**:
   - Go to **Data** (or **Catalog** in the sidebar) → select catalog **melissap** → **Permissions** (or right‑click → Permissions).
   - **Add** the principal: paste the service principal ID or search for the app name (e.g. `ehr-clinical-explorer`). If your UI lists "Service principals" under **Settings**, you can find the app's principal there by ID or name.
   - Grant: **USE CATALOG** on `melissap`, **USE SCHEMA** on `melissap.melissa_pang`, **SELECT** on `melissap.melissa_pang.ehr`, `melissap.melissa_pang.lung_cancer_images`, `melissap.melissa_pang.parsed_clinical_notes`.

Alternatively, a workspace admin can run SQL (e.g. in a notebook or Databricks SQL) to grant the principal by name, once you have the principal's name/ID from the Authorization tab.

## Dashboard not showing data?

If the Dashboard tab loads but metrics show "—" and charts show "Could not load", do both:

1. **Add the SQL warehouse resource**: **Apps** → **ehr-clinical-explorer** → **Configure** → **Resources** → add **SQL warehouse** with key `sql-warehouse`, select your warehouse, **Can use** → Save, then **Redeploy**.
2. **Grant the app's service principal access to the data** (see Permissions above). Without USE CATALOG / USE SCHEMA / SELECT on the three tables, the app cannot run the dashboard queries.
