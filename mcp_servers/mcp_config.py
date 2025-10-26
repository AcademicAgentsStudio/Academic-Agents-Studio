# -*- coding: utf-8 -*-
"""
智能体MCP配置管理
支持配置多个智能体MCP服务器，用于智能体功能扩展
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

@dataclass
class MCPServerConfig:
    """智能体MCP服务器配置"""
    name: str
    url: str
    headers: Dict[str, str]
    description: str = ""
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPServerConfig':
        return cls(**data)

class MCPConfigManager:
    """智能体MCP配置管理器"""

    def __init__(self):
        self.config_file = "mcp_servers/mcp_servers.json"
        self._default_configs = self._get_default_configs()
        self._load_configs()

    def _get_default_configs(self) -> Dict[str, MCPServerConfig]:
        """获取默认的智能体MCP服务器配置"""

        return {
            "FreeAcademicWrite": MCPServerConfig(
                name="学术智能体（Academic Agents）免费学术写作服务",
                url="https://academicwrite.freemcps.aiearth.vip/sse",
                headers={"Authorization": f"Bearer aioagi.tech"},
                description="学术智能体（Academic Agents）是一个专为学术研究和论文写作设计的智能助手平台，为研究人员和学者提供全方位的学术写作支持，集成四大核心功能：学术语料润色支持中文学术文本的语法优化、句式改进和可读性提升；语法错误检查提供英文学术文本的精确语法和拼写校对；智能翻译具备自动语言识别能力，可准确翻译各种语言的学术内容；学术英中互译专门针对学术场景，运用自然语言处理技术和修辞学知识，在英文和中文之间进行高质量的双向翻译。",
                enabled=True
            ),
            "FreeWebSearch": MCPServerConfig(
                name="学术智能体（Academic Agents）免费网络搜索服务",
                url="https://websearch.freemcps.aiearth.vip/sse",
                headers={"Authorization": f"Bearer aioagi.tech"},
                description="搜索判定等多种检索模型及语义理解，串接专业搜索工程框架及各类型实时信息检索工具，提供实时互联网全栈信息检索，提升 LLM 回答准确性及时效性。",
                enabled=True
            ),
            "FreeAcademicChart": MCPServerConfig(
                name="学术智能体（Academic Agents）免费学术图表可视化服务",
                url="https://academicchart.freemcps.aiearth.vip/sse",
                headers={"Authorization": f"Bearer aioagi.tech"},
                description="支持生成多种类型的图表并返回图表 url，包括：条形图、折线图、饼图、环状图、雷达图、极坐标区域图、散点图、气泡图、径向仪表图、速度表；可定制图表配置，包括：标签、数据和颜色。",
                enabled=True
            )
        }

    def _load_configs(self):
        """加载配置文件"""
        self.servers = {}

        # 首先加载默认配置
        for key, config in self._default_configs.items():
            self.servers[key] = config

        # 尝试从文件加载用户配置
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)['available_servers']
                for key, config_data in data.items():
                    self.servers[key] = MCPServerConfig.from_dict(config_data)

    def save_configs(self):
        """保存配置到文件"""
        data = {}
        for key, config in self.servers.items():
            data[key] = config.to_dict()

        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_enabled_servers(self) -> Dict[str, MCPServerConfig]:
        """获取所有启用的服务器配置"""
        return {key: config for key, config in self.servers.items() if config.enabled}

    def get_server_config(self, server_key: str) -> Optional[MCPServerConfig]:
        """获取指定服务器的配置"""
        return self.servers.get(server_key)

    def add_server(self, key: str, config: MCPServerConfig):
        """添加新的服务器配置"""
        self.servers[key] = config
        self.save_configs()

    def update_server(self, key: str, config: MCPServerConfig):
        """更新服务器配置"""
        if key in self.servers:
            self.servers[key] = config
            self.save_configs()

    def remove_server(self, key: str):
        """删除服务器配置"""
        if key in self.servers and key not in self._default_configs:
            del self.servers[key]
            self.save_configs()

    def enable_server(self, key: str, enabled: bool = True):
        """启用或禁用服务器"""
        if key in self.servers:
            self.servers[key].enabled = enabled
            self.save_configs()

    def get_servers_for_qwen_agent(self, test_connection: bool = True) -> List[Dict[str, Any]]:
        """获取适用于智能体的MCP服务器配置格式

        Args:
            test_connection: 是否测试连接，如果为True，只返回可连接的服务器
        """
        enabled_servers = self.get_enabled_servers()
        if not enabled_servers:
            return []

        mcp_servers = {}

        if test_connection:
            for key, config in enabled_servers.items():
                if self._test_server_connection(config):
                    mcp_servers[config.name] = {
                        "name": config.name,
                        "url": config.url,
                        "headers": config.headers,
                        "description": config.description
                    }
        else:
            # 添加所有启用的服务器（不测试连接）
            for key, config in enabled_servers.items():
                mcp_servers[config.name] = {
                    "name": config.name,
                    "url": config.url,
                    "headers": config.headers,
                    "description": config.description
                }

        if not mcp_servers:
            return []

        return [{"mcpServers": mcp_servers}]

    def _test_server_connection(self, config: MCPServerConfig) -> bool:
        """测试单个MCP服务器的连接状态"""
        import requests
        import time

        # 发送一个简单的HEAD请求测试连接
        response = requests.head(
            config.url,
            headers=config.headers,
            timeout=5  # 5秒超时
        )
        return response.status_code in [200, 204, 405]  # 405表示方法不允许但服务可达

    def get_server_list(self) -> List[Dict[str, Any]]:
        """获取服务器列表，用于前端显示"""
        return [
            {
                "key": key,
                "name": config.name,
                "description": config.description,
                "enabled": config.enabled,
                "url": config.url
            }
            for key, config in self.servers.items()
        ]

# 全局MCP配置管理器实例
mcp_config_manager = MCPConfigManager()