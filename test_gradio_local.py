import requests
resp = requests.post("http://127.0.0.1:7860/queue/join", json={
    "data": ["MTEY", "Three.js", "NRC Pure Math & Physics Engine (Deterministic)", ""],
    "fn_index": 3,
    "session_hash": "testhash123"
})
print(resp.status_code)
print(resp.json())
import time
time.sleep(1)
resp2 = requests.get("http://127.0.0.1:7860/queue/data?session_hash=testhash123")
print("Stream:")
for line in resp2.iter_lines():
    print(line)
