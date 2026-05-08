from gradio_client import Client
client = Client("http://127.0.0.1:7860/")
for i, ep in enumerate(client.endpoints):
    print(i, ep.api_name, ep.fn_index)
