"""
EHR Clinical Explorer – Streamlit app with embedded Genie and Dashboard.
Uses GENIE_SPACE_ID and optional DASHBOARD_EMBED_URL from app resources.
"""
import os
import streamlit as st
from databricks.sdk.core import Config

# Reference (for Apps UI binding and local run): Genie space name "build-con-mp", warehouse id e9b34f7a2e4b0561.
# Local run only: fallback warehouse id when DATABRICKS_WAREHOUSE_ID is not set (e.g. running outside Apps).
LOCAL_DEFAULT_WAREHOUSE_ID = "719412a7f456a882"
GENIE_SPACE_NAME = "build-con-mp"  # Used in UI messages; actual GENIE_SPACE_ID comes from app resource or env.
# Default dashboard URL (overridden by env DASHBOARD_EMBED_URL when set in app.yaml or Apps UI).
# Project workspace: https://fe-sandbox-serverless-sandbox-x7ar8s.cloud.databricks.com — set a dashboard URL from that workspace.
DEFAULT_DASHBOARD_URL = "https://fe-sandbox-serverless-sandbox-x7ar8s.cloud.databricks.com/dashboardsv3/01f118e23e341466b577e2f3d7097536/published/pages/5a2d82e0?o=7474649442851266"

# Must be first Streamlit command
st.set_page_config(
    page_title="EHR Clinical Explorer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Resolve workspace host and Genie space ID (from app resources when deployed; fallbacks for local run)
@st.cache_resource
def get_config():
    cfg = Config()
    host = (cfg.host or "").replace("https://", "").replace("http://", "").rstrip("/")
    space_id = os.getenv("GENIE_SPACE_ID", "").strip()
    # Fallback: look up Genie space by name when env not set (app needs genie list permission)
    if not space_id and host:
        try:
            from databricks.sdk import WorkspaceClient
            w = WorkspaceClient(config=cfg)
            response = w.genie.list_spaces(page_size=100)
            spaces = response.spaces or []
            match = next((s for s in spaces if (s.title or "").strip() == GENIE_SPACE_NAME), None)
            if match and getattr(match, "space_id", None):
                space_id = match.space_id
        except Exception:
            pass
    warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID", "").strip() or LOCAL_DEFAULT_WAREHOUSE_ID
    dashboard_url = (os.getenv("DASHBOARD_EMBED_URL") or "").strip() or (DEFAULT_DASHBOARD_URL or "").strip()
    return {"host": host, "space_id": space_id or "", "warehouse_id": warehouse_id, "dashboard_url": dashboard_url}

config = get_config()
GENIE_URL = (
    f"https://{config['host']}/genie/rooms/{config['space_id']}"
    if (config["host"] and config["space_id"]) else ""
)

# Sidebar
with st.sidebar:
    st.title("🩺 EHR Clinical Explorer")
    st.caption("Explore EHR, imaging, and clinical notes")
    st.divider()
    tab_choice = st.radio(
        "View",
        ["Ask Genie", "Dashboard"],
        index=0,
        label_visibility="collapsed",
    )
    if config["space_id"]:
        st.link_button("Open Genie in new tab", GENIE_URL, use_container_width=True)
    if config["dashboard_url"]:
        st.link_button("Open Dashboard in new tab", config["dashboard_url"], use_container_width=True)

# Main area: Genie (in-app chat via Conversation API) or Dashboard embed
if tab_choice == "Ask Genie":
    st.header("Ask Genie")
    st.caption(f"Natural language Q&A over EHR, lung cancer images, and parsed clinical notes ({GENIE_SPACE_NAME}).")
    if not config["space_id"]:
        st.warning(
            f"Genie space not configured. Add a **Genie space** resource ({GENIE_SPACE_NAME}) in the app settings and redeploy. "
            "For local run, set GENIE_SPACE_ID (from the Genie space URL) and ensure Databricks Config() resolves the workspace host."
        )
    else:
        # In-app chat using Genie Conversation API (no iframe)
        space_id = config["space_id"]
        if "genie_messages" not in st.session_state:
            st.session_state.genie_messages = []
        if "genie_conversation_id" not in st.session_state:
            st.session_state.genie_conversation_id = None

        for msg in st.session_state.genie_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("sql"):
                    st.code(msg["sql"], language="sql")

        if st.button("New conversation", type="secondary"):
            st.session_state.genie_conversation_id = None
            st.session_state.genie_messages = []
            st.rerun()
        if prompt := st.chat_input("Ask a question about EHR, imaging, or clinical notes..."):
            st.session_state.genie_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Genie is thinking..."):
                    try:
                        from databricks.sdk import WorkspaceClient
                        from datetime import timedelta
                        w = WorkspaceClient()
                        if st.session_state.genie_conversation_id is None:
                            msg = w.genie.start_conversation_and_wait(
                                space_id=space_id, content=prompt, timeout=timedelta(minutes=2)
                            )
                            st.session_state.genie_conversation_id = msg.conversation_id
                        else:
                            msg = w.genie.create_message_and_wait(
                                space_id=space_id,
                                conversation_id=st.session_state.genie_conversation_id,
                                content=prompt,
                                timeout=timedelta(minutes=2),
                            )
                        reply_parts = []
                        sql_part = None
                        for att in (msg.attachments or []):
                            if getattr(att, "text", None) and getattr(att.text, "content", None):
                                reply_parts.append(att.text.content)
                            if getattr(att, "query", None) and getattr(att.query, "query", None):
                                sql_part = att.query.query
                        reply = "\n\n".join(reply_parts) if reply_parts else "(No text response)"
                        if msg.error:
                            reply = f"Genie encountered an error: {msg.error}"
                        st.markdown(reply)
                        if sql_part:
                            st.code(sql_part, language="sql")
                        st.session_state.genie_messages.append({
                            "role": "assistant",
                            "content": reply,
                            "sql": sql_part,
                        })
                    except Exception as e:
                        err = str(e)
                        if "does not exist" in err or "Unable to get space" in err:
                            st.error(
                                "This Genie space was not found in this workspace. In **Apps** → **ehr-clinical-explorer** → "
                                "**Configure**, add a **Genie space** resource with key `genie-space`, select **build-con-mp**, "
                                "then **Redeploy**."
                            )
                        else:
                            st.error(f"Failed to call Genie: {err}")
                        st.session_state.genie_messages.append({
                            "role": "assistant",
                            "content": err,
                            "sql": None,
                        })

else:
    st.header("Dashboard")
    st.caption("Pre-built views on patients, imaging, and clinical notes (live from your data).")
    with st.expander("Dashboard not showing data? Configure app resources and permissions."):
        st.markdown("""
        1. **Add SQL warehouse resource**: Apps → ehr-clinical-explorer → Configure → **Resources** → add **SQL warehouse** (key `sql-warehouse`), select your warehouse, **Can use** → Save → **Redeploy**.
        2. **Grant the app's service principal access to the data**: Find the principal in the app's **Configure** → **Authorization** tab (copy the service principal ID). Then in **Data** → catalog **melissap** → **Permissions**, add that principal and grant **USE CATALOG**, **USE SCHEMA** on `melissap.melissa_pang`, and **SELECT** on the tables `ehr`, `lung_cancer_images`, `parsed_clinical_notes`. See the app README for step-by-step instructions.
        """)

    # In-app dashboard: run SQL via Statement Execution API and render in Streamlit (no iframe).
    CATALOG = "melissap"
    SCHEMA = "melissa_pang"
    warehouse_id = config["warehouse_id"]

    def run_sql(sql: str):
        """Execute SQL on the app warehouse; return (column_names, rows) or (None, error_msg)."""
        try:
            from databricks.sdk import WorkspaceClient
            from databricks.sdk.service.sql import Disposition
            w = WorkspaceClient()
            resp = w.statement_execution.execute_statement(
                statement=sql,
                warehouse_id=warehouse_id,
                catalog=CATALOG,
                schema=SCHEMA,
                disposition=Disposition.INLINE,
                wait_timeout="60s",
                row_limit=1000,
            )
            if not resp.status or getattr(resp.status, "state", None) != "SUCCEEDED":
                err = getattr(resp.status, "error", None) or "Statement did not succeed"
                return None, str(err)
            cols = []
            if resp.manifest and resp.manifest.schema and resp.manifest.schema.columns:
                cols = [c.name or f"col_{i}" for i, c in enumerate(resp.manifest.schema.columns)]
            rows = list(resp.result.data_array) if (resp.result and resp.result.data_array) else []
            # Fetch additional chunks if any
            stmt_id = resp.statement_id
            chunk = resp.result
            while chunk and getattr(chunk, "next_chunk_index", None) is not None:
                next_idx = chunk.next_chunk_index
                chunk = w.statement_execution.get_statement_result_chunk_n(stmt_id, next_idx)
                if chunk and chunk.data_array:
                    rows.extend(chunk.data_array)
            return cols, rows
        except Exception as e:
            return None, str(e)

    if not warehouse_id:
        st.warning("No SQL warehouse configured. Set **DATABRICKS_WAREHOUSE_ID** (or bind a sql-warehouse resource) to show the dashboard.")
    else:
        with st.spinner("Loading dashboard…"):
            # Metrics row
            c1, c2, c3 = st.columns(3)
            with c1:
                cols, rows = run_sql("SELECT COUNT(*) AS patient_count FROM melissap.melissa_pang.ehr")
                if cols is not None and rows and len(rows) > 0:
                    st.metric("Patients", rows[0][0])
                else:
                    st.metric("Patients", "—")
            with c2:
                cols, rows = run_sql("SELECT COUNT(*) AS image_count FROM melissap.melissa_pang.lung_cancer_images")
                if cols is not None and rows and len(rows) > 0:
                    st.metric("Imaging studies", rows[0][0])
                else:
                    st.metric("Imaging studies", "—")
            with c3:
                cols, rows = run_sql("SELECT COUNT(*) AS note_count FROM melissap.melissa_pang.parsed_clinical_notes")
                if cols is not None and rows and len(rows) > 0:
                    st.metric("Clinical notes", rows[0][0])
                else:
                    st.metric("Clinical notes", "—")

            st.subheader("Diagnosis breakdown")
            cols, rows = run_sql(
                "SELECT diagnosis AS diagnosis, COUNT(*) AS count FROM melissap.melissa_pang.ehr GROUP BY diagnosis ORDER BY count DESC LIMIT 20"
            )
            if cols is not None and rows is not None:
                import pandas as pd
                df = pd.DataFrame(rows, columns=cols or [f"col_{i}" for i in range(len(rows[0]) if rows else 0)])
                if not df.empty and df.shape[1] >= 2:
                    st.bar_chart(df.set_index(df.columns[0]))
                else:
                    st.dataframe(df, use_container_width=True)
            else:
                st.caption(f"Could not load: {rows}")

            st.subheader("Stage breakdown")
            cols, rows = run_sql(
                "SELECT stage AS stage, COUNT(*) AS count FROM melissap.melissa_pang.ehr GROUP BY stage ORDER BY count DESC LIMIT 20"
            )
            if cols is not None and rows is not None:
                import pandas as pd
                df = pd.DataFrame(rows, columns=cols or [f"col_{i}" for i in range(len(rows[0]) if rows else 0)])
                if not df.empty and df.shape[1] >= 2:
                    st.bar_chart(df.set_index(df.columns[0]))
                else:
                    st.dataframe(df, use_container_width=True)
            else:
                st.caption(f"Could not load: {rows}")

            st.subheader("Images by modality")
            cols, rows = run_sql(
                "SELECT modality AS modality, COUNT(*) AS count FROM melissap.melissa_pang.lung_cancer_images GROUP BY modality ORDER BY count DESC LIMIT 20"
            )
            if cols is not None and rows is not None:
                import pandas as pd
                df = pd.DataFrame(rows, columns=cols or [f"col_{i}" for i in range(len(rows[0]) if rows else 0)])
                if not df.empty and df.shape[1] >= 2:
                    st.bar_chart(df.set_index(df.columns[0]))
                else:
                    st.dataframe(df, use_container_width=True)
            else:
                st.caption(f"Could not load: {rows}")

        if config["dashboard_url"]:
            st.divider()
            st.caption("For the full Databricks AI/BI dashboard (charts, filters), open it in a new tab.")
            st.link_button("Open full dashboard in new tab", config["dashboard_url"], use_container_width=True)
