# -*- coding: utf-8 -*-
"""
MCP服务器静态工具函数
用于读取和处理mcp_servers.json文件，提供服务器展示功能
"""

import os
import json
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime


def load_mcp_server_data(file_path: str = "mcp_servers.json") -> Dict[str, Any]:
    """加载mcp_servers.json文件数据

    Args:
        file_path: mcp_servers.json文件路径，默认为当前目录下的文件

    Returns:
        包含服务器信息的字典，如果文件不存在或读取失败则返回空数据结构
    """

    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, file_path)

    try:
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "available_servers": {}
            }
    except Exception as e:
        return {
            "available_servers": {}
        }


def format_server_message(mcp_data: Dict[str, Any]) -> str:
    """格式化服务器信息为可显示的消息

    Args:
        mcp_data: 从mcp_servers.json加载的数据

    Returns:
        格式化后的消息字符串
    """
    if not mcp_data:
        return "⚠️ 无法获取学术智能体（Academic Agents）服务信息"

    # 构建服务消息
    status_msg = f""
    # 显示可用的服务器
    available_servers = mcp_data.get("available_servers", {})
    if available_servers:
        status_msg += "🚀 **可用的学术智能体（Academic Agents）服务**:\n"
        for key, server in available_servers.items():
            status_msg += f"\n• ✅ **{server.get('name', key)}**: {server.get('description', '无描述')}\n"
    else:
        status_msg += "❌ **当前没有可用的学术智能体（Academic Agents）服务**\n"

    # 显示不可用的服务器
    unavailable_servers = mcp_data.get("unavailable_servers", {})
    if unavailable_servers:
        status_msg += f"\n\n🚀 **不可用的学术智能体（Academic Agents）服务** :\n"
        for key, server in unavailable_servers.items():
            status_msg += f"\n• ❌ **{server.get('name', key)}**: 服务暂不可用，请联系管理员(QQ群 1030022463 | 微信群 搜索AIOAGI)维护。\n"

    return status_msg


def get_mcp_servers_for_config() -> List[Dict[str, Any]]:
    """获取可用MCP服务器的配置信息，用于系统配置

    Returns:
        可用MCP服务器的配置列表，格式适用于qwen-agent等框架
    """
    mcp_data = load_mcp_server_data()
    available_servers = mcp_data.get("available_servers", {})

    if not available_servers:
        return []

    # 转换为qwen-agent需要的格式
    mcp_servers = {}
    for key, server in available_servers.items():
        mcp_servers[server.get('name', key)] = {
            "name": server.get('name', key),
            "url": server.get('url', ''),
            "headers": server.get('headers', {}),
            "description": server.get('description', '')
        }

    return [{"mcpServers": mcp_servers}] if mcp_servers else []



def clean_html_content(text: str) -> str:
    """
    清理HTML内容，提取纯文本
    主要用于从chatbot历史记录中清理HTML标签和隐藏内容，减少模型token消耗

    Args:
        text: 包含HTML的文本内容

    Returns:
        清理后的纯文本内容
    """
    if not text or not isinstance(text, str):
        return text or ""

    # 移除隐藏的div元素（如raw_text和message_tail）
    text = re.sub(r'<div[^>]*style="display:none"[^>]*>.*?</div>', '', text, flags=re.DOTALL)

    # 移除<script>和<style>标签及其内容
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)

    # 移除所有HTML标签
    text = re.sub(r'<[^>]+>', '', text)

    # 清理HTML实体
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")

    # 清理多余的空白字符
    text = re.sub(r'\s+', ' ', text).strip()

    return text