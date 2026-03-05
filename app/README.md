# EHR Clinical Explorer (Databricks App)

Streamlit app that embeds **Genie** (natural-language Q&A over your EHR data) and an optional **AI/BI dashboard**.

## Prerequisites

- **Notebooks 1–4** in this repo run: volume + Genie space **build-con-mp**, synthetic data, Delta tables (ehr, lung_cancer_images, parsed_clinical_notes), and tables registered in the Genie space.
- A **SQL warehouse** (for the app resource and for Genie/dashboard queries).

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

- Install the [Databricks CLI](https://docs.databricks.com/dev-tools/cli/index.html) and [configure](https://docs.databricks.com/dev-tools/cli/auth.html) it (e.g. `databricks configure --token` or profile in `~/.databrickscfg`).
- Use the same workspace where you created the Genie space **build-con-mp** and the SQL warehouse.

### 2. Create the app (once)

From the **project root** (parent of `app/`):

```bash
databricks apps create ehr-clinical-explorer
```

Or create the app from the **Databricks workspace**: **Apps** → **Create app** → enter name `ehr-clinical-explorer`.

### 3. Upload source code

Replace `<your-username>` with your workspace username (e.g. your email or `melissa.pang@databricks.com`):

```bash
# From project root (claude-playground/)
databricks workspace mkdirs /Workspace/Users/<your-username>/apps/ehr-clinical-explorer
databricks workspace import-dir ./app /Workspace/Users/<your-username>/apps/ehr-clinical-explorer
```

### 4. Add resources in the Apps UI

1. In the workspace, go to **Apps** → open **ehr-clinical-explorer** → **Configure** (or **Edit**).
2. Under **Resources**, click **Add resource**:
   - **Genie space**: key `genie-space`, select the space **build-con-mp**, permissions **Can view**, **Can run**.
   - **SQL warehouse**: key `sql-warehouse`, select the warehouse (e.g. id `e9b34f7a2e4b0561`), permission **Can use**.
3. Save.

### 5. Deploy the app

```bash
databricks apps deploy ehr-clinical-explorer \
  --source-code-path /Workspace/Users/<your-username>/apps/ehr-clinical-explorer
```

### 6. Open the app

- **Apps** → **ehr-clinical-explorer** → click **Open** (or use the URL from **databricks apps get ehr-clinical-explorer**).
- Use **Ask Genie** for the embedded Genie space; use **Dashboard** for the configured dashboard.

### Redeploy after code changes

```bash
databricks workspace delete /Workspace/Users/<your-username>/apps/ehr-clinical-explorer --recursive
databricks workspace import-dir ./app /Workspace/Users/<your-username>/apps/ehr-clinical-explorer
databricks apps deploy ehr-clinical-explorer \
  --source-code-path /Workspace/Users/<your-username>/apps/ehr-clinical-explorer
```

### Check logs

```bash
databricks apps logs ehr-clinical-explorer
```

Look for `Deployment successful` and `App started successfully`; any errors will appear in the log output.

## Iframe behavior

- **Genie**: The app embeds `https://<workspace>/genie/rooms/<space_id>`. If the embedded iframe does not load (e.g. cookie or embedding restrictions), use **Open Genie in new tab** in the sidebar.
- **Dashboard**: Only shown when `DASHBOARD_EMBED_URL` is set to a published AI/BI dashboard embed URL.

## Permissions

The app’s service principal needs:

- **Genie space**: Can view, Can run (via resource).
- **SQL warehouse**: Can use (via resource).
- **Data**: `USE CATALOG`, `USE SCHEMA`, and `SELECT` on `melissap.melissa_pang` (ehr, lung_cancer_images, parsed_clinical_notes) so Genie can run queries.
