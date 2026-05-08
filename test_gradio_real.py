from gradio_client import Client
client = Client("http://127.0.0.1:7860/")
result = client.predict("MTEY", "Three.js", "NRC Pure Math & Physics Engine (Deterministic)", "", fn_index=4)
print("SUCCESS:", len(result))
