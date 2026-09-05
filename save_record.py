import json
import os
from datetime import datetime

RECORDS_FILE = "patient_records_log.json"

def save_confirmed_record(patient_id, patient_name, diagnosis, prescription):
    record = {
        "timestamp": datetime.now().isoformat(),
        "patient_id": int(patient_id),
        "patient_name": patient_name,
        "diagnosis": diagnosis,
        "prescription": prescription
    }

    if os.path.exists(RECORDS_FILE):
        with open(RECORDS_FILE, "r") as f:
            records = json.load(f)
    else:
        records = []

    records.append(record)

    with open(RECORDS_FILE, "w") as f:
        json.dump(records, f, indent=2)

    return record