import gradio as gr
import sys

from toolbox import is_any_api_key, load_chat_cookies

cookies = load_chat_cookies()
print(is_any_api_key("sk-LBq3ru0nc6dSr1Jh79C83228A1544186Ad0a2bC4CaA2929c"))
print(cookies)






sys.exit(0)
# 定义一个简单的函数
def greet(name):
    return f"Hello, {name}!"

def classify_image(image):
    # 假设我们有一个图像分类模型（简化示例）
    return "This is a cat."

def number_fun(value):
    return value

def analyze_text(text, slider):
    # 返回一些分析结果
    return f"Text length: {len(text)}, Slider value: {slider}"
# text（文本框）、image（图片上传）、audio（音频上传）、slider（滑动条）、checkbox（复选框）
# text（文本）、image（显示图片）、label（标签）、plot（显示图表）等
# 使用 Gradio 创建接口
# iface = gr.Interface(
#     fn=greet,                  # 调用的函数
#     inputs=["text","slider"],             # 输入组件：文本
#     outputs="text"             # 输出组件：文本
# )
#
# # 启动应用
# iface.launch()
# 使用 Gradio 创建 Blocks 界面
with gr.Blocks() as demo:
    # with gr.Row():
        # iface1 = gr.Interface(fn=greet, inputs="text", outputs="text").load()
        # iface2 = gr.Interface(fn=number_fun, inputs="number", outputs="number")
        # iface3 = gr.Interface(fn=analyze_text, inputs=["text", "slider"], outputs="text")
        # iface4 = gr.Interface(fn=classify_image, inputs="image", outputs="label") # 使用 classify_image 函数

    # 将所有接口添加到 Blocks 中，不需要单独调用 launch()
    with gr.Row():
        input_name = gr.Textbox(label="Your name")
        greet_output = gr.Textbox(label="Greeting")

        input_number = gr.Number(label="Enter a number")
        number_output = gr.Number(label="Number Output")

        input_text = gr.Textbox(label="Text to analyze")
        slider_value = gr.Slider(label="Slider Value", minimum=0, maximum=10, step=1)
        text_analysis_output = gr.Textbox(label="Text Analysis")

        image_input = gr.Image(label="Image to classify")
        image_output = gr.Label(label="Image Classification")

    # 设置交互功能
    greet_button = gr.Button("Greet")
    greet_button.click(greet, inputs=input_name, outputs=greet_output)

    number_button = gr.Button("Process Number")
    number_button.click(number_fun, inputs=input_number, outputs=number_output)

    text_analysis_button = gr.Button("Analyze Text")
    text_analysis_button.click(analyze_text, inputs=[input_text, slider_value], outputs=text_analysis_output)

    image_button = gr.Button("Classify Image")
    image_button.click(classify_image, inputs=image_input, outputs=image_output)
demo.launch()