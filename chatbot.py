"""
AI Health Chatbot
Provides conversational health guidance
"""

import re
import random
from datetime import datetime

class HealthChatbot:
    """Intelligent health chatbot"""
    
    def __init__(self):
        self.context = {}
        self.greetings = [
            "Hello! I'm your AI health assistant. How can I help you today?",
            "Hi there! Ready to help with your health concerns. What's bothering you?",
            "Welcome! I'm here to provide health information. What would you like to know?",
            "Greetings! How are you feeling today?"
        ]
        
        self.symptom_questions = [
            "What symptoms are you experiencing?",
            "Can you describe how you're feeling?",
            "Tell me more about your symptoms.",
            "What specific symptoms do you have?"
        ]
        
        self.responses = {
            "fever": [
                "Fever indicates your body is fighting an infection. Monitor your temperature. If it exceeds 103°F (39.4°C), seek medical attention.",
                "For fever, rest and stay hydrated. Take fever reducers if needed. Seek care if fever persists beyond 3 days."
            ],
            "cough": [
                "A cough can be from allergies, cold, or respiratory infection. Try honey and warm liquids. Persistent cough > 2 weeks needs evaluation.",
                "Stay hydrated and rest. If cough is productive with colored mucus, consider seeing a doctor."
            ],
            "headache": [
                "Headaches often result from stress, dehydration, or lack of sleep. Rest in a dark room and hydrate.",
                "For headaches, ensure adequate water intake. If severe or recurring, consult a doctor."
            ],
            "fatigue": [
                "Fatigue can indicate poor sleep, stress, or nutritional deficiencies. Aim for 7-9 hours of quality sleep.",
                "Persistent fatigue may require medical evaluation. Consider your sleep, diet, and stress levels."
            ],
            "nausea": [
                "Nausea often resolves with rest and clear fluids. Try ginger or peppermint tea.",
                "If nausea persists or you can't keep liquids down, seek medical care to prevent dehydration."
            ],
            "chest pain": [
                "🚨 CHEST PAIN IS A MEDICAL EMERGENCY. Seek immediate emergency care!",
                "⚠️ Do not ignore chest pain. Call emergency services immediately."
            ],
            "difficulty breathing": [
                "🚨 DIFFICULTY BREATHING IS AN EMERGENCY. Get medical help immediately!",
                "⚠️ This requires urgent medical attention. Call emergency services now."
            ],
            "prevention": [
                "Prevention tips: Wash hands frequently, get adequate sleep, exercise regularly, eat balanced meals, stay hydrated.",
                "Boost immunity with vitamin C, zinc, proper nutrition, and regular physical activity."
            ],
            "medication": [
                "I can provide general information, but always consult a doctor before taking medication.",
                "Medication questions should be directed to your healthcare provider or pharmacist."
            ],
            "emergency": [
                "🚨 If you're experiencing severe symptoms, difficulty breathing, chest pain, or severe bleeding, call emergency services immediately!",
                "⚠️ This may be a medical emergency. Seek immediate professional care."
            ]
        }
        
        self.fallback = [
            "I understand. For medical advice, please consult a healthcare professional. Would you like to use our symptom checker?",
            "That's important. Consider using our symptom checker for a detailed analysis.",
            "I'm here to help with health information. Could you tell me more about your symptoms?"
        ]
    
    def get_response(self, message):
        """Generate response based on user message"""
        message_lower = message.lower()
        
        # Check for emergency keywords
        emergency_keywords = ["emergency", "heart attack", "stroke", "bleeding", "can't breathe", "chest pain", "difficulty breathing", "severe pain"]
        if any(keyword in message_lower for keyword in emergency_keywords):
            return random.choice(self.responses["emergency"])
        
        # Check for greetings
        greeting_keywords = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"]
        if any(keyword in message_lower for keyword in greeting_keywords):
            return random.choice(self.greetings)
        
        # Check for symptom requests
        symptom_keywords = ["symptom", "feel", "experiencing", "bothering", "issue"]
        if any(keyword in message_lower for keyword in symptom_keywords) and len(message_lower.split()) < 10:
            return random.choice(self.symptom_questions)
        
        # Match specific symptoms
        if "fever" in message_lower or "temperature" in message_lower:
            return random.choice(self.responses["fever"])
        
        if "cough" in message_lower:
            return random.choice(self.responses["cough"])
        
        if "headache" in message_lower or "migraine" in message_lower:
            return random.choice(self.responses["headache"])
        
        if "tired" in message_lower or "fatigue" in message_lower or "exhausted" in message_lower:
            return random.choice(self.responses["fatigue"])
        
        if "nausea" in message_lower or "vomit" in message_lower:
            return random.choice(self.responses["nausea"])
        
        if "chest" in message_lower and "pain" in message_lower:
            return random.choice(self.responses["chest pain"])
        
        if "breath" in message_lower:
            return random.choice(self.responses["difficulty breathing"])
        
        if "prevent" in message_lower or "avoid" in message_lower:
            return random.choice(self.responses["prevention"])
        
        if "medication" in message_lower or "medicine" in message_lower or "drug" in message_lower:
            return random.choice(self.responses["medication"])
        
        # Default response
        return random.choice(self.fallback)

# Global chatbot instance
chatbot = HealthChatbot()

def get_response(message):
    """Wrapper function for Flask app"""
    return chatbot.get_response(message)

# Test the chatbot
if __name__ == "__main__":
    test_messages = [
        "Hello",
        "I have a fever and cough",
        "What can I do to prevent illness?",
        "My chest hurts"
    ]
    
    for msg in test_messages:
        print(f"\nUser: {msg}")
        print(f"Bot: {get_response(msg)}")
