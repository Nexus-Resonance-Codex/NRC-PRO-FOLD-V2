from gradio_client import Client
import json
client = Client("http://127.0.0.1:7860/")
result = client.predict("MTEY", "Three.js", "NRC Pure Math & Physics Engine (Deterministic)", "", fn_index=3)
print("SUCCESS. Output length:", len(result))
