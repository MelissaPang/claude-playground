# claude-playground

Context for AI assistants working in this project.

## What this project is

Databricks-backed EHR (Electronic Health Records) demo: synthetic clinical data generation, Unity Catalog storage, document parsing, and a Genie space for exploration. All data lives under catalog `melissap`, schema `melissa_pang`.

## Project layout

| Path | Purpose |
|------|--------|
| `create_schema.py` | Ensures catalog `melissap` and schema `melissa_pang` exist. Uses DatabricksSession with profile `DEFAULT`. |
| `1.setup_volume_and_genie.ipynb` | Creates UC volume `melissap.melissa_pang.project_volume`, subfolder `clinical_notes`, and Genie space **build-con-mp**. Uses Databricks SDK (`WorkspaceClient(profile="DEFAULT")`). |
| `2.generate_synthetic_clinical_data.ipynb` | Generates synthetic clinical data: 100 PDF clinical notes (in volume `project_volume/clinical_notes/`), one JSON (lung cancer images metadata), one CSV (EHR). 35 patients with shared `patient_id` (e.g. `PAT_001`). Uses Faker, fpdf2, pandas; uploads via `w.files.upload()` with `io.BytesIO()` for contents. |
| `3.unify_ehr_data.ipynb` | **unify_ehr_data** workflow: reads PDFs from `project_volume/clinical_notes`, parses with `ai_parse_document`, writes to `melissap.melissa_pang.parsed_clinical_notes`. Last cell creates/updates a Databricks Job named `unify_ehr_data` that runs this notebook. Uses Spark (or Databricks Connect); avoid `spark.sparkContext` when using Spark Connect. |
| `DATABRICKS_REPO_SETUP.md` | How to mirror this project in the Databricks workspace with Repos (Git) so notebooks stay in sync and the job can run from the repo path. |

## Conventions

- **Databricks auth:** Scripts use `profile="DEFAULT"` (e.g. `WorkspaceClient(profile="DEFAULT")`, `DatabricksSession.builder.profile("DEFAULT")`). Align new code with this unless the user asks otherwise.
- **Catalog/schema:** Use `melissap` / `melissa_pang` for tables and volumes in this project.
- **Volume paths:** Base volume path is `/Volumes/melissap/melissa_pang/project_volume`; PDFs live under `.../project_volume/clinical_notes/`.
- **Faker:** Use `chance_of_getting_true` (not `chance_of_being_true`) for `fake.boolean()`.
- **SDK file upload:** Pass file-like contents (e.g. `io.BytesIO(bytes)`) to `w.files.upload()`, not raw `bytes`/`bytearray`, to avoid `seekable` errors.

## Key tables and outputs

- `melissap.melissa_pang.parsed_clinical_notes` — Parsed clinical note PDFs (path, patient_id, parsed variant, parsed_text, parsed_at).
- Volume `project_volume`: root holds `lung_cancer_images_metadata.json` and `ehr.csv`; `clinical_notes/` holds the 100 PDFs.

## Databricks Repos (mirror Cursor ↔ workspace)

To run the **unify_ehr_data** job in Databricks, the notebook must exist in the workspace. Use **Repos** to clone this project from Git; then push from Cursor and pull in Databricks to keep in sync. See **DATABRICKS_REPO_SETUP.md** for step-by-step instructions.

## Dependencies

- **Notebooks:** `faker`, `fpdf2`, `pandas`, `databricks-sdk` (and Spark/Databricks Connect for notebook 3).
- **Runtime:** `ai_parse_document` requires a Databricks cluster (or Databricks Connect to a cluster); it is not available in a local-only PySpark session.
