import os
import json
import time
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def get_diagnosis(patient_data, complaint, xray_image=None):
    prompt = f"""
    Patient data: {patient_data}
    Chief complaint: {complaint}
    Provide diagnosis suggestion with:
    - primary_diagnosis (condition, icd_10_code, confidence_score as decimal 0-1, reasoning)
    - differential_diagnoses (list of objects, EACH MUST include condition, icd_10_code, confidence_score as decimal 0-1, and reasoning — confidence_score is required for every item)
    - follow_up_tests (list)
    - clinical_notes (list)
    If an X-ray image is provided, incorporate visual findings into your reasoning.
    Respond ONLY with valid JSON, no markdown formatting, no code blocks.
    """

    contents = [prompt]
    if xray_image is not None:
        image_bytes = xray_image.read() if hasattr(xray_image, "read") else xray_image
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/png"))

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=contents
            )
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                return {"error": True, "error_type": "429", "message": error_str}
            elif "503" in error_str:
                return {"error": True, "error_type": "503", "message": error_str}
            if attempt < 2:
                time.sleep(3)
            else:
                return {"error": True, "error_type": "OTHER", "message": error_str}


def ask_followup(patient_data, diagnosis_context, chat_history, question):
    context_summary = f"""
    Patient: {patient_data}
    Diagnosed condition: {diagnosis_context.get('condition', 'N/A') if diagnosis_context else 'Not yet diagnosed'}
    Diagnosis reasoning: {diagnosis_context.get('reasoning', 'N/A') if diagnosis_context else 'N/A'}
    """
    history_text = "\n".join([f"{h['role']}: {h['text']}" for h in chat_history])
    prompt = f"""
    You are a clinical assistant helping a doctor with follow-up questions about a patient's diagnosis, treatment, or prescription.
    {context_summary}
    Conversation so far:
    {history_text}
    Doctor's question: {question}
    Answer concisely and clinically. If the question is outside the scope of this patient's case, say so.
    """
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt
            )
            return response.text
        except Exception as e:
            error_str = str(e)
            if "503" in error_str and attempt < 2:
                time.sleep(5)
                continue
            return f"⚠️ Error: {error_str}"