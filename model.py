"""
AI Health Prediction Model - 23 Diseases with Accurate Symptoms
Complete Disease Database for Symptom Checking
"""

import re
import random

class HealthModel:
    """AI Model for symptom analysis with 23 diseases"""
    
    def __init__(self):
        self.diseases = {
            # 1. RESPIRATORY DISEASES
            "Common Cold": {
                "symptoms": ["fever", "cough", "runny nose", "sneezing", "sore throat", "congestion", "mild fatigue", "watery eyes"],
                "severity": "Mild",
                "advice": "Rest, stay hydrated, use honey for cough. Most symptoms resolve in 7-10 days.",
                "treatment": "Over-the-counter cold medicine, rest, fluids, saline nasal spray",
                "duration": "7-10 days",
                "contagious": "Yes - first 3 days"
            },
            "Influenza (Flu)": {
                "symptoms": ["high fever", "cough", "severe fatigue", "body ache", "headache", "chills", "sore throat", "weakness", "loss of appetite"],
                "severity": "Moderate to Severe",
                "advice": "Get plenty of rest, stay hydrated, monitor fever. Seek medical care if symptoms worsen.",
                "treatment": "Antiviral medication (within 48 hours), rest, fluids, fever reducers",
                "duration": "5-7 days",
                "contagious": "Yes - 1 day before symptoms to 5-7 days after"
            },
            "COVID-19": {
                "symptoms": ["fever", "cough", "fatigue", "loss of taste", "loss of smell", "difficulty breathing", "sore throat", "headache", "body ache", "congestion"],
                "severity": "Mild to Severe",
                "advice": "⚠️ ISOLATE IMMEDIATELY. Get tested. Seek emergency care if breathing difficulties occur.",
                "treatment": "Isolation, rest, fever reducers, oxygen therapy if needed",
                "duration": "10-14 days",
                "contagious": "Yes - 2 days before symptoms to 10 days after"
            },
            "Bronchitis": {
                "symptoms": ["persistent cough", "mucus production", "fatigue", "chest discomfort", "shortness of breath", "wheezing", "mild fever", "chills"],
                "severity": "Moderate",
                "advice": "Rest, stay hydrated, use humidifier. Seek care if cough persists beyond 3 weeks.",
                "treatment": "Rest, fluids, humidifier, cough medicine, possible antibiotics",
                "duration": "2-3 weeks",
                "contagious": "Varies - usually not contagious"
            },
            "Pneumonia": {
                "symptoms": ["high fever", "productive cough", "difficulty breathing", "chest pain", "fatigue", "chills", "sweating", "confusion", "nausea"],
                "severity": "Severe",
                "advice": "⚠️ URGENT: Seek immediate medical attention. Pneumonia requires professional medical care.",
                "treatment": "Antibiotics (if bacterial), rest, fluids, hospitalization if severe",
                "duration": "2-4 weeks",
                "contagious": "Yes - can be contagious"
            },
            
            # 2. HEAD & NEUROLOGICAL DISORDERS
            "Migraine": {
                "symptoms": ["severe headache", "nausea", "vomiting", "sensitivity to light", "sensitivity to sound", "aura", "throbbing pain", "dizziness", "vision changes"],
                "severity": "Moderate to Severe",
                "advice": "Rest in dark, quiet room. Apply cold compress. Avoid triggers like bright lights and loud noises.",
                "treatment": "Dark room, cold compress, pain relievers, prescription migraine medication",
                "duration": "4-72 hours",
                "contagious": "No"
            },
            "Tension Headache": {
                "symptoms": ["mild to moderate headache", "pressure around forehead", "tightness in neck", "scalp tenderness", "difficulty sleeping", "fatigue"],
                "severity": "Mild to Moderate",
                "advice": "Apply warm compress, practice relaxation techniques, maintain good posture.",
                "treatment": "Over-the-counter pain relievers, rest, stress management",
                "duration": "30 minutes to several days",
                "contagious": "No"
            },
            "Sinusitis": {
                "symptoms": ["facial pain", "pressure around eyes", "nasal congestion", "headache", "thick nasal discharge", "cough", "tooth pain", "fatigue", "fever"],
                "severity": "Mild to Moderate",
                "advice": "Use saline nasal spray, apply warm compresses, stay hydrated, use humidifier.",
                "treatment": "Nasal irrigation, decongestants, rest, warm compresses",
                "duration": "10-14 days",
                "contagious": "Usually not contagious"
            },
            
            # 3. ALLERGIC & SKIN CONDITIONS
            "Allergic Rhinitis": {
                "symptoms": ["sneezing", "runny nose", "itchy eyes", "watery eyes", "nasal congestion", "itchy throat", "cough", "fatigue", "dark circles under eyes"],
                "severity": "Mild to Moderate",
                "advice": "Avoid allergens, take antihistamines, use air purifier, keep windows closed during high pollen counts.",
                "treatment": "Antihistamines, nasal sprays, allergy shots, avoid triggers",
                "duration": "Varies with exposure",
                "contagious": "No"
            },
            "Urticaria (Hives)": {
                "symptoms": ["raised red welts", "itching", "swelling", "burning sensation", "wheals that change shape", "symptoms worsen with heat"],
                "severity": "Mild to Moderate",
                "advice": "Apply cold compress, avoid triggers, take antihistamines. Seek care if throat swelling occurs.",
                "treatment": "Antihistamines, corticosteroids, avoid allergens",
                "duration": "Few hours to several weeks",
                "contagious": "No"
            },
            "Eczema (Dermatitis)": {
                "symptoms": ["dry skin", "intense itching", "red patches", "cracked skin", "thickened skin", "small bumps", "raw sensitive skin"],
                "severity": "Mild to Moderate",
                "advice": "Moisturize regularly, avoid triggers, use gentle soaps, avoid scratching.",
                "treatment": "Moisturizers, topical corticosteroids, antihistamines",
                "duration": "Chronic condition",
                "contagious": "No"
            },
            
            # 4. GASTROINTESTINAL DISORDERS
            "Gastroenteritis (Stomach Flu)": {
                "symptoms": ["nausea", "vomiting", "diarrhea", "stomach pain", "cramps", "low-grade fever", "headache", "muscle aches", "loss of appetite"],
                "severity": "Mild to Moderate",
                "advice": "Stay hydrated with clear fluids. Follow BRAT diet (Bananas, Rice, Applesauce, Toast).",
                "treatment": "Rest, hydration, electrolyte replacement, bland diet",
                "duration": "1-3 days",
                "contagious": "Yes - highly contagious"
            },
            "Gastritis": {
                "symptoms": ["burning stomach pain", "nausea", "indigestion", "bloating", "loss of appetite", "belching", "feeling full quickly"],
                "severity": "Mild to Moderate",
                "advice": "Avoid spicy foods, alcohol, and NSAIDs. Eat smaller, frequent meals.",
                "treatment": "Antacids, proton pump inhibitors, diet changes",
                "duration": "Acute or chronic",
                "contagious": "No"
            },
            "Food Poisoning": {
                "symptoms": ["nausea", "vomiting", "diarrhea", "stomach cramps", "fever", "headache", "weakness", "blood in stool"],
                "severity": "Mild to Severe",
                "advice": "Stay hydrated, rest, avoid solid foods until symptoms improve. Seek care if severe.",
                "treatment": "Hydration, rest, electrolytes, medical care if severe",
                "duration": "1-7 days",
                "contagious": "Sometimes"
            },
            
            # 5. EAR, NOSE & THROAT
            "Strep Throat": {
                "symptoms": ["sudden sore throat", "painful swallowing", "fever", "swollen lymph nodes", "white patches on tonsils", "headache", "nausea", "red spots on roof of mouth"],
                "severity": "Moderate",
                "advice": "See a doctor for antibiotics. Rest and warm salt water gargles.",
                "treatment": "Antibiotics (prescription), rest, warm liquids, throat lozenges",
                "duration": "3-7 days with treatment",
                "contagious": "Yes - highly contagious"
            },
            "Tonsillitis": {
                "symptoms": ["sore throat", "red swollen tonsils", "white or yellow coating", "painful swallowing", "fever", "bad breath", "stiff neck", "headache"],
                "severity": "Moderate",
                "advice": "Rest, drink warm liquids, gargle salt water. See doctor if recurrent.",
                "treatment": "Antibiotics, rest, fluids, surgery if recurrent",
                "duration": "5-7 days",
                "contagious": "Yes"
            },
            "Laryngitis": {
                "symptoms": ["hoarse voice", "loss of voice", "dry throat", "sore throat", "cough", "difficulty speaking", "tickling sensation"],
                "severity": "Mild",
                "advice": "Rest your voice, stay hydrated, use humidifier, avoid whispering.",
                "treatment": "Voice rest, hydration, humidifier, avoid irritants",
                "duration": "1-2 weeks",
                "contagious": "Sometimes"
            },
            
            # 6. MUSCULOSKELETAL
            "Osteoarthritis": {
                "symptoms": ["joint pain", "stiffness", "swelling", "reduced range of motion", "grating sensation", "bone spurs", "morning stiffness"],
                "severity": "Mild to Severe",
                "advice": "Maintain healthy weight, exercise regularly, use heat/cold therapy.",
                "treatment": "Pain relievers, physical therapy, exercise, weight management",
                "duration": "Chronic",
                "contagious": "No"
            },
            "Gout": {
                "symptoms": ["intense joint pain", "swelling", "redness", "heat in joint", "tenderness", "limited mobility", "pain at night"],
                "severity": "Moderate to Severe",
                "advice": "Avoid purine-rich foods, stay hydrated, take prescribed medication.",
                "treatment": "Anti-inflammatory drugs, dietary changes, hydration",
                "duration": "3-10 days per flare",
                "contagious": "No"
            },
            
            # 7. URINARY & KIDNEY
            "Urinary Tract Infection (UTI)": {
                "symptoms": ["burning sensation during urination", "frequent urination", "cloudy urine", "strong-smelling urine", "pelvic pain", "blood in urine", "fever", "chills"],
                "severity": "Mild to Moderate",
                "advice": "Drink plenty of water, urinate frequently, see doctor for antibiotics.",
                "treatment": "Antibiotics, increased fluid intake, pain relievers",
                "duration": "3-7 days with treatment",
                "contagious": "No"
            },
            
            # 8. MENTAL HEALTH
            "Anxiety Disorder": {
                "symptoms": ["excessive worry", "restlessness", "fatigue", "difficulty concentrating", "irritability", "muscle tension", "sleep problems", "rapid heartbeat", "sweating"],
                "severity": "Mild to Severe",
                "advice": "Practice deep breathing, exercise regularly, consider therapy, maintain sleep schedule.",
                "treatment": "Therapy (CBT), medication, relaxation techniques, lifestyle changes",
                "duration": "Chronic",
                "contagious": "No"
            },
            "Depression": {
                "symptoms": ["persistent sadness", "loss of interest", "fatigue", "sleep changes", "appetite changes", "worthlessness", "difficulty concentrating", "thoughts of death"],
                "severity": "Mild to Severe",
                "advice": "⚠️ Seek professional help. Talk to someone you trust. Consider therapy.",
                "treatment": "Therapy, medication, support groups, lifestyle changes",
                "duration": "Chronic",
                "contagious": "No"
            },
            
            # 9. OTHER COMMON CONDITIONS
            "Dehydration": {
                "symptoms": ["excessive thirst", "dry mouth", "dark urine", "decreased urination", "dizziness", "fatigue", "confusion", "dry skin", "headache"],
                "severity": "Mild to Moderate",
                "advice": "Drink water immediately. Electrolyte drinks can help. Seek care if severe.",
                "treatment": "Hydration, electrolyte replacement, rest",
                "duration": "Hours to days",
                "contagious": "No"
            },
            "Insomnia": {
                "symptoms": ["difficulty falling asleep", "waking up frequently", "waking too early", "daytime fatigue", "irritability", "difficulty concentrating", "poor memory"],
                "severity": "Mild to Moderate",
                "advice": "Maintain regular sleep schedule, avoid caffeine before bed, create relaxing bedtime routine.",
                "treatment": "Sleep hygiene, CBT for insomnia, medication if needed",
                "duration": "Acute or chronic",
                "contagious": "No"
            },
            "Heat Exhaustion": {
                "symptoms": ["heavy sweating", "cold clammy skin", "nausea", "headache", "dizziness", "weakness", "rapid heartbeat", "muscle cramps", "fainting"],
                "severity": "Moderate",
                "advice": "Move to cool area, drink water, apply cool compresses. Seek care if symptoms worsen.",
                "treatment": "Cool environment, hydration, rest, electrolyte replacement",
                "duration": "Hours",
                "contagious": "No"
            }
        }
    
    def extract_symptoms(self, text):
        """Extract symptoms from user input with fuzzy matching"""
        text = text.lower()
        found_symptoms = []
        
        for disease_name, disease_info in self.diseases.items():
            for symptom in disease_info["symptoms"]:
                # Direct match
                if symptom in text and symptom not in found_symptoms:
                    found_symptoms.append(symptom)
                # Partial match for multi-word symptoms
                elif len(symptom.split()) > 1 and any(word in text for word in symptom.split()):
                    if symptom not in found_symptoms:
                        found_symptoms.append(symptom)
        
        return list(set(found_symptoms))
    
    def predict_disease(self, symptoms_text):
        """Predict disease based on symptoms with weighted scoring"""
        extracted = self.extract_symptoms(symptoms_text)
        
        if not extracted:
            return {
                "disease": "Unknown",
                "severity": "Unknown",
                "confidence": 0,
                "advice": "Please consult a healthcare professional. Try using more specific symptom descriptions like 'fever', 'cough', 'headache'.",
                "treatment": "Consult a doctor for proper diagnosis",
                "detected_symptoms": [],
                "duration": "Unknown",
                "contagious": "Unknown"
            }
        
        # Calculate weighted scores for each disease
        scores = {}
        for disease_name, disease_info in self.diseases.items():
            total_symptoms = len(disease_info["symptoms"])
            matched = [s for s in extracted if s in disease_info["symptoms"]]
            
            # Base score
            base_score = len(matched) / total_symptoms if total_symptoms > 0 else 0
            
            # Bonus for high-priority symptoms
            high_priority = ["difficulty breathing", "chest pain", "severe headache", "loss of consciousness", "blood"]
            bonus = 0
            for symptom in matched:
                if any(priority in symptom for priority in high_priority):
                    bonus += 0.15
            
            scores[disease_name] = {
                "score": min(1.0, base_score + bonus),
                "matched_count": len(matched),
                "matched_symptoms": matched,
                "info": disease_info
            }
        
        # Get best match
        best_match = max(scores, key=lambda x: scores[x]["score"])
        best_data = scores[best_match]
        confidence = round(best_data["score"] * 100, 1)
        
        # If confidence is too low, return uncertain
        if confidence < 20:
            return {
                "disease": "Uncertain",
                "severity": "Unknown",
                "confidence": confidence,
                "advice": "Your symptoms don't clearly match a specific condition. Please consult a healthcare provider for accurate diagnosis.",
                "treatment": "Monitor symptoms and seek medical advice if they persist or worsen",
                "detected_symptoms": extracted[:5],
                "duration": "Unknown",
                "contagious": "Unknown"
            }
        
        disease_info = best_data["info"]
        
        return {
            "disease": best_match,
            "severity": disease_info["severity"],
            "confidence": confidence,
            "advice": disease_info["advice"],
            "treatment": disease_info["treatment"],
            "detected_symptoms": best_data["matched_symptoms"][:5],
            "duration": disease_info.get("duration", "Varies"),
            "contagious": disease_info.get("contagious", "Consult doctor")
        }

# Create global instance
model = HealthModel()

def predict_disease(symptoms_text):
    """Wrapper function for Flask app"""
    return model.predict_disease(symptoms_text)

# Test the model
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AI Health Model - 23 Diseases Test")
    print("=" * 60)
    
    test_symptoms = [
        "fever, cough, runny nose",
        "severe headache, nausea, sensitivity to light",
        "chest pain, difficulty breathing",
        "sneezing, itchy eyes, runny nose",
        "nausea, vomiting, diarrhea"
    ]
    
    for symptoms in test_symptoms:
        result = predict_disease(symptoms)
        print(f"\n📋 Symptoms: {symptoms}")
        print(f"   Prediction: {result['disease']}")
        print(f"   Confidence: {result['confidence']}%")
        print(f"   Severity: {result['severity']}")
        print(f"   Advice: {result['advice'][:80]}...")
    
    print("\n" + "=" * 60)
    print(f"✅ Model loaded with {len(model.diseases)} diseases")
    print("=" * 60)
