import json
import os
import streamlit as st
from collections import Counter

RECORDS_FILE = "patient_records_log.json"

def show_stats_dashboard():
    if not os.path.exists(RECORDS_FILE):
        st.info("No records saved yet. Confirm a diagnosis to see stats here.")
        return

    with open(RECORDS_FILE, "r") as f:
        records = json.load(f)

    if not records:
        st.info("No records saved yet.")
        return

    st.metric("Total Confirmed Records", len(records))

    unique_patients = len(set(r["patient_id"] for r in records))
    st.metric("Unique Patients Treated", unique_patients)

    diagnoses = [r["diagnosis"]["condition"] for r in records if r.get("diagnosis")]
    if diagnoses:
        st.subheader("Most Common Diagnoses")
        counts = Counter(diagnoses)
        for condition, count in counts.most_common(5):
            st.write(f"- {condition}: {count}")

    prescriptions = [r["prescription"] for r in records if r.get("prescription")]
    if prescriptions:
        st.subheader("Most Prescribed Medications")
        counts = Counter(prescriptions)
        for drug, count in counts.most_common(5):
            st.write(f"- {drug}: {count}")

    st.subheader("Recent Activity")
    for r in reversed(records[-5:]):
        st.caption(f"{r['timestamp']} — {r['patient_name']}: {r.get('prescription', 'N/A')}")
