import pandas as pd
import random

random.seed(42)

first_names = ["Arun", "Priya", "Rajesh", "Divya", "Suresh", "Lakshmi", "Karthik", "Meena",
               "Vijay", "Anitha", "Prakash", "Kavya", "Senthil", "Deepa", "Manoj", "Sneha",
               "Ganesh", "Pooja", "Ravi", "Swathi"]
last_names = ["Kumar", "Sharma", "Nair", "Menon", "Babu", "Iyer", "Raj", "Devi",
              "Anand", "Rao", "Reddy", "Pillai", "Krishnan", "Varma", "Naidu"]

allergy_options = ["Penicillin", "Sulfa drugs", "NSAIDs", "None", "Latex", "Aspirin"]
medication_options = ["Metformin", "Amlodipine", "Atorvastatin", "None", "Losartan", "Insulin"]
complaint_options = [
    "Chest pain, shortness of breath",
    "Persistent cough, fever",
    "Abdominal pain, nausea",
    "Headache, dizziness",
    "Joint pain, swelling",
    "Fatigue, weight loss"
]
departments = ["General Medicine", "Orthopedics", "Pediatrics", "Neurology", "Cardiology"]

def get_age_group(age):
    if age <= 30:
        return "18-30"
    elif age <= 45:
        return "31-45"
    elif age <= 60:
        return "46-60"
    else:
        return "60+"

data = []
for i in range(1, 51):
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    age = random.randint(25, 80)
    data.append({
        "patient_id": i,
        "name": name,
        "age": age,
        "age_group": get_age_group(age),
        "gender": random.choice(["Male", "Female"]),
        "department": random.choice(departments),
        "blood_pressure": f"{random.randint(100,160)}/{random.randint(60,100)}",
        "heart_rate": random.randint(60, 110),
        "temperature_f": round(random.uniform(97.0, 101.5), 1),
        "oxygen_saturation": random.randint(90, 100),
        "allergies": random.choice(allergy_options),
        "current_medications": random.choice(medication_options),
        "chief_complaint_history": random.choice(complaint_options)
    })

df = pd.DataFrame(data)
df.to_csv("Datasets/synthetic_patients.csv", index=False)
print("Saved:", df.shape)
print(df.head())