import gradio as gr
import pandas as pd

def test_func():
    # Simulate what app.py generates
    summary_data = [
        ["Residues", "4"], 
        ["Avg Confidence", "100.00%"], 
        ["TTT Stability", "1.0000"],
        ["Resonance Error", "0.0000"],
        ["Mode", "NRC Pure Math & Physics Engine (Deterministic)"]
    ]
    summary_df = pd.DataFrame(summary_data, columns=["Metric", "Value"])
    return summary_df

with gr.Blocks() as demo:
    out1 = gr.Dataframe()
    btn = gr.Button("run")
    btn.click(test_func, outputs=[out1])

if __name__ == "__main__":
    demo.launch(prevent_thread_lock=True, server_port=7862)
    from gradio_client import Client
    client = Client("http://127.0.0.1:7862/")
    res = client.predict(fn_index=0)
    print("SUCCESS", res)
