"""
    该文件中主要包含三个函数

    不具备多线程能力的函数：
    1. predict: 正常对话时使用，具备完备的交互功能，不可多线程

    具备多线程调用能力的函数
    2. predict_no_ui_long_connection：支持多线程
"""

import json
import os
import re
import time
import traceback
import requests
import random

from loguru import logger

# config_private.py放自己的秘密如API和代理网址
# 读取时首先看是否存在私密的config_private配置文件（不受git管控），如果有，则覆盖原config文件
from toolbox import get_conf, update_ui, is_any_api_key, select_api_key, what_keys, clip_history
from toolbox import trimmed_format_exc, is_the_upload_folder, read_one_api_model_name, log_chat
from toolbox import ChatBotWithCookies, have_any_recent_upload_image_files, encode_image
proxies, WHEN_TO_USE_PROXY, TIMEOUT_SECONDS, MAX_RETRY, API_ORG, AZURE_CFG_ARRAY = \
    get_conf('proxies', 'WHEN_TO_USE_PROXY', 'TIMEOUT_SECONDS', 'MAX_RETRY', 'API_ORG', 'AZURE_CFG_ARRAY')

if "Connect_OpenAI" not in WHEN_TO_USE_PROXY:
    if proxies is not None:
        logger.error("虽然您配置了代理设置，但不会在连接OpenAI的过程中起作用，请检查WHEN_TO_USE_PROXY配置。")
        proxies = None

timeout_bot_msg = '[Local Message] Request timeout. Network error. Please check proxy settings in config.py.' + \
                  '网络错误，检查代理服务器是否可用，以及代理设置的格式是否正确，格式须是[协议]://[地址]:[端口]，缺一不可。'

def get_full_error(chunk, stream_response):
    """
        获取完整的从Openai返回的报错
    """
    while True:
        try:
            chunk += next(stream_response)
        except:
            break
    return chunk

def make_multimodal_input(inputs, image_paths):
    image_base64_array = []
    for image_path in image_paths:
        path = os.path.abspath(image_path)
        base64 = encode_image(path)
        inputs = inputs + f'<br/><br/><div align="center"><img src="file={path}" base64="{base64}"></div>'
        image_base64_array.append(base64)
    return inputs, image_base64_array

def reverse_base64_from_input(inputs):
    # 定义一个正则表达式来匹配 Base64 字符串（假设格式为 base64="<Base64编码>"）
    # pattern = re.compile(r'base64="([^"]+)"></div>')
    pattern = re.compile(r'<br/><br/><div align="center"><img[^<>]+base64="([^"]+)"></div>')
    # 使用 findall 方法查找所有匹配的 Base64 字符串
    base64_strings = pattern.findall(inputs)
    # 返回反转后的 Base64 字符串列表
    return base64_strings

def contain_base64(inputs):
    base64_strings = reverse_base64_from_input(inputs)
    return len(base64_strings) > 0

def append_image_if_contain_base64(inputs):
    if not contain_base64(inputs):
        return inputs
    else:
        image_base64_array = reverse_base64_from_input(inputs)
        pattern = re.compile(r'<br/><br/><div align="center"><img[^><]+></div>')
        inputs = re.sub(pattern, '', inputs)
        res = []
        res.append({
            "type": "text",
            "text": inputs
        })
        for image_base64 in image_base64_array:
            res.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            })
        return res

def remove_image_if_contain_base64(inputs):
    if not contain_base64(inputs):
        return inputs
    else:
        pattern = re.compile(r'<br/><br/><div align="center"><img[^><]+></div>')
        inputs = re.sub(pattern, '', inputs)
        return inputs

def decode_chunk(chunk):
    # 提前读取一些信息 （用于判断异常）
    chunk_decoded = chunk.decode()
    chunkjson = None
    has_choices = False
    choice_valid = False
    has_content = False
    has_role = False
    try:
        chunkjson = json.loads(chunk_decoded[6:])
        has_choices = 'choices' in chunkjson
        if has_choices: choice_valid = (len(chunkjson['choices']) > 0)
        if has_choices and choice_valid: has_content = ("content" in chunkjson['choices'][0]["delta"])
        if has_content: has_content = (chunkjson['choices'][0]["delta"]["content"] is not None)
        if has_choices and choice_valid: has_role = "role" in chunkjson['choices'][0]["delta"]
    except:
        pass
    return chunk_decoded, chunkjson, has_choices, choice_valid, has_content, has_role

