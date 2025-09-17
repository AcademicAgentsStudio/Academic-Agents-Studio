import gradio as gr

def simple_test():
    return "测试成功！界面正常工作。"

# 创建简单的测试界面
with gr.Blocks(title="测试界面") as demo:
    gr.HTML("<h1>🧪 界面测试</h1>")

    with gr.Row():
        test_btn = gr.Button("点击测试", variant="primary")
        output = gr.Textbox(label="输出")

    test_btn.click(simple_test, outputs=output)

if __name__ == "__main__":
    demo.launch(server_port=7861, share=False)