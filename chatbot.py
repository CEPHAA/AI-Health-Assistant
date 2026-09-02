import random
import re

class HealthChatbot:
    def __init__(self):
        self.responses = {
            "greeting": [
                "Hello! How can I help you with your health today?",
                "Hi there! I'm your AI health assistant. What can I do for you?",
                "Welcome! How are you feeling today?"
            ],
            "symptoms": [
                "I can help analyze your symptoms. Please describe what you're experiencing.",
                "Tell me more about your symptoms so I can provide better guidance.",
                "What symptoms are you experiencing? Be as specific as possible."
            ],
            "fever": [
                "A fever indicates your body is fighting an infection. Stay hydrated and rest. If fever exceeds 103°F (39.4°C), seek medical attention.",
                "Monitor your temperature. For mild fever, rest and drink fluids. Consult a doctor if it persists for more than 3 days."
            ],
            "headache": [
                "Headaches can be caused by stress, dehydration, or lack of sleep. Try resting in a dark room and staying hydrated.",
                "For headaches, ensure you're drinking enough water and taking breaks from screens. If severe, consider over-the-counter pain relief."
            ],
            "cough": [
                "A cough can be from allergies, cold, or respiratory infection. Honey and warm liquids can help soothe your throat.",
                "Persistent cough lasting more than 2 weeks should be evaluated by a doctor. Stay hydrated and rest."
            ],
            "fatigue": [
                "Fatigue often results from poor sleep, stress, or nutritional deficiencies. Ensure you're getting 7-9 hours of sleep and eating well.",
                "Persistent fatigue may indicate underlying issues. Consider your sleep quality, stress levels, and diet."
            ],
            "emergency": [
                "⚠️ If you're experiencing severe symptoms like difficulty breathing, chest pain, or severe bleeding, please call emergency services immediately!",
                "🚨 This could be a medical emergency. Please seek immediate medical attention or call emergency services."
            ],
            "prevention": [
                "Good hygiene, regular exercise, balanced diet, and adequate sleep are key to preventing many illnesses.",
                "Wash hands frequently, stay hydrated, maintain social distance when sick, and get recommended vaccines."
            ],
            "default": [
                "I understand. For medical advice, please consult a healthcare professional. Would you like to use our symptom checker?",
                "That's important to note. Consider using our symptom checker for a more detailed analysis."
            ]
        }
    
    def get_response(self, message):
        message = message.lower()
        
        # Emergency detection
        if any(word in message for word in ["emergency", "heart attack", "stroke", "bleeding", "can't breathe", "chest pain"]):
            return random.choice(self.responses["emergency"])
        
        # Greeting detection
        if any(word in message for word in ["hello", "hi", "hey", "greetings"]):
            return random.choice(self.responses["greeting"])
        
        # Symptom-related responses
        if "symptom" in message:
            return random.choice(self.responses["symptoms"])
        
        if "fever" in message or "temperature" in message:
            return random.choice(self.responses["fever"])
        
        if "headache" in message or "migraine" in message:
            return random.choice(self.responses["headache"])
        
        if "cough" in message:
            return random.choice(self.responses["cough"])
        
        if "tired" in message or "fatigue" in message or "energy" in message:
            return random.choice(self.responses["fatigue"])
        
        if "prevent" in message or "avoid" in message:
            return random.choice(self.responses["prevention"])
        
        # Default response
        return random.choice(self.responses["default"])

chatbot = HealthChatbot()

def get_response(message):
    return chatbot.get_response(message)