from functools import lru_cache
@lru_cache(maxsize=32)
def verify_endpoint(endpoint):
    """
        检查endpoint是否可用
    """
    if "你亲手写的api名称" in endpoint:
        raise ValueError("Endpoint不正确, 请检查AZURE_ENDPOINT的配置! 当前的Endpoint为:" + endpoint)
    return endpoint

def predict_no_ui_long_connection(inputs:str, llm_kwargs:dict, history:list=[], sys_prompt:str="", observe_window:list=None, console_silence:bool=False):
    """
    发送至chatGPT，等待回复，一次性完成，不显示中间过程。但内部用stream的方法避免中途网线被掐。
    inputs：
        是本次问询的输入
    sys_prompt:
        系统静默prompt
    llm_kwargs：
        chatGPT的内部调优参数
    history：
        是之前的对话列表
    observe_window = None：
        用于负责跨越线程传递已经输出的部分，大部分时候仅仅为了fancy的视觉效果，留空即可。observe_window[0]：观测窗。observe_window[1]：看门狗
    """
    from request_llms.bridge_all import model_info

    watch_dog_patience = 1500 # 看门狗的耐心, 设置5秒即可

    if model_info[llm_kwargs['llm_model']].get('openai_disable_stream', False): stream = False
    else: stream = True

    headers, payload = generate_payload(inputs, llm_kwargs, history, system_prompt=sys_prompt, stream=stream)
    retry = 0
    while True:
        try:
            # make a POST request to the API endpoint, stream=False
            endpoint = verify_endpoint(model_info[llm_kwargs['llm_model']]['endpoint'])
            response = requests.post(endpoint, headers=headers, proxies=proxies,
                                    json=payload, stream=stream, timeout=TIMEOUT_SECONDS); break
        except requests.exceptions.ReadTimeout as e:
            retry += 1
            traceback.print_exc()
            if retry > MAX_RETRY: raise TimeoutError
            if MAX_RETRY!=0: logger.error(f'请求超时，正在重试 ({retry}/{MAX_RETRY}) ……')

    if not stream:
        # 该分支仅适用于不支持stream的o1模型，其他情形一律不适用
        chunkjson = json.loads(response.content.decode())
        gpt_replying_buffer = chunkjson['choices'][0]["message"]["content"]
        return gpt_replying_buffer

    stream_response = response.iter_lines()
    result = ''
    json_data = None
    while True:
        try: chunk = next(stream_response)
        except StopIteration:
            break
        except requests.exceptions.ConnectionError:
            chunk = next(stream_response) # 失败了，重试一次？再失败就没办法了。
        chunk_decoded, chunkjson, has_choices, choice_valid, has_content, has_role = decode_chunk(chunk)
        if len(chunk_decoded)==0: continue
        if not chunk_decoded.startswith('data:'):
            error_msg = get_full_error(chunk, stream_response).decode()
            if "reduce the length" in error_msg:
                raise ConnectionAbortedError("OpenAI拒绝了请求:" + error_msg)
            elif """type":"upstream_error","param":"307""" in error_msg:
                raise ConnectionAbortedError("正常结束，但显示Token不足，导致输出不完整，请削减单次输入的文本量。")
            else:
                raise RuntimeError("OpenAI拒绝了请求：" + error_msg)
        if ('data: [DONE]' in chunk_decoded): break # api2d & aioagi 正常完成
        # 提前读取一些信息 （用于判断异常）
        if has_choices and not choice_valid:
            # 一些垃圾第三方接口的出现这样的错误
            continue
        json_data = chunkjson['choices'][0]
        delta = json_data["delta"]

        if len(delta) == 0:
            is_termination_certain = False
            if (has_choices) and (chunkjson['choices'][0].get('finish_reason', 'null') == 'stop'): is_termination_certain = True
            if is_termination_certain: break
            else: continue # 对于不符合规范的狗屎接口，这里需要继续

        if (not has_content) and has_role: continue
        if (not has_content) and (not has_role): continue # raise RuntimeError("发现不标准的第三方接口："+delta)
        if has_content: # has_role = True/False
            result += delta["content"]
            if not console_silence: print(delta["content"], end='')
            if observe_window is not None:
                # 观测窗，把已经获取的数据显示出去
                if len(observe_window) >= 1:
                    observe_window[0] += delta["content"]
                # 看门狗，如果超过期限没有喂狗，则终止
                if len(observe_window) >= 2:
                    if (time.time()-observe_window[1]) > watch_dog_patience:
                        raise RuntimeError("用户取消了程序。")
        else: raise RuntimeError("意外Json结构："+delta)

    finish_reason = json_data.get('finish_reason', None) if json_data else None
    if finish_reason == 'content_filter':
        raise RuntimeError("由于提问含不合规内容被过滤。")
    if finish_reason == 'length':
        raise ConnectionAbortedError("正常结束，但显示Token不足，导致输出不完整，请削减单次输入的文本量。")

    return result


