import pandas as pd

df = pd.read_csv("Datasets/synthetic_patients.csv")

ground_truth_map = {
    "Chest pain, shortness of breath": "Acute Coronary Syndrome",
    "Persistent cough, fever": "Community-Acquired Pneumonia",
    "Abdominal pain, nausea": "Acute Gastroenteritis",
    "Headache, dizziness": "Migraine",
    "Joint pain, swelling": "Osteoarthritis",
    "Fatigue, weight loss": "Hypothyroidism"
}

# Pick 3 patients per complaint type for a balanced 18-case evaluation set
sample = df.groupby("chief_complaint_history").head(3).reset_index(drop=True)
sample["ground_truth_diagnosis"] = sample["chief_complaint_history"].map(ground_truth_map)

eval_df = sample[["patient_id", "name", "chief_complaint_history", "ground_truth_diagnosis"]]
eval_df.to_csv("Datasets/evaluation_cases.csv", index=False)
print("Saved:", eval_df.shape)
print(eval_df)