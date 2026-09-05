import pandas as pd

def load_analytics_data():
    return pd.read_csv("healthcare_patient_analytics_seaborn.csv")

def recommend_treatment(department, age_group):
    df = load_analytics_data()

    # Filter similar cases: same department + age group
    similar = df[(df["department"] == department) & (df["age_group"] == age_group)]

    if similar.empty:
        # Fallback: same department only
        similar = df[df["department"] == department]

    if similar.empty:
        return None

    # Group by treatment_type, find average recovery_score and readmission_risk
    summary = similar.groupby("treatment_type").agg(
        avg_recovery_score=("recovery_score", "mean"),
        avg_readmission_risk=("readmission_risk", "mean"),
        case_count=("patient_id", "count")
    ).reset_index()

    # Best treatment = highest recovery score, lowest readmission risk
    summary["score"] = summary["avg_recovery_score"] - (summary["avg_readmission_risk"] * 100)
    summary = summary.sort_values("score", ascending=False)

    best = summary.iloc[0]
    return {
        "recommended_treatment": best["treatment_type"],
        "avg_recovery_score": round(best["avg_recovery_score"], 1),
        "avg_readmission_risk": round(best["avg_readmission_risk"], 2),
        "based_on_cases": int(best["case_count"]),
        "all_options": summary.to_dict("records")
    }
from sklearn.linear_model import LinearRegression
import numpy as np

def simulate_outcome_feedback(department, age_group, treatment_type):
    df = load_analytics_data()

    similar = df[(df["department"] == department) & (df["treatment_type"] == treatment_type)]
    if similar.empty:
        similar = df[df["treatment_type"] == treatment_type]
    if similar.empty:
        return None

    age_map = {"18-30": 24, "31-45": 38, "46-60": 53, "60+": 70}
    similar = similar.copy()
    similar["age_numeric"] = similar["age_group"].map(age_map)

    X = similar[["age_numeric", "length_of_stay_days", "treatment_cost"]].fillna(0)
    y = similar["recovery_score"]

    if len(X) < 5:
        return {
            "predicted_recovery": round(y.mean(), 1),
            "confidence_note": "Low sample size — using average"
        }

    model = LinearRegression()
    model.fit(X, y)

    avg_stay = similar["length_of_stay_days"].mean()
    avg_cost = similar["treatment_cost"].mean()
    query_age = age_map.get(age_group, 40)

    predicted = model.predict([[query_age, avg_stay, avg_cost]])[0]

    return {
        "predicted_recovery": round(predicted, 1),
        "confidence_note": f"Based on regression over {len(X)} similar cases"
    }