def predict(inputs:str, llm_kwargs:dict, plugin_kwargs:dict, chatbot:ChatBotWithCookies,
            history:list=[], system_prompt:str='', stream:bool=True, additional_fn:str=None):
    """
    发送至chatGPT，流式获取输出。
    用于基础的对话功能。
    inputs 是本次问询的输入
    top_p, temperature是chatGPT的内部调优参数
    history 是之前的对话列表（注意无论是inputs还是history，内容太长了都会触发token数量溢出的错误）
    chatbot 为WebUI中显示的对话列表，修改它，然后yield出去，可以直接修改对话界面内容
    additional_fn代表点击的哪个按钮，按钮见functional.py
    """
    from request_llms.bridge_all import model_info
    if is_any_api_key(inputs):
        chatbot._cookies['api_key'] = inputs
        chatbot.append(("输入已识别为openai的api_key", what_keys(inputs)))
        yield from update_ui(chatbot=chatbot, history=history, msg="api_key已导入") # 刷新界面
        return
    elif not is_any_api_key(chatbot._cookies['api_key']):
        chatbot.append((inputs, "缺少api_key。\n\n1. 临时解决方案：直接在输入区键入api_key，然后回车提交。\n\n2. 长效解决方案：在config.py中配置。"))
        yield from update_ui(chatbot=chatbot, history=history, msg="缺少api_key") # 刷新界面
        return

    user_input = inputs
    if additional_fn is not None:
        from core_functional import handle_core_functionality
        inputs, history = handle_core_functionality(additional_fn, inputs, history, chatbot)

    # 多模态模型
    has_multimodal_capacity = model_info[llm_kwargs['llm_model']].get('has_multimodal_capacity', False)
    if has_multimodal_capacity:
        has_recent_image_upload, image_paths = have_any_recent_upload_image_files(chatbot, pop=True)
    else:
        has_recent_image_upload, image_paths = False, []
    if has_recent_image_upload:
        _inputs, image_base64_array = make_multimodal_input(inputs, image_paths)
    else:
        _inputs, image_base64_array = inputs, []
    chatbot.append((_inputs, ""))
    yield from update_ui(chatbot=chatbot, history=history, msg="等待响应") # 刷新界面

    # 禁用stream的特殊模型处理
    if model_info[llm_kwargs['llm_model']].get('openai_disable_stream', False): stream = False
    else: stream = True

    # check mis-behavior
    if is_the_upload_folder(user_input):
        chatbot[-1] = (inputs, f"[Local Message] 检测到操作错误！当您上传文档之后，需点击“**函数插件区**”按钮进行处理，请勿点击“提交”按钮或者“基础功能区”按钮。")
        yield from update_ui(chatbot=chatbot, history=history, msg="正常") # 刷新界面
        time.sleep(2)

    try:
        headers, payload = generate_payload(inputs, llm_kwargs, history, system_prompt, image_base64_array, has_multimodal_capacity, stream)
    except RuntimeError as e:
        chatbot[-1] = (inputs, f"您提供的api-key不满足要求，不包含任何可用于{llm_kwargs['llm_model']}的api-key。您可能选择了错误的模型或请求源。")
        yield from update_ui(chatbot=chatbot, history=history, msg="api-key不满足要求") # 刷新界面
        return

    # 检查endpoint是否合法
    try:
        endpoint = verify_endpoint(model_info[llm_kwargs['llm_model']]['endpoint'])
    except:
        tb_str = '```\n' + trimmed_format_exc() + '```'
        chatbot[-1] = (inputs, tb_str)
        yield from update_ui(chatbot=chatbot, history=history, msg="Endpoint不满足要求") # 刷新界面
        return

    # 加入历史
    if has_recent_image_upload:
        history.extend([_inputs, ""])
    else:
        history.extend([inputs, ""])

    previous_ui_reflesh_time = 0
    ui_reflesh_min_interval = 0.0

    # 使用线程创建聊天，主线程负责更新进度显示
    import time
    import threading

    start_time = time.time()

    response = None
    creation_complete = False
    creation_error = None
    max_wait_time = 600  # 最多等待60秒

    def create_post():
        nonlocal response, creation_complete, creation_error
        try:
            response = requests.post(endpoint, headers=headers, proxies=proxies,
                                     json=payload, stream=stream, timeout=TIMEOUT_SECONDS)
            creation_complete = True
        except Exception as e:
            print(f"POST失败: {e}")
            creation_error = e
            creation_complete = True

    # 启动POST聊天创建线程
    creation_thread = threading.Thread(target=create_post, daemon=True)
    creation_thread.start()

    # 主线程每秒更新一次进度显示
    while not creation_complete and (time.time() - start_time) < max_wait_time:
        elapsed = int(time.time() - start_time)

        progress_msg = f"⏳ 请稍候...({elapsed}s)"

        chatbot[-1] = [chatbot[-1][0], progress_msg]

        # 更新UI
        for ui_update in update_ui(chatbot=chatbot, history=history):
            yield ui_update

        # 等待5秒或直到创建完成
        wait_start = time.time()
        while (time.time() - wait_start) < 1 and not creation_complete:
            time.sleep(0.5)  # 每0.5秒检查一次是否完成

    # 如果创建线程仍在运行且超时，显示超时信息
    if not creation_complete:
        print("POST创建超时")
        progress_msg = f"🤖模型返回超时，请重试/联系管理员维护！"
        chatbot[-1] = [chatbot[-1][0], progress_msg]
        for ui_update in update_ui(chatbot=chatbot, history=history):
            yield ui_update
        raise Exception("POST创建超时，请重试")

    # 如果创建过程中有错误，抛出异常
    if creation_error:
        progress_msg = f"🤖模型返回出错，请重试/联系管理员维护！"
        chatbot[-1] = [chatbot[-1][0], progress_msg]
        for ui_update in update_ui(chatbot=chatbot, history=history):
            yield ui_update
        raise creation_error

    if not stream:
        # 该分支仅适用于不支持stream的o1模型，其他情形一律不适用
        yield from handle_o1_model_special(response, inputs, llm_kwargs, chatbot, history)
        return

    if stream:
        reach_termination = False   # 处理一些 new-api 的奇葩异常
        gpt_replying_buffer = ""
        is_head_of_the_stream = True
        stream_response =  response.iter_lines()
        while True:
            try:
                chunk = next(stream_response)
            except StopIteration:
                # 非OpenAI官方接口的出现这样的报错，OpenAI和API2D不会走这里
                chunk_decoded = chunk.decode()
                error_msg = chunk_decoded
                # 首先排除一个one-api没有done数据包的第三方Bug情形
                if len(gpt_replying_buffer.strip()) > 0 and len(error_msg) == 0:
                    yield from update_ui(chatbot=chatbot, history=history, msg="检测到有缺陷的接口，建议选择更稳定的接口。")
                    if not reach_termination:
                        reach_termination = True
                        log_chat(llm_model=llm_kwargs["llm_model"], input_str=inputs, output_str=gpt_replying_buffer)
                    break
                # 其他情况，直接返回报错
                chatbot, history = handle_error(inputs, llm_kwargs, chatbot, history, chunk_decoded, error_msg)
                yield from update_ui(chatbot=chatbot, history=history, msg="接口返回了错误:" + chunk.decode()) # 刷新界面
                return

            # 提前读取一些信息 （用于判断异常）
            chunk_decoded, chunkjson, has_choices, choice_valid, has_content, has_role = decode_chunk(chunk)

            if is_head_of_the_stream and (r'"object":"error"' not in chunk_decoded) and (r"content" not in chunk_decoded):
                # 数据流的第一帧不携带content
                is_head_of_the_stream = False; continue

            if "error" in chunk_decoded: logger.error(f"接口返回了未知错误: {chunk_decoded}")

            if chunk:
                try:
                    if has_choices and not choice_valid:
                        # 一些垃圾第三方接口的出现这样的错误
                        continue
                    if ('data: [DONE]' not in chunk_decoded) and len(chunk_decoded) > 0 and (chunkjson is None):
                        # 传递进来一些奇怪的东西
                        raise ValueError(f'无法读取以下数据，请检查配置。\n\n{chunk_decoded}')
                    # 前者是API2D & One-API的结束条件，后者是OPENAI的结束条件
                    one_api_terminate = ('data: [DONE]' in chunk_decoded)
                    openai_terminate = (has_choices) and (len(chunkjson['choices'][0]["delta"]) == 0)
                    if one_api_terminate or openai_terminate:
                        is_termination_certain = False
                        if one_api_terminate: is_termination_certain = True # 抓取符合规范的结束条件
                        elif (has_choices) and (chunkjson['choices'][0].get('finish_reason', 'null') == 'stop'): is_termination_certain = True # 抓取符合规范的结束条件
                        if is_termination_certain:
                            reach_termination = True
                            log_chat(llm_model=llm_kwargs["llm_model"], input_str=inputs, output_str=gpt_replying_buffer)
                            break # 对于符合规范的接口，这里可以break
                        else:
                            continue # 对于不符合规范的接口，这里需要继续
                    # 到这里，我们已经可以假定必须包含choice了
                    try:
                        status_text = f"finish_reason: {chunkjson['choices'][0].get('finish_reason', 'null')}"
                    except:
                        logger.error(f"一些第三方接口出现这样的错误，兼容一下吧: {chunk_decoded}")
                    # 处理数据流的主体
                    if has_content:
                        # 正常情况
                        gpt_replying_buffer = gpt_replying_buffer + chunkjson['choices'][0]["delta"]["content"]
                    elif has_role:
                        # 一些第三方接口的出现这样的错误，兼容一下吧
                        continue
                    else:
                        # 至此已经超出了正常接口应该进入的范围，一些第三方接口会出现这样的错误
                        if chunkjson['choices'][0]["delta"].get("content", None) is None:
                            logger.error(f"一些第三方接口出现这样的错误，兼容一下吧: {chunk_decoded}")
                            continue
                        gpt_replying_buffer = gpt_replying_buffer + chunkjson['choices'][0]["delta"]["content"]

                    history[-1] = gpt_replying_buffer
                    chatbot[-1] = (history[-2], history[-1])
                    if time.time() - previous_ui_reflesh_time > ui_reflesh_min_interval:
                        yield from update_ui(chatbot=chatbot, history=history, msg=status_text) # 刷新界面
                        previous_ui_reflesh_time = time.time()
                except Exception as e:
                    yield from update_ui(chatbot=chatbot, history=history, msg="Json解析不合常规") # 刷新界面
                    chunk = get_full_error(chunk, stream_response)
                    chunk_decoded = chunk.decode()
                    error_msg = chunk_decoded
                    chatbot, history = handle_error(inputs, llm_kwargs, chatbot, history, chunk_decoded, error_msg)
                    logger.error(error_msg)
                    yield from update_ui(chatbot=chatbot, history=history, msg="Json解析异常" + error_msg) # 刷新界面
                    return
        yield from update_ui(chatbot=chatbot, history=history, msg="完成") # 刷新界面
        return  # return from stream-branch

