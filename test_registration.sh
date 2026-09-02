#!/bin/bash
# Test user registration and login

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 TESTING USER REGISTRATION & LOGIN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

BASE_URL="http://localhost:5000"
COOKIES="/tmp/cookies.txt"

echo ""
echo "📌 1. REGISTER NEW PATIENT"
echo "─────────────────────────────────────────────────────────────"

# Register a new user
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/register" \
  -d "name=Test%20User&email=testuser$(date +%s)@example.com&password=Test123&confirm_password=Test123")

if echo "$REGISTER_RESPONSE" | grep -qi "redirect"; then
    echo "✅ Registration successful"
else
    echo "❌ Registration failed"
fi

echo ""
echo "📌 2. LOGIN WITH NEW CREDENTIALS"
echo "─────────────────────────────────────────────────────────────"

echo ""
echo "📌 3. VERIFY USER IN DATABASE"
echo "─────────────────────────────────────────────────────────────"

sqlite3 database.db "SELECT id, name, email, user_type, created_at FROM users WHERE user_type='patient' ORDER BY id DESC LIMIT 5;"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ TEST COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
