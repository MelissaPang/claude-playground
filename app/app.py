"""
EHR Clinical Explorer – Streamlit app with embedded Genie and Dashboard.
Uses GENIE_SPACE_ID and optional DASHBOARD_EMBED_URL from app resources.
"""
import os
import streamlit as st
from databricks.sdk.core import Config

# Reference (for Apps UI binding and local run): Genie space name "build-con-mp", warehouse id e9b34f7a2e4b0561.
# Local run only: fallback warehouse id when DATABRICKS_WAREHOUSE_ID is not set (e.g. running outside Apps).
LOCAL_DEFAULT_WAREHOUSE_ID = "e9b34f7a2e4b0561"
GENIE_SPACE_NAME = "build-con-mp"  # Used in UI messages; actual GENIE_SPACE_ID comes from app resource or env.
# Default dashboard URL (overridden by env DASHBOARD_EMBED_URL when set in app.yaml or Apps UI).
DEFAULT_DASHBOARD_URL = "https://e2-demo-field-eng.cloud.databricks.com/sql/dashboardsv3/01f118ce98d61261aa6e5e6afe3086fb/pages/0920a246?o=1444828305810485"

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
    warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID", "").strip() or LOCAL_DEFAULT_WAREHOUSE_ID
    dashboard_url = (os.getenv("DASHBOARD_EMBED_URL") or "").strip() or DEFAULT_DASHBOARD_URL
    return {"host": host, "space_id": space_id, "warehouse_id": warehouse_id, "dashboard_url": dashboard_url}

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

# Main area: Genie embed or Dashboard embed
if tab_choice == "Ask Genie":
    st.header("Ask Genie")
    st.caption(f"Natural language Q&A over EHR, lung cancer images, and parsed clinical notes ({GENIE_SPACE_NAME}).")
    if not GENIE_URL:
        st.warning(
            f"Genie space not configured. Add a **Genie space** resource ({GENIE_SPACE_NAME}) in the app settings and redeploy. "
            "For local run, set GENIE_SPACE_ID (from the Genie space URL) and ensure Databricks Config() resolves the workspace host."
        )
    else:
        # Embed Genie: workspace URL for the space (user must be authenticated in same workspace)
        st.components.v1.iframe(
            src=GENIE_URL,
            height=700,
            scrolling=True,
        )

else:
    st.header("Dashboard")
    st.caption("Pre-built views on patients, imaging, and clinical notes.")
    if not config["dashboard_url"]:
        st.info(
            "No dashboard URL set. Create and publish an AI/BI dashboard on `ehr`, `lung_cancer_images`, and `parsed_clinical_notes`, "
            "then set **DASHBOARD_EMBED_URL** in the app environment (or add a dashboard resource) and redeploy."
        )
    else:
        st.components.v1.iframe(
            src=config["dashboard_url"],
            height=700,
            scrolling=True,
        )