def handle_o1_model_special(response, inputs, llm_kwargs, chatbot, history):
    try:
        chunkjson = json.loads(response.content.decode())
        gpt_replying_buffer = chunkjson['choices'][0]["message"]["content"]
        log_chat(llm_model=llm_kwargs["llm_model"], input_str=inputs, output_str=gpt_replying_buffer)
        history[-1] = gpt_replying_buffer
        chatbot[-1] = (history[-2], history[-1])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    except Exception as e:
        yield from update_ui(chatbot=chatbot, history=history, msg="Json解析异常" + response.text) # 刷新界面

def handle_error(inputs, llm_kwargs, chatbot, history, chunk_decoded, error_msg):
    from request_llms.bridge_all import model_info
    openai_website = ' 请登录OpenAI查看详情 https://platform.openai.com/signup'
    if "reduce the length" in error_msg:
        if len(history) >= 2: history[-1] = ""; history[-2] = "" # 清除当前溢出的输入：history[-2] 是本次输入, history[-1] 是本次输出
        history = clip_history(inputs=inputs, history=history, tokenizer=model_info[llm_kwargs['llm_model']]['tokenizer'],
                                               max_token_limit=(model_info[llm_kwargs['llm_model']]['max_token'])) # history至少释放二分之一
        chatbot[-1] = (chatbot[-1][0], "[Local Message] Reduce the length. 本次输入过长, 或历史数据过长. 历史缓存数据已部分释放, 您可以请再次尝试. (若再次失败则更可能是因为输入过长.)")
    elif "does not exist" in error_msg:
        chatbot[-1] = (chatbot[-1][0], f"[Local Message] Model {llm_kwargs['llm_model']} does not exist. 模型不存在, 或者您没有获得体验资格.")
    elif "Incorrect API key" in error_msg:
        chatbot[-1] = (chatbot[-1][0], "[Local Message] Incorrect API key. OpenAI以提供了不正确的API_KEY为由, 拒绝服务. " + openai_website)
    elif "exceeded your current quota" in error_msg:
        chatbot[-1] = (chatbot[-1][0], "[Local Message] You exceeded your current quota. OpenAI以账户额度不足为由, 拒绝服务." + openai_website)
    elif "account is not active" in error_msg:
        chatbot[-1] = (chatbot[-1][0], "[Local Message] Your account is not active. OpenAI以账户失效为由, 拒绝服务." + openai_website)
    elif "associated with a deactivated account" in error_msg:
        chatbot[-1] = (chatbot[-1][0], "[Local Message] You are associated with a deactivated account. OpenAI以账户失效为由, 拒绝服务." + openai_website)
    elif "API key has been deactivated" in error_msg:
        chatbot[-1] = (chatbot[-1][0], "[Local Message] API key has been deactivated. OpenAI以账户失效为由, 拒绝服务." + openai_website)
    elif "bad forward key" in error_msg:
        chatbot[-1] = (chatbot[-1][0], "[Local Message] Bad forward key. API2D账户额度不足.")
    elif "Not enough point" in error_msg:
        chatbot[-1] = (chatbot[-1][0], "[Local Message] Not enough point. API2D账户点数不足.")
    else:
        from toolbox import regular_txt_to_markdown
        tb_str = '```\n' + trimmed_format_exc() + '```'
        chatbot[-1] = (chatbot[-1][0], f"[Local Message] 异常 \n\n{tb_str} \n\n{regular_txt_to_markdown(chunk_decoded)}")
    return chatbot, history

