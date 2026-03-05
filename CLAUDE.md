# claude-playground

Context for AI assistants working in this project.

## What this project is

Databricks-backed EHR (Electronic Health Records) demo: synthetic clinical data generation, Unity Catalog storage, document parsing, Delta tables with primary/foreign keys, and a Genie space for natural-language exploration. All data lives under catalog `melissap`, schema `melissa_pang`.

## Run order (notebooks 1 → 2 → 3 → 4)

1. **Notebook 1** — Create volume and Genie space **build-con-mp**.
2. **Notebook 2** — Generate synthetic data (100 PDFs, JSON, CSV) into the volume.
3. **Notebook 3** — Parse PDFs into `parsed_clinical_notes`, load CSV/JSON into **ehr** and **lung_cancer_images**, add PK/FK; optionally create the **unify_ehr_data** job.
4. **Notebook 4** — Add the three Delta tables to the Genie space **build-con-mp** so you can query them in AI/BI Genie.

## Project layout

| Path | Purpose |
|------|--------|
| `create_schema.py` | Ensures catalog `melissap` and schema `melissa_pang` exist. Uses DatabricksSession with profile `DEFAULT`. |
| `1.setup_volume_and_genie.ipynb` | Creates UC volume `melissap.melissa_pang.project_volume`, ensures `clinical_notes` subfolder, and Genie space **build-con-mp** (title). Uses Databricks SDK (`WorkspaceClient(profile="DEFAULT")`). Optional: set `WAREHOUSE_ID`; tables can be added later via notebook 4. |
| `2.generate_synthetic_clinical_data.ipynb` | Generates synthetic clinical data: 100 PDF clinical notes in `project_volume/clinical_notes/`, one JSON (`lung_cancer_images_metadata.json`) and one CSV (`ehr.csv`) in the volume root. 35 patients with shared `patient_id` (e.g. `PAT_001`). Uses Faker, fpdf2, pandas; uploads via `w.files.upload()` with `io.BytesIO()` for contents. |
| `3.unify_ehr_data.ipynb` | **unify_ehr_data** workflow: (1) reads PDFs from `project_volume/clinical_notes`, parses with `ai_parse_document`, writes to `parsed_clinical_notes` with structured fields (note_date, encounter, chief_complaint, assessment, plan, next_visit, etc.); (2) loads `ehr.csv` and `lung_cancer_images_metadata.json` into Delta tables **ehr** and **lung_cancer_images**; (3) adds PRIMARY KEY and FOREIGN KEY so the three tables join on `patient_id`; (4) optional cell to create/update the Databricks Job. Uses Spark (or Databricks Connect); avoid `spark.sparkContext` when using Spark Connect. |
| `4.add_tables_to_genie_space.ipynb` | Adds the three Delta tables (ehr, lung_cancer_images, parsed_clinical_notes) to the existing Genie space **build-con-mp**. Finds the space by title via `w.genie.list_spaces`, gets current config with `get_space(include_serialized_space=True)`, then `update_space` with `serialized_space` in **version 2** format: `data_sources.tables` as list of `{"identifier": "catalog.schema.table"}`. Run after notebooks 1 and 3. Uses only Databricks SDK (no Spark). |
| `DATABRICKS_REPO_SETUP.md` | How to mirror this project in the Databricks workspace with Repos (Git) so notebooks stay in sync and the **unify_ehr_data** job can run from the repo path. |
| `APP_PROPOSAL.md` | Proposal for the EHR Clinical Explorer app (Genie + dashboard). |
| `app/` | **EHR Clinical Explorer** Databricks app: Streamlit, Genie embed (iframe), optional dashboard embed. `app.yaml` uses resources `genie-space` and `sql-warehouse`. See `app/README.md` for deploy and resources. |

## Conventions

- **Databricks auth:** Scripts use `profile="DEFAULT"` (e.g. `WorkspaceClient(profile="DEFAULT")`, `DatabricksSession.builder.profile("DEFAULT")`). Align new code with this unless the user asks otherwise.
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
