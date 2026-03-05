# Mirror This Project in Databricks with Repos

Use **Databricks Repos** so the same code lives in Cursor and in the Databricks workspace. Push from Cursor → Git → pull in Databricks; then jobs can run the notebooks from the repo path.

**Note:** The **EHR Clinical Explorer** app (`app/`) is deployed separately via **Databricks Apps** (upload + deploy from CLI or UI). See **`app/README.md`** for app deployment. Repos are used for the notebooks and the **unify_ehr_data** job, not for the app runtime.

---

## 1. Push this project to a Git remote

You need a Git repo that contains **only** the `claude-playground` project (not your whole home folder) so Databricks can clone it and see the notebooks at the root.

### Step 1a: Create a new repo on GitHub (or GitLab / Bitbucket)

1. Go to [GitHub](https://github.com/MelissaPang) (or your host).
2. Create a new repository, e.g. **claude-playground**.
3. Do **not** initialize with a README (you already have files).
4. Copy the repo URL, e.g. `https://github.com/YOUR_USERNAME/claude-playground.git`.

### Step 1b: Make `claude-playground` a Git repo and push

Open a terminal in the **claude-playground** folder (your Cursor project root):

```bash
cd /Users/melissa.pang/claude-playground
```

**If this folder is not yet a Git repo** (no `.git` here — your `.git` might be in a parent folder):

```bash
git init
git add .
git commit -m "Initial commit: EHR demo notebooks and setup"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/claude-playground.git
git push -u origin main
```

Replace `YOUR_USERNAME` and the URL with your actual repo URL. Use `git remote add origin <url>` for GitLab/Bitbucket/Azure Repos the same way.

**If you already ran `git remote add origin` with the placeholder URL**, fix it with:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/claude-playground.git
```
(Replace `YOUR_USERNAME` with your GitHub username, then run `git push -u origin main`.)

**If this folder is already its own Git repo** and you only need to add the remote and push:

```bash
git remote add origin https://github.com/YOUR_USERNAME/claude-playground.git
git add .
git commit -m "Initial commit"   # if you have uncommitted changes
git branch -M main
git push -u origin main
```

**If your Git repo is the parent folder** (e.g. your home) and you want Databricks to see only `claude-playground`:

- Easiest: make `claude-playground` its own repo as in “If this folder is not yet a Git repo” above (run `git init` inside `claude-playground`). Then you have two repos: the big one at home and this small one for Databricks.
- Or create a new GitHub repo that only contains the contents of `claude-playground` (e.g. copy the folder elsewhere, `git init`, add, commit, add remote, push).

The project root has a `.gitignore` so `.venv`, `__pycache__`, and `.ipynb_checkpoints` are not pushed.

---

## 2. Create a Repo in the Databricks workspace

1. In Databricks: go to **Repos** (left sidebar or **Workspace → Repos**).
2. Click **Add Repo** (or **Create repo**).
3. Choose **Clone from URL** (or connect your Git provider first under **Settings → Git integration**).
4. **Git repository URL:** your repo URL, e.g. `https://github.com/MelissaPang/claude-playground.git`.
5. **Repo name:** e.g. `claude-playground` (can match the project name).
6. **Path (optional):** leave default so the repo is at `/Repos/<your-user>/claude-playground`.
7. Create the repo. Databricks will clone the repo; your notebooks (e.g. `3.unify_ehr_data.ipynb`) will appear under that path.

## 3. Get the notebook path in the workspace

After the repo is created:

- In the repo, open **3.unify_ehr_data.ipynb**.
- Copy its path from the breadcrumb at the top (e.g. **File → Copy path**). It will look like:
  - `/Workspace/Repos/<your-email>/claude-playground/3.unify_ehr_data`
- Do **not** include the `.ipynb` extension in the path when using it in the job.

## 4. Create the job in the notebook

1. In **3.unify_ehr_data.ipynb** (in Cursor or in Databricks), set:
   ```python
   NOTEBOOK_IN_WORKSPACE_PATH = "/Workspace/Repos/<your-email>/claude-playground/3.unify_ehr_data"
   ```
   Use the path you copied (no `.ipynb`).
2. Run the last cell of the notebook. It will create or update the **unify_ehr_data** job that runs this notebook from the repo.

## 5. Keep Cursor and Databricks in sync

- **From Cursor:** commit and push to your Git remote:
  ```bash
  git add .
  git commit -m "Your message"
  git push
  ```
- **In Databricks:** open the repo and click **Pull** (or use the refresh/sync control) to get the latest changes.

After you pull, any job that runs the notebook will use the updated version. No need to re-create the job when you change the notebook; only the repo content changes.

## Optional: Git provider integration

In **Settings → Git integration** you can connect GitHub (or another provider). That allows:

- Creating repos by selecting a repo from the provider.
- Using the same credentials for pull/push from Databricks if you edit in both places.

For a Cursor-only workflow, connecting the provider and using **Clone from URL** plus manual **Pull** after you push from Cursor is enough.
