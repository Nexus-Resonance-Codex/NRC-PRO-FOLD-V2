import gradio as gr
import pandas as pd
import time

def test_func():
    yield ["logging..."] + [None]*16
    time.sleep(0.5)
    
    viewer_html = "<div>html</div>"
    
    summary_data = [
        ["Residues", "4"], 
        ["Avg Confidence", "100.00%"]
    ]
    summary_df = pd.DataFrame(summary_data, columns=["Metric", "Value"])
    
    zip_path = "/tmp/test.zip"
    
    yield [
        "logs", viewer_html, None, None, None, None, None, None,
        summary_df, zip_path, "ATOM 1...", "CCCC", 5.5, "a1b2c3d4", [], {}, {}
    ]

with gr.Blocks() as demo:
    out0 = gr.Textbox()
    out1 = gr.HTML()
    out2 = gr.Plot()
    out3 = gr.Plot()
    out4 = gr.Plot()
    out5 = gr.Plot()
    out6 = gr.Plot()
    out7 = gr.Plot()
    out8 = gr.Dataframe()
    out9 = gr.File()
    out10 = gr.Code()
    out11 = gr.Textbox()
    out12 = gr.Label()
    out13 = gr.Label()
    out14 = gr.State()
    out15 = gr.State()
    out16 = gr.State()
    btn = gr.Button("run")
    btn.click(test_func, outputs=[out0, out1, out2, out3, out4, out5, out6, out7, out8, out9, out10, out11, out12, out13, out14, out15, out16])

if __name__ == "__main__":
    demo.launch(prevent_thread_lock=True, server_port=7864)
    from gradio_client import Client
    client = Client("http://127.0.0.1:7864/")
    res = client.predict(fn_index=0)
    print("SUCCESS", len(res))
