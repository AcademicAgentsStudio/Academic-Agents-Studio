# -*- coding: utf-8 -*-
"""
智能体MCP管理器
负责智能体MCP服务的调用和管理
支持多用户会话隔离
"""

import asyncio
import json
import sys
import os
from typing import Dict, List, Optional, Any, Generator
from qwen_agent.agents import Assistant
from mcp_servers.mcp_config import mcp_config_manager, MCPServerConfig
from toolbox import get_conf
import asyncio
from mcp.client.sse import sse_client
from mcp import ClientSession


import time
# 确保Linux系统下的正确编码处理
if sys.platform.startswith('linux'):
    # 设置默认编码为UTF-8
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class MCPManager:
    """智能体MCP服务管理器 - 支持多用户会话隔离"""

    def __init__(self):
        # 移除全局状态，改为基于用户会话的状态管理
        pass

    def _get_user_id(self, chatbot) -> str:
        """从chatbot中获取用户ID，用于会话隔离"""
        if chatbot and hasattr(chatbot, '_cookies'):

            # 尝试获取用户ID，如果没有则创建一个基于cookies的唯一标识
            user_id = chatbot._cookies.get('user_id')
            if not user_id:
                import hashlib
                import time
                api_key = chatbot._cookies.get('api_key', '')
                timestamp = str(time.time())
                user_id = hashlib.md5(f"{api_key}_{timestamp}".encode()).hexdigest()[:16]
                chatbot._cookies['user_id'] = user_id
            return user_id
        else:
            return "default_user"

    def is_enabled(self, chatbot) -> bool:
        """检查指定用户会话的MCP是否启用"""
        if not chatbot or not hasattr(chatbot, '_cookies'):
            return False
        return chatbot._cookies.get('mcp_enabled', False)

    def enable_mcp(self, chatbot, enabled: bool = True):
        """启用或禁用指定用户会话的MCP功能"""
        if not chatbot or not hasattr(chatbot, '_cookies'):
            return False

        chatbot._cookies['mcp_enabled'] = enabled
        if not enabled:
            # 清理该用户的智能体MCP服务
            chatbot._cookies.pop('mcp_bot_created', None)
        return True

    def get_llm_config(self, chatbot=None) -> Dict[str, Any]:
        """获取LLM配置"""
        try:
            # 优先从chatbot cookies获取用户当前使用的API密钥
            if chatbot and hasattr(chatbot, '_cookies') and chatbot._cookies is not None and 'api_key' in chatbot._cookies:
                api_key = chatbot._cookies['api_key']
            else:
                # 回退到配置文件中的API密钥
                api_key = get_conf('API_KEY')

            # 从项目配置获取LLM设置
            try:
                llm_model = chatbot._cookies['llm_model']
                if llm_model.startswith('aioagi-'):
                    llm_model = llm_model.replace("aioagi-", "", 1)
            except Exception as e:
                llm_model = "gpt-5-mini"

            try:
                api_base = get_conf('API_URL_REDIRECT', {}).get(llm_model, "")
            except Exception as e:
                api_base = "https://api.aiearth.vip/v1"

            # 默认配置
            llm_cfg = {
                "model": llm_model,
                "model_server": api_base,
                "api_key": api_key
            }

            return llm_cfg

        except Exception as e:
            # 返回默认配置
            return {
                "model": "gpt-5-mini",
                "model_server": "https://api.aiearth.vip/v1",
                "api_key": get_conf('API_KEY')
            }

    def create_agent_bot(self, chatbot, mcp_servers=None, system_message: str = None) -> Optional[Assistant]:
        """为指定用户会话创建支持MCP的智能体bot"""
        if not self.is_enabled(chatbot):
            return None

        try:
            if mcp_servers:
                mcp_tools = mcp_servers
            else:
                mcp_tools = mcp_config_manager.get_servers_for_qwen_agent(test_connection=True)
            if not mcp_tools:
                # 如果没有可连接的服务器，尝试使用所有启用的服务器
                mcp_tools = mcp_config_manager.get_servers_for_qwen_agent(test_connection=False)
                if not mcp_tools:
                    return None

            # 获取用户特定的LLM配置
            llm_cfg = self.get_llm_config(chatbot)
            user_id = self._get_user_id(chatbot)

            # 默认系统消息
            if not system_message:
                # 获取实际可用的服务器名称
                available_servers = []
                if mcp_tools and mcp_tools[0].get("mcpServers"):
                    available_servers = list(mcp_tools[0]["mcpServers"].keys())

                if available_servers:
                    system_message = (
                        f'你是一个智能助手，可以调用以下工具来帮助用户：{", ".join(available_servers)}。'
                        '请根据用户的需求智能选择合适的工具进行调用，并对结果进行解释和总结。'
                    )
                else:
                    system_message = '你是一个智能助手，为用户提供帮助。'

            # 创建用户专属的智能体
            bot = Assistant(
                llm=llm_cfg,
                name=f'学术智能体（Academic Agents）- {user_id}',
                description='你的学术智能助手',
                system_message=system_message,
                function_list=mcp_tools,
            )

            chatbot._cookies['mcp_bot_created'] = True

            return bot

        except Exception as e:
            # 尝试创建不带MCP工具的基础智能体bot
            try:
                llm_cfg = self.get_llm_config(chatbot)
                user_id = self._get_user_id(chatbot)

                bot = Assistant(
                    llm=llm_cfg,
                    name=f'学术智能体（Academic Agents）- {user_id}',
                    description='你的学术智能助手',
                    system_message='你是一个学术智能体（Academic Agents）助手，为用户提供帮助。',
                    function_list=[],  # 空的工具列表
                )

                return bot
            except Exception as e2:
                return None

    def chat_with_mcp(self, user_input: str, history: List[Dict[str, str]] = None, chatbot=None, bot=None) -> Generator[str, None, None]:
        """与MCP智能体对话 - 使用线程处理智能体交互，主线程保持前端连接"""
        if not self.is_enabled(chatbot):
            yield "学术智能体功能未启用，请先点击'学术智能体（Academic Agents）'按钮开启。"
            return

        try:
            if not bot:
                yield "学术智能体（Academic Agents）连接失败，请重试/联系管理员(QQ群 1030022463 | 微信群 搜索AIOAGI)。"
                return

            # 构建消息历史
            messages = []
            if history:
                for item in history:
                    if item.get('role') == 'user':
                        messages.append({'role': 'user', 'content': item.get('content', '')})
                    elif item.get('role') == 'assistant':
                        messages.append({'role': 'assistant', 'content': item.get('content', '')})

            # 添加当前用户输入
            messages.append({'role': 'user', 'content': user_input})

            # 使用线程获取智能体交互结果，主线程负责保持连接
            import threading
            import queue

            # 用于线程间通信的队列
            result_queue = queue.Queue()
            error_queue = queue.Queue()

            # 转换工具调用返回结果格式
            async def format_tool_result(result_text: str) -> str:
                """
                格式化工具返回结果

                Args:
                    result_text: 需要格式化的原始结果文本

                Returns:
                    格式化后的HTML内容
                """
                async with sse_client(
                        "https://academicformatter.freemcps.aiearth.vip/sse",
                        headers={"Authorization": f"Bearer aioagi.tech"}
                ) as streams:
                    async with ClientSession(*streams) as session:
                        await session.initialize()

                        # 调用格式化工具
                        result = await session.call_tool(
                            'format_tool_result',  # 工具名称
                            {
                                'result': result_text  # 需要格式化的文本
                            }
                        )

                        return result.content[0].text



            def agent_worker():
                """智能体工作线程"""
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    response_parts = []
                    for response in bot.run(messages):
                        if isinstance(response, list):
                            item = response[-1]
                            if isinstance(item, dict):# and item.get('role') == 'function':
                                role = item.get('role')
                                content = item.get('content', '')
                                if role == 'function':
                                    content_md = loop.run_until_complete(format_tool_result(content))
                                    content = "🛠️" + "工具调用结果：<br>" + content_md
                                    response_parts.append(content)
                                    result_queue.put(('data', content))
                                elif role == 'assistant' and item.get('function_call'):
                                    content = '⏳工具调用：' + item.get('function_call')['name']
                                    response_parts.append(content)
                                    result_queue.put(('data', content))
                                elif role == 'assistant' and content:
                                    response_parts.append(content)
                                    result_queue.put(('data', content))
                        elif isinstance(response, dict) and 'content' in response:
                            content = response['content']
                            if content:
                                response_parts.append(content)
                                result_queue.put(('data', content))

                    # 如果没有返回内容，提供默认回复
                    if not response_parts:
                        result_queue.put(('data', "抱歉，请重试/联系管理员(QQ群 1030022463 | 微信群 搜索AIOAGI)。"))

                    result_queue.put(('done', None))
                except Exception as e:
                    error_queue.put(e)
                    result_queue.put(('done', None))

            # 启动智能体工作线程
            worker_thread = threading.Thread(target=agent_worker, daemon=True)
            worker_thread.start()

            # 主线程显示进度
            start_time = time.time()
            last_progress_time = start_time
            progress_symbols = ["🤖", "🖥️", "🔍"]
            symbol_index = 0
            max_wait_time = 120  # 最多等待120秒

            while True:
                current_time = time.time()

                # 检查是否有错误
                if not error_queue.empty():
                    error = error_queue.get()
                    # 确保错误信息的正确编码处理
                    try:
                        error_str = str(error)
                        if any(ord(char) > 127 for char in error_str):
                            error_str = error_str.encode('utf-8', errors='replace').decode('utf-8')
                    except UnicodeError:
                        error_str = repr(error)

                    error_msg = f"学术智能体（Academic Agents）调用出错: {error_str}，请重试/联系管理员(QQ群 1030022463 | 微信群 搜索AIOAGI)。"
                    yield error_msg
                    break

                # 检查是否有新的响应数据
                try:
                    msg_type, data = result_queue.get_nowait()
                    if msg_type == 'data':
                        # 收到数据，直接yield给前端
                        yield data
                        start_time = time.time()#重置处理时间 trick
                    elif msg_type == 'done':
                        break
                except queue.Empty:
                    if current_time - last_progress_time >= 1.0:  # 每1秒更新一次进度符号
                        symbol_index = (symbol_index + 1) % len(progress_symbols)
                        elapsed = int(current_time - start_time)

                        progress_msg = f"{progress_symbols[symbol_index]} 学术智能体（Academic Agents）思考中...({elapsed}s)"
                        yield progress_msg
                        last_progress_time = current_time

                        if elapsed >= max_wait_time:
                            yield f"很抱歉，🤖学术智能体（Academic Agents）服务响应超时，请重试/联系管理员(QQ群 1030022463 | 微信群 搜索AIOAGI)。"
                            break

        except Exception as e:
            # 确保错误信息的正确编码处理
            try:
                error_str = str(e)
                # 如果包含非ASCII字符，确保正确编码
                if any(ord(char) > 127 for char in error_str):
                    error_str = error_str.encode('utf-8', errors='replace').decode('utf-8')
            except UnicodeError:
                error_str = repr(e)

            error_msg = f"学术智能体（Academic Agents）调用出错: {error_str}，请重试/联系管理员(QQ群 1030022463 | 微信群 搜索AIOAGI)。"
            yield error_msg

    def get_available_tools(self, chatbot=None) -> List[Dict[str, Any]]:
        """获取可用的MCP工具列表"""
        if not self.is_enabled(chatbot):
            return []

        return mcp_config_manager.get_server_list()

    def get_server_status(self, chatbot=None) -> Dict[str, Any]:
        """获取所有MCP服务器的状态信息"""
        if not self.is_enabled(chatbot):
            return {"enabled": False, "servers": []}

        enabled_servers = mcp_config_manager.get_enabled_servers()
        server_status = []

        for key, config in enabled_servers.items():
            # 测试连接状态
            is_available = mcp_config_manager._test_server_connection(config)
            server_status.append({
                "key": key,
                "name": config.name,
                "description": config.description,
                "url": config.url,
                "enabled": config.enabled,
                "available": is_available,
                "status": "可用" if is_available else "不可用"
            })

        total_enabled = len(enabled_servers)
        available_count = sum(1 for server in server_status if server["available"])

        return {
            "enabled": True,
            "total_enabled": total_enabled,
            "available_count": available_count,
            "servers": server_status
        }

    def test_mcp_connection(self, server_key: str, chatbot=None) -> Dict[str, Any]:
        """测试MCP服务器连接"""
        try:
            config = mcp_config_manager.get_server_config(server_key)
            if not config:
                return {"success": False, "message": "服务器配置不存在"}

            # 创建临时智能体进行测试，使用用户的API密钥
            llm_cfg = self.get_llm_config(chatbot)
            test_tools = [{"mcpServers": {config.name: {"url": config.url, "headers": config.headers}}}]

            bot = Assistant(
                llm=llm_cfg,
                name='测试智能体',
                description='用于测试MCP连接',
                system_message='你是一个测试智能体，用于验证MCP工具连接。',
                function_list=test_tools,
            )

            # 发送简单的测试消息
            test_message = "请列出你可用的工具"
            messages = [{'role': 'user', 'content': test_message}]

            # 尝试调用
            responses = list(bot.run(messages))
            if responses:
                return {"success": True, "message": "连接成功"}
            else:
                return {"success": False, "message": "连接超时或无响应"}

        except Exception as e:
            return {"success": False, "message": f"连接失败: {str(e)}"}

    def get_user_mcp_status(self, chatbot) -> Dict[str, Any]:
        """获取用户的MCP状态信息"""
        if not chatbot or not hasattr(chatbot, '_cookies'):
            return {
                "enabled": False,
                "user_id": "未知",
                "api_key_source": "默认配置",
                "bot_created": False
            }

        user_id = self._get_user_id(chatbot)
        enabled = self.is_enabled(chatbot)
        api_key_source = "用户提供" if chatbot._cookies is not None and 'api_key' in chatbot._cookies else "默认配置"
        bot_created = chatbot._cookies.get('mcp_bot_created', False) if chatbot._cookies is not None else False

        return {
            "enabled": enabled,
            "user_id": user_id,
            "api_key_source": api_key_source,
            "bot_created": bot_created
        }

# 全局MCP管理器实例
mcp_manager = MCPManager()