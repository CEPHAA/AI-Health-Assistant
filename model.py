import random

def predict_disease(symptoms):
    """
    AI model to predict diseases based on symptoms
    In production, replace with actual ML model
    """
    symptom_list = [s.strip().lower() for s in symptoms.split(',')]
    
    # Disease database with symptoms and severity
    diseases = {
        "Common Cold": {
            "symptoms": ["fever", "cough", "runny nose", "sneezing", "sore throat"],
            "severity": "Mild",
            "advice": "Rest, stay hydrated, and take over-the-counter cold medicine."
        },
        "Influenza": {
            "symptoms": ["fever", "cough", "fatigue", "body ache", "headache", "chills"],
            "severity": "Moderate",
            "advice": "Get plenty of rest, stay hydrated, and consult a doctor if symptoms persist."
        },
        "COVID-19": {
            "symptoms": ["fever", "cough", "loss of taste", "loss of smell", "difficulty breathing", "fatigue"],
            "severity": "Severe",
            "advice": "Isolate immediately, get tested, and seek medical attention if breathing difficulties occur."
        },
        "Migraine": {
            "symptoms": ["headache", "nausea", "sensitivity to light", "vomiting"],
            "severity": "Moderate",
            "advice": "Rest in a dark room, stay hydrated, and take prescribed medication."
        },
        "Allergy": {
            "symptoms": ["sneezing", "runny nose", "itchy eyes", "rash", "congestion"],
            "severity": "Mild",
            "advice": "Avoid allergens and take antihistamines if needed."
        },
        "Gastroenteritis": {
            "symptoms": ["nausea", "vomiting", "diarrhea", "stomach pain", "fever"],
            "severity": "Moderate",
            "advice": "Stay hydrated, rest, and follow a bland diet."
        }
    }
    
    # Find best match
    best_match = None
    max_score = 0
    
    for disease, info in diseases.items():
        score = sum(1 for s in symptom_list if s in info["symptoms"])
        if score > max_score:
            max_score = score
            best_match = disease
    
    if max_score == 0:
        return {
            "disease": "Unknown",
            "severity": "Mild",
            "advice": "Please consult a healthcare professional for accurate diagnosis.",
            "confidence": 0
        }
    
    disease_info = diseases[best_match]
    confidence = (max_score / len(disease_info["symptoms"])) * 100
    
    return {
        "disease": best_match,
        "severity": disease_info["severity"],
        "advice": disease_info["advice"],
        "confidence": round(confidence, 2),
        "detected_symptoms": [s for s in symptom_list if any(s in ds for ds in disease_info["symptoms"])]
    }
