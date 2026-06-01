#!/bin/bash

# Quick Start Script for Terraform AI Agent

echo "🤖 Terraform AI Agent - Quick Start Setup"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi
echo "✅ Python 3 found: $(python3 --version)"

# Check API key
if [ -z "$OPENROUTER_API_KEY" ] && [ -z "$LLM_API_KEY" ]; then
    echo ""
    echo "⚠️  No API key found!"
    echo ""
    echo "   Get your free API key from: https://openrouter.ai"
    echo ""
    echo "   Then set environment variable:"
    echo "   export OPENROUTER_API_KEY='your-key-here'"
    echo ""
    exit 1
fi
echo "✅ API Key configured"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt 2>/dev/null || pip3 install -q -r requirements.txt
echo "✅ Dependencies installed"

# Run demo
echo ""
echo "📚 Running demo..."
python3 demo.py

echo ""
echo "🚀 Quick Start:"
echo "   python agent.py \"your requirement\" --cloud azure"
echo "   python agent.py \"your requirement\" --cloud aws"
echo "   python agent.py \"your requirement\" --cloud gcp"
echo "   python agent.py --interactive"
echo ""