def generate_payload(inputs:str, llm_kwargs:dict, history:list, system_prompt:str, image_base64_array:list=[], has_multimodal_capacity:bool=False, stream:bool=True):
    """
    整合所有信息，选择LLM模型，生成http请求，为发送请求做准备
    """
    from request_llms.bridge_all import model_info

    if not is_any_api_key(llm_kwargs['api_key']):
        raise AssertionError("你提供了错误的API_KEY。\n\n1. 临时解决方案：直接在输入区键入api_key，然后回车提交。\n\n2. 长效解决方案：在config.py中配置。")

    if llm_kwargs['llm_model'].startswith('vllm-'):
        api_key = 'no-api-key'
    else:
        api_key = select_api_key(llm_kwargs['api_key'], llm_kwargs['llm_model'])

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    if API_ORG.startswith('org-'): headers.update({"OpenAI-Organization": API_ORG})
    if llm_kwargs['llm_model'].startswith('azure-'):
        headers.update({"api-key": api_key})
        if llm_kwargs['llm_model'] in AZURE_CFG_ARRAY.keys():
            azure_api_key_unshared = AZURE_CFG_ARRAY[llm_kwargs['llm_model']]["AZURE_API_KEY"]
            headers.update({"api-key": azure_api_key_unshared})

    if has_multimodal_capacity:
        # 当以下条件满足时，启用多模态能力：
        # 1. 模型本身是多模态模型（has_multimodal_capacity）
        # 2. 输入包含图像（len(image_base64_array) > 0）
        # 3. 历史输入包含图像（ any([contain_base64(h) for h in history]) ）
        enable_multimodal_capacity = (len(image_base64_array) > 0) or any([contain_base64(h) for h in history])
    else:
        enable_multimodal_capacity = False

    conversation_cnt = len(history) // 2
    openai_disable_system_prompt = model_info[llm_kwargs['llm_model']].get('openai_disable_system_prompt', False)

    if openai_disable_system_prompt:
        messages = [{"role": "user", "content": system_prompt}]
    else:
        messages = [{"role": "system", "content": system_prompt}]

    if not enable_multimodal_capacity:
        # 不使用多模态能力
        if conversation_cnt:
            for index in range(0, 2*conversation_cnt, 2):
                what_i_have_asked = {}
                what_i_have_asked["role"] = "user"
                what_i_have_asked["content"] = remove_image_if_contain_base64(history[index])
                what_gpt_answer = {}
                what_gpt_answer["role"] = "assistant"
                what_gpt_answer["content"] = remove_image_if_contain_base64(history[index+1])
                if what_i_have_asked["content"] != "":
                    if what_gpt_answer["content"] == "": continue
                    if what_gpt_answer["content"] == timeout_bot_msg: continue
                    messages.append(what_i_have_asked)
                    messages.append(what_gpt_answer)
                else:
                    messages[-1]['content'] = what_gpt_answer['content']
        what_i_ask_now = {}
        what_i_ask_now["role"] = "user"
        what_i_ask_now["content"] = inputs
        messages.append(what_i_ask_now)
    else:
        # 多模态能力
        if conversation_cnt:
            for index in range(0, 2*conversation_cnt, 2):
                what_i_have_asked = {}
                what_i_have_asked["role"] = "user"
                what_i_have_asked["content"] = append_image_if_contain_base64(history[index])
                what_gpt_answer = {}
                what_gpt_answer["role"] = "assistant"
                what_gpt_answer["content"] = append_image_if_contain_base64(history[index+1])
                if what_i_have_asked["content"] != "":
                    if what_gpt_answer["content"] == "": continue
                    if what_gpt_answer["content"] == timeout_bot_msg: continue
                    messages.append(what_i_have_asked)
                    messages.append(what_gpt_answer)
                else:
                    messages[-1]['content'] = what_gpt_answer['content']
        what_i_ask_now = {}
        what_i_ask_now["role"] = "user"
        what_i_ask_now["content"] = []
        what_i_ask_now["content"].append({
            "type": "text",
            "text": inputs
        })
        for image_base64 in image_base64_array:
            what_i_ask_now["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            })
        messages.append(what_i_ask_now)


    model = llm_kwargs['llm_model']
    if llm_kwargs['llm_model'].startswith('api2d-'):
        model = llm_kwargs['llm_model'][len('api2d-'):]
    if llm_kwargs['llm_model'].startswith('aioagi-'):
        model = llm_kwargs['llm_model'][len('aioagi-'):]
        model, _ = read_one_api_model_name(model)
    if llm_kwargs['llm_model'].startswith('vllm-'):
        model = llm_kwargs['llm_model'][len('vllm-'):]
        model, _ = read_one_api_model_name(model)
    if model == "gpt-3.5-random": # 随机选择, 绕过openai访问频率限制
        model = random.choice([
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-1106",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-3.5-turbo-0301",
        ])

    payload = {
        "model": model,
        "messages": messages,
        "temperature": llm_kwargs['temperature'],  # 1.0,
        "top_p": llm_kwargs['top_p'],  # 1.0,
        "n": 1,
        "stream": stream,
    }
    openai_force_temperature_one = model_info[llm_kwargs['llm_model']].get('openai_force_temperature_one', False)
    if openai_force_temperature_one:
        payload.pop('temperature')
    return headers,payload

