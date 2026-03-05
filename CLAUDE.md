# claude-playground

Context for AI assistants working in this project.

## What this project is

Databricks-backed EHR (Electronic Health Records) demo: synthetic clinical data generation, Unity Catalog storage, document parsing, Delta tables with primary/foreign keys, a Genie space for natural-language exploration, and a **Databricks App** (EHR Clinical Explorer) that provides in-app Genie chat and an in-app dashboard over the same data. All data lives under catalog `melissap`, schema `melissa_pang`.

## Run order (notebooks 1 → 2 → 3 → 4)

1. **Notebook 1** — Create volume and Genie space **build-con-mp**.
2. **Notebook 2** — Generate synthetic data (100 PDFs, JSON, CSV) into the volume.
3. **Notebook 3** — Parse PDFs into `parsed_clinical_notes`, load CSV/JSON into **ehr** and **lung_cancer_images**, add PK/FK; optionally create the **unify_ehr_data** job.
4. **Notebook 4** — Add the three Delta tables to the Genie space **build-con-mp** so you can query them in AI/BI Genie.

## Project layout

| Path | Purpose |
|------|--------|
| `WORKSPACE.md` | Documents project workspace (fe-sandbox-serverless-sandbox-x7ar8s.cloud.databricks.com) and how to configure `DEFAULT` profile. |
| `.databrickscfg.example` | Example `~/.databrickscfg` with project workspace host; copy and add token. |
| `create_schema.py` | Ensures catalog `melissap` and schema `melissa_pang` exist. Uses `WorkspaceClient(profile="tko")`. Run: `.venv/bin/python create_schema.py`. |
| `1.setup_volume_and_genie.ipynb` | Creates UC volume `melissap.melissa_pang.project_volume`, ensures `clinical_notes` subfolder, and Genie space **build-con-mp** (title). Uses Databricks SDK (`WorkspaceClient` with profile). Optional: set `WAREHOUSE_ID`; tables can be added later via notebook 4. |
| `2.generate_synthetic_clinical_data.ipynb` | Generates synthetic clinical data: 100 PDF clinical notes in `project_volume/clinical_notes/`, one JSON (`lung_cancer_images_metadata.json`) and one CSV (`ehr.csv`) in the volume root. 35 patients with shared `patient_id` (e.g. `PAT_001`). Uses Faker, fpdf2, pandas; uploads via `w.files.upload()` with `io.BytesIO()` for contents. |
| `3.unify_ehr_data.ipynb` | **unify_ehr_data** workflow: (1) reads PDFs from `project_volume/clinical_notes`, parses with `ai_parse_document`, writes to `parsed_clinical_notes` with structured fields (note_date, encounter, chief_complaint, assessment, plan, next_visit, etc.); (2) loads `ehr.csv` and `lung_cancer_images_metadata.json` into Delta tables **ehr** and **lung_cancer_images**; (3) adds PRIMARY KEY and FOREIGN KEY so the three tables join on `patient_id`; (4) optional cell to create/update the Databricks Job. Uses Spark (or Databricks Connect); avoid `spark.sparkContext` when using Spark Connect. |
| `4.add_tables_to_genie_space.ipynb` | Adds the three Delta tables (ehr, lung_cancer_images, parsed_clinical_notes) to the existing Genie space **build-con-mp**. Finds the space by title via `w.genie.list_spaces`, gets current config with `get_space(include_serialized_space=True)`, then `update_space` with `serialized_space` in **version 2** format: `data_sources.tables` as list of `{"identifier": "catalog.schema.table"}`. Run after notebooks 1 and 3. Uses only Databricks SDK (no Spark). |
| `DATABRICKS_REPO_SETUP.md` | How to mirror this project in the Databricks workspace with Repos (Git) so notebooks stay in sync and the **unify_ehr_data** job can run from the repo path. |
| `APP_PROPOSAL.md` | Proposal for the EHR Clinical Explorer app (Genie + dashboard). |
| `app/` | **EHR Clinical Explorer** Databricks app: Streamlit with two tabs. (1) **Ask Genie**: in-app chat via Genie Conversation API (no iframe); "New conversation" and "Open Genie in new tab" in sidebar. (2) **Dashboard**: in-app metrics and bar charts (patient/image/note counts, diagnosis/stage/modality breakdowns) via Statement Execution API; optional link to full AI/BI dashboard. `app.yaml` uses `valueFrom` for `genie-space` and `sql-warehouse`. App service principal needs data permissions for Dashboard. See `app/README.md` for deploy and permissions. |

## Conventions

- **Workspace:** **https://fe-sandbox-serverless-sandbox-x7ar8s.cloud.databricks.com** — Configure `DEFAULT` in `~/.databrickscfg` or set `DATABRICKS_HOST` / `DATABRICKS_TOKEN`. See `WORKSPACE.md` and `.databrickscfg.example`.
- **Databricks auth:** Notebooks and scripts use `profile="tko"` for the project workspace (see WORKSPACE.md). App deployment uses `--profile tko`. The app itself uses `Config()` and injected credentials (no profile in app code).
- **Catalog/schema:** Use `melissap` / `melissa_pang` for tables and volumes in this project.
- **Volume paths:** Base volume path is `/Volumes/melissap/melissa_pang/project_volume`; PDFs live under `.../project_volume/clinical_notes/`.
- **Faker:** Use `chance_of_getting_true` (not `chance_of_being_true`) for `fake.boolean()`.
- **SDK file upload:** Pass file-like contents (e.g. `io.BytesIO(bytes)`) to `w.files.upload()`, not raw `bytes`/`bytearray`, to avoid `seekable` errors.

## Key tables and outputs

- **ehr** (`melissap.melissa_pang.ehr`) — One row per patient from `ehr.csv`; PRIMARY KEY `patient_id`. Loaded in notebook 3.
- **lung_cancer_images** (`melissap.melissa_pang.lung_cancer_images`) — One row per image from `lung_cancer_images_metadata.json`; PRIMARY KEY `image_id`, FOREIGN KEY `patient_id` → ehr. Loaded in notebook 3.
- **parsed_clinical_notes** (`melissap.melissa_pang.parsed_clinical_notes`) — Parsed clinical note PDFs: path, patient_id, parsed, parsed_text, parsed_at, plus structured fields (note_patient_id, note_date, encounter, chief_complaint, assessment, plan, next_visit). PRIMARY KEY `path`, FOREIGN KEY `patient_id` → ehr. Populated and constrained in notebook 3.
- All three tables join on `patient_id` and are registered in the Genie space **build-con-mp** by notebook 4 for natural-language SQL in AI/BI Genie.
- **Volume** `project_volume`: root holds `ehr.csv` and `lung_cancer_images_metadata.json`; subfolder `clinical_notes/` holds the 100 PDFs.

## Databricks Repos (mirror Cursor ↔ workspace)

To run the **unify_ehr_data** job in Databricks, the notebook must exist in the workspace. Use **Repos** to clone this project from Git; then push from Cursor and pull in Databricks to keep in sync. See **DATABRICKS_REPO_SETUP.md** for step-by-step instructions.

## Dependencies

- **Notebooks 1, 4:** `databricks-sdk` only.
- **Notebook 2:** `faker`, `fpdf2`, `pandas`, `databricks-sdk`.
- **Notebook 3:** Spark or Databricks Connect, plus `databricks-sdk` for the job-creation cell. `ai_parse_document` requires a Databricks cluster (or Databricks Connect); not available in local-only PySpark.
