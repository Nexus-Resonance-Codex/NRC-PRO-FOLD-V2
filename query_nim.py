import os
import requests
import json

api_key = "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"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

prompt = """
You are the Llama 4 Maverick / DeepSeek V3 agent on the NVIDIA NIM manifold.
The user requires a detailed step-by-step plan with full code to achieve 100% accuracy on the REFOLD test using ONLY Pure Math (NRC pure engine, deterministic phi-spiral mathematics, TTT-7 stability).
Generate a detailed plan and the complete python code for `nrc_engine.py` (specifically the `_initialize_lattice` and the 30-step turbulence loop) that strictly relies on pure mathematical derivations (no AI inference) and guarantees 100% REFOLD parity.
Output the plan and the python code.
"""

data = {
    "model": "meta/llama-3.1-70b-instruct",
    "messages": [{"role": "user", "content": prompt}],
    "temperature": 0.2,
    "max_tokens": 2048
}

response = requests.post("https://integrate.api.nvidia.com/v1/chat/completions", headers=headers, json=data)
if response.status_code == 200:
    print(response.json()["choices"][0]["message"]["content"])
else:
    print(f"Error {response.status_code}: {response.text}")
