import pandas as pd
import time
from data import load_patients
from utils import get_diagnosis

eval_df = pd.read_csv("Datasets/evaluation_cases.csv")
patients_df = load_patients()

results = []

for _, row in eval_df.iterrows():
    patient = patients_df[patients_df["patient_id"] == row["patient_id"]].iloc[0]

    print(f"Testing patient {row['patient_id']} - {row['name']}...")

    try:
        ai_result = get_diagnosis(patient.to_dict(), row["chief_complaint_history"])
        ai_diagnosis = ai_result["primary_diagnosis"]["condition"]
    except Exception as e:
        ai_diagnosis = f"ERROR: {e}"

    # Simple match check: does ground truth keyword appear in AI diagnosis?
    gt = row["ground_truth_diagnosis"].lower()
    ai = ai_diagnosis.lower()
    match = any(word in ai for word in gt.split())

    results.append({
        "patient_id": row["patient_id"],
        "name": row["name"],
        "complaint": row["chief_complaint_history"],
        "ground_truth": row["ground_truth_diagnosis"],
        "ai_diagnosis": ai_diagnosis,
        "match": match
    })

    time.sleep(2)  # avoid rate limit issues

results_df = pd.DataFrame(results)
results_df.to_csv("Datasets/evaluation_results.csv", index=False)

accuracy = results_df["match"].mean() * 100
print(f"\n=== EVALUATION COMPLETE ===")
print(f"Accuracy: {accuracy:.1f}% ({results_df['match'].sum()}/{len(results_df)} matched)")
print(results_df[["name", "ground_truth", "ai_diagnosis", "match"]])