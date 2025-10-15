#!/bin/bash

echo "🚀 DBT + SODA COMPLETE TEST SUITE"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "/home/ubuntu/myenv" ]; then
    echo "❌ Virtual environment not found. Please create one first:"
    echo "   python3 -m venv /home/ubuntu/myenv"
    echo "   source /home/ubuntu/myenv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source /home/ubuntu/myenv/bin/activate

# Check if email is configured
if [ -z "$SENDER_EMAIL" ] || [ "$SENDER_EMAIL" = "your-email@gmail.com" ]; then
    echo "⚠️  Email not configured. To enable email notifications:"
    echo "   export SENDER_EMAIL=your-email@gmail.com"
    echo "   export SENDER_PASSWORD=your-app-password"
    echo "   export RECIPIENT_EMAIL=recipient@gmail.com"
    echo ""
    echo "Continuing without email notifications..."
fi

# Run the complete test suite
echo "🧪 Running complete test suite..."
python test_all.py

echo ""
echo "✅ Test suite completed!"
echo "📊 Check results above for detailed output"
