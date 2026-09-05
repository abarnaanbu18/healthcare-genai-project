DRUG_INTERACTIONS = {
    "warfarin": ["aspirin", "nsaids", "ibuprofen"],
    "metformin": ["contrast dye"],
    "ace inhibitors": ["potassium supplements", "nsaids"],
    "insulin": ["corticosteroids", "beta blockers"],
    "ssri": ["maoi", "tramadol"],
    "statins": ["clarithromycin", "grapefruit"],
}

ALLERGY_KEYWORDS = {
    "penicillin": ["amoxicillin", "ampicillin", "penicillin"],
    "sulfa drugs": ["sulfamethoxazole", "bactrim"],
    "nsaids": ["ibuprofen", "naproxen", "aspirin"],
    "aspirin": ["aspirin"],
}

def check_prescription_safety(prescription, patient):
    warnings = []
    prescription_lower = prescription.lower()

    patient_allergy = str(patient.get('allergies', 'None')).lower()
    if patient_allergy != "none":
        for allergy_key, drug_list in ALLERGY_KEYWORDS.items():
            if allergy_key in patient_allergy:
                for drug in drug_list:
                    if drug in prescription_lower:
                        warnings.append({
                            "severity": "critical",
                            "message": f"Patient allergic to {allergy_key} — prescription contains {drug}"
                        })

    current_meds = str(patient.get('current_medications', 'None')).lower()
    if current_meds != "none":
        for drug, interacts_with in DRUG_INTERACTIONS.items():
            if drug in current_meds:
                for interacting_drug in interacts_with:
                    if interacting_drug in prescription_lower:
                        warnings.append({
                            "severity": "warning",
                            "message": f"{prescription} may interact with current medication ({drug})"
                        })

    return warnings