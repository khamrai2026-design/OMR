#!/usr/bin/env python
"""Test the analytics endpoint"""
import requests
import json

response = requests.get('http://localhost:5000/api/analytics')
if response.status_code == 200:
    data = response.json()
    print("✓ Analytics endpoint is working!")
    print(f"  Total attempts: {data.get('total_attempts')}")
    print(f"  Average score: {data.get('avg_score')}")
    print(f"  Best score: {data.get('best_score')}")
else:
    print(f"✗ Error: {response.status_code}")
    print(response.text)
