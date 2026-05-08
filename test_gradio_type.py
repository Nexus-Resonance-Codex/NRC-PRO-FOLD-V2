import gradio as gr
import pandas as pd

def test_func():
    df = pd.DataFrame([["A", "10"], ["B", "20.5%"]], columns=["X", "Y"])
    return df, 5.5, "my_hash_string"

with gr.Blocks() as demo:
    out1 = gr.Dataframe()
    out2 = gr.Label()
    out3 = gr.Label()
    btn = gr.Button("run")
    btn.click(test_func, outputs=[out1, out2, out3])

if __name__ == "__main__":
    demo.launch(prevent_thread_lock=True)
    from gradio_client import Client
    client = Client("http://127.0.0.1:7861/")
    res = client.predict(fn_index=0)
    print("SUCCESS", res)
