"""
AI Media Analysis - Streamlit UI
Version: Alpha 0.6.0 - Quick Fix
"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

# Page config
st.set_page_config(
    page_title="AI Media Analysis",
    page_icon="🎥",
    layout="wide"
)

# API Configuration - FIXED HOSTS
API_HOSTS = {
    "job_manager": "http://ai_job_manager:8000",  # Fixed: ai_job_manager statt job_manager_api
    "control": "http://ai_control:8000",
    "person_dossier": "http://ai_person_dossier:8000",
    "video_context": "http://ai_video_context_analyzer:8000",
    "clothing": "http://ai_clothing_analyzer:8000",
    "uc001": "http://ai_uc001_job_manager:8012"
}

def check_service_health(service_name: str) -> bool:
    """Check if a service is healthy."""
    try:
        host = API_HOSTS.get(service_name)
        if not host:
            return False
        response = requests.get(f"{host}/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def get_service_status() -> Dict[str, bool]:
    """Get status of all services."""
    return {name: check_service_health(name) for name in API_HOSTS.keys()}

def main():
    st.title("🎥 AI Media Analysis System")
    st.caption("Alpha 0.6.0 - Quick Fix UI")

    # Service Status Dashboard
    st.header("📊 Service Status")

    status = get_service_status()
    cols = st.columns(len(status))

    for i, (service, healthy) in enumerate(status.items()):
        with cols[i]:
            emoji = "✅" if healthy else "❌"
            color = "green" if healthy else "red"
            st.metric(
                label=service.replace("_", " ").title(),
                value=emoji,
                delta="Healthy" if healthy else "Unhealthy"
            )

    # UC-001 Dashboard
    st.header("🔬 UC-001 Enhanced Manual Analysis")

    if status.get("uc001", False):
        try:
            # Get UC-001 job status
            response = requests.get(f"{API_HOSTS['uc001']}/uc001/jobs", timeout=5)
            if response.status_code == 200:
                jobs = response.json()
                if jobs:
                    df = pd.DataFrame(jobs)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No UC-001 jobs found")
            else:
                st.warning("UC-001 API not responding correctly")
        except Exception as e:
            st.error(f"UC-001 connection error: {str(e)}")
    else:
        st.warning("UC-001 service not available")

    # File Upload (Basic)
    st.header("📁 File Upload")

    uploaded_file = st.file_uploader(
        "Upload media file",
        type=['mp4', 'avi', 'mov', 'jpg', 'jpeg', 'png']
    )

    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")

        if st.button("Start Analysis"):
            try:
                # Create basic job
                job_data = {
                    "filename": uploaded_file.name,
                    "file_type": uploaded_file.type,
                    "timestamp": datetime.now().isoformat(),
                    "priority": "normal"
                }

                # Try to submit to UC-001 if available
                if status.get("uc001", False):
                    response = requests.post(
                        f"{API_HOSTS['uc001']}/uc001/analyze/upload",
                        json=job_data,
                        timeout=10
                    )
                    if response.status_code == 200:
                        st.success("Analysis job created successfully!")
                        st.json(response.json())
                    else:
                        st.error(f"Job creation failed: {response.status_code}")
                else:
                    st.warning("UC-001 service not available - file uploaded but analysis not started")

            except Exception as e:
                st.error(f"Error creating job: {str(e)}")

    # System Information
    with st.expander("🔧 System Information"):
        st.subheader("API Endpoints")
        for name, host in API_HOSTS.items():
            st.code(f"{name}: {host}")

        st.subheader("Health Check Results")
        st.json(status)

if __name__ == "__main__":
    main()
