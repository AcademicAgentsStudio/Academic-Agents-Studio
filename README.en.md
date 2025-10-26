<p align="right">
   <strong>Chinese</strong> | <a href="./docs/README.en.md">English</a>
</p>

<div align="center">

<img src="./docs/images/logo.png" width="120" />

# Academic Agents Studio

### 🤖 Next-Generation Academic AI Agent Application Service Platform

<p>
<strong>AI Agent-driven intelligent platform for the entire academic research workflow</strong><br>
Supports academic scenarios including paper writing, literature analysis, code interpretation, multilingual translation, and more.
</p>

[![Github][Github-image]][Github-url]
[![License][License-image]][License-url]
[![Python][Python-image]][Python-url]
[![Gradio][Gradio-image]][Gradio-url]
[![Stars][Stars-image]][Stars-url]

[Github-image]: https://img.shields.io/badge/GitHub-Repository-black?style=flat-square&logo=github
[License-image]: https://img.shields.io/badge/License-MIT-orange?style=flat-square
[Python-image]: https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python
[Gradio-image]: https://img.shields.io/badge/Gradio-Web%20UI-yellow?style=flat-square
[Stars-image]: https://img.shields.io/github/stars/AcademicAgentsStudio?style=flat-square

[Github-url]: https://github.com/AcademicAgentsStudio
[License-url]: https://github.com/AcademicAgentsStudio/blob/master/LICENSE
[Python-url]: https://www.python.org/
[Gradio-url]: https://gradio.app/
[Stars-url]: https://github.com/AcademicAgentsStudio/stargazers

</div>

---

## 🎯 Project Introduction

**Academic Agents Studio** is a next-generation academic AI agent platform for academic researchers, built on the <a href="https://github.com/QwenLM/Qwen-Agent">Qwen-Agent</a> framework and <a href="https://github.com/modelcontextprotocol">MCP (Model Context Protocol)</a> protocol, constructed upon the foundation of the <a href="https://github.com/binary-husky/gpt_academic">CAS Academic GPT</a> platform. It focuses on providing comprehensive AI agent-assisted services for academic researchers, educators, and students, integrating various academic-specific agent tools to significantly enhance research efficiency and quality.

### ✨ Core Features

- 🔬 **Academic Specialization**: Deeply optimized for academic scenarios, supporting multiple academic tasks
- 🌐 **Multi-Model Support**: Integrates mainstream AI models including GPT, Claude, Gemini, Deepseek, Qwen, and more
- 🤖 **Academic Agent Support**: Integrates advanced agent frameworks and service protocols, supports external tool calling and academic function expansion
- 📚 **Document Processing**: Intelligent processing of various formats including PDF, LaTeX, Markdown, and more
- 🎨 **User-Friendly Interface**: Newly designed tech-style interactive interface based on Gradio, supporting dark mode and multiple themes
- 🔧 **Highly Customizable**: Supports custom plugins and shortcuts to meet personalized needs
- 🚀 **Easy Deployment**: Supports local deployment, Docker deployment, and cloud deployment
- ⭐ **Online Experience**: Free online experience of the <a href="https://agents.aiearth.vip">beta version</a>, supporting the latest R&D features, 🙂 supports GPT, Claude and other base model series, feedback welcome!

### 🏗️ Technical Architecture
<p align="center">
    <img src="https://qianwen-res.oss-accelerate-overseas.aliyuncs.com/logo_qwen_agent.png" width="400"/>
<p>

#### 🤖 Agent System:

  - Agent Collaboration: Professional agent ecosystem built on Qwen-Agent framework
  - Modular Design: Agent services focus on specific domains, supporting flexible combination
  - Asynchronous Processing: Efficient asynchronous task processing mechanism
  - Context Management: Intelligent dialogue context and task state management

#### 🔧 MCP Service Integration:

  - Standardized Protocol: Tool integration based on Model Context Protocol
  - Extensible Architecture: Supports custom MCP server development
  - Tool Ecosystem: Rich preset tool services
  - Hot-plug Support: Dynamic loading and unloading of MCP services

## 🎓 **Academic Agents Studio** Academic Agent Features

<div align="center">

| Feature Category | Core Features | Description |
|---------|--------------|--------------------------------|
| 🏗️ **Agent Framework** | Qwen-Agent Integration | Built on advanced Qwen-Agent framework for professional agent ecosystem |
| | Modular Agents | Each agent focuses on specific domains, supporting flexible combination and task collaboration |
| | Asynchronous Task Processing | Efficient asynchronous task processing mechanism, supports parallel agent invocation |
| | Context Management | Intelligent dialogue context and task state management, maintaining session coherence |
| 🔌 **MCP Services** | Standardized Protocol | Standardized tool integration based on Model Context Protocol |
| | Extensible Architecture | Supports custom MCP server development and hot-plug deployment |
| | Rich Tool Ecosystem | Multiple pre-configured academic-specific MCP tool services |
| | Dynamic Service Management | Supports dynamic loading, unloading, and configuration updates of MCP services |
| 🤖 **Academic Agents** | External Tool Calling | Supports agent tools like chart visualization, map weather, web search, etc. |
| | Tool Call Visualization | Complete display of intermediate processes and execution results of tool calls |
| | Multi-user Isolation | Independent agent states and API keys for each user, ensuring privacy and security |
| | One-click Enablement | Quickly enable agent functions via the "Academic Agent" button |
| | Free and Open | Academic agent services are free and open for academic users |
| 🔄 **Interaction Flow** | Transparent Execution | Real-time display of agent reasoning process and tool selection logic |
| | Step Visualization | Complete display of each processing step from user input to final output |
| | Error Diagnostics | Detailed error information and debugging information for problem troubleshooting |
| | Execution Logging | Complete operation log records supporting traceback and analysis |
| 🎨 **Interface Optimization** | Visual Effects Optimization | Deep blue tech style, multi-layer shadow effects, real-time gradient border animations, highly technological |
| | Interaction Experience Enhancement | More detailed prompt information, adaptive text input, real-time status prompts and intelligent feedback |
| | Button Interaction Optimization | 3D visual button design, smooth state transitions and glow animations |

</div>

### 🔧 Inherited Features from CAS Academic GPT

Inherits basic component tools from the <a href="https://github.com/binary-husky/gpt_academic">CAS Academic GPT</a> project, providing essential basic functions for academic research:
<div align="center">

| Feature Category | Core Features | Description |
|---------|---------|------|
| 📄 **Document Processing** | PDF Parsing & Translation | One-click translation of academic papers, preserving format and formulas |
| | LaTeX Processing | Supports LaTeX paper polishing, translation, grammar checking |
| | Markdown Conversion | Intelligent conversion and formatting of Markdown documents |
| 🔍 **Academic Tools** | Arxiv Paper Assistant | Quick acquisition and translation of Arxiv papers |
| | Literature Review Generation | Generate comprehensive literature reviews based on multiple papers |
| | Code Interpretation & Analysis | Deep parsing of various programming language codes |
| 🎨 **Visualization** | Flowchart Generation | Supports Mermaid charts, mind maps, Gantt charts, etc. |
| | Formula Rendering | Visual rendering and editing of LaTeX formulas |
| 🔊 **Interaction Enhancement** | Voice Dialogue | Real-time voice input and TTS voice output |
| | Virtual Terminal | Natural language invocation of various plugin functions |
| 💫 **Interface Optimization** | Tech-style Input Area | Gradient background, frosted glass effect, dynamic border glow animation |
| | Smart Interaction | Multi-line input, file drag-and-drop, shortcut key prompts, status feedback |
| 🛠️ **Extensibility** | Plugin System | Rich plugin library and custom plugin support |
| | Theme Customization | Multiple interface themes and personalized settings |

</div>

## 🔄 Academic Agent Interaction Flow Visualization

<div align="center">

### Transparent Academic Agent Execution Process:
Academic Agents Studio provides complete academic agent interaction flow visualization, allowing users to clearly understand agent processing steps:

### **User Input Parsing**:
Intent recognition, task decomposition, MCP service parsing, tool matching.

### **Tool Calling Process**:
Real-time display of called tools and services, showing tool execution status and progress, complete request and response information.

### **Result Processing & Integration**:
Intelligent integration of tool results, formatting and visualization processing, final result generation and display.

</div>

## 🚀 Quick Start

### Environment Requirements

- **Python**: 3.9-3.12
- **Operating System**: Windows, Linux, macOS
- **Memory**: Recommended 4GB or more
- **Network**: Stable network connection required for accessing AI model APIs

### One-Click Installation (Recommended)

```bash
# Clone project
git clone https://github.com/AcademicAgentsStudio.git
cd AcademicAgentsStudio

# Install dependencies
pip install -r requirements.txt

# Configure API Key (in config.py)
# API_KEY = "your-api-key-here"

# Start application
python main.py
```

### Docker Deployment

```bash
# Pull image
docker pull aioagitech/academic_agents_studio:latest

# Run container (Quick Start)
docker run -it -p 7860:7860 --name academic_agents_studio aioagitech/academic_agents_studio:latest sh -c "cd /workspace && python main.py" /bin/bash

# The sh -c "cd /workspace && python main.py" part can be removed for users to manually enter the workspace folder and execute python main.py

# Run container (Set environment variables: Multiple environment variables under config.py can be set, here using WEB_PORT for network access port and API_KEY for model calling as examples)
docker run -it -p 16666:16666 --name academic_agents_studio -e WEB_PORT=16666 -e API_KEY="sk-8fK9m2pQ7xR4sT6yV3nW" aioagitech/academic_agents_studio:latest sh -c "cd /workspace && python main.py" /bin/bash
```

Access `http://localhost:7860` locally to use.

## 🤖 Academic Agent MCP Service Support

### 🛠️ Pre-configured Free Academic Agent MCP Services

Academic Agents Studio, based on the MCP (Model Context Protocol) protocol, pre-integrates the following professional academic agent free services, covering core needs of academic research:

| Service Name | Function Description | Core Capabilities | Usage Scenarios |
|---------|---------|---------|---------|
| **🎨 Academic Chart Visualization**<br>FreeAcademicChart | Professional academic data visualization solution | Supports 10+ chart types including bar charts, line charts, pie charts, donut charts, radar charts, etc.; Highly customizable labels, data, colors, and styles; Complies with academic publishing standards | Research data visualization, paper chart creation, academic report illustrations, data analysis display |
| **🔍 Web Search Service**<br>FreeWebSearch | Intelligent academic information retrieval and analysis system | Multi-model retrieval and semantic understanding; Real-time full-stack internet information retrieval; Professional search engineering framework integration; Improves answer accuracy and timeliness | Literature survey and review, tracking latest research trends, policy and regulation queries, background information collection |
| **✍️ Academic Writing Service**<br>FreeAcademicWrite | Professional academic text processing and optimization platform | Academic corpus polishing and grammar optimization; Intelligent translation and language recognition; Academic English-Chinese translation; Grammar error checking and spell checking | Paper writing and revision, academic report optimization, research proposal polishing, international journal submission preparation |
| **📝 Result Format Conversion**<br>FreeAcademicFormatter | Intelligent tool result format conversion and optimization | HTML formatting and Markdown conversion; Uses default large models for formatting processing; Optimizes front-end page visualization effects | Tool return result display, academic report content formatting, data visualization preprocessing |

### 🚀 Usage Methods

#### 1. **Enable Academic Agent Function**
```
Click the "Academic Agent" button in the interface
The system will automatically detect and configure all available free academic agent services
```

#### 2. **Start Smart Conversation**
```
After enabling, directly ask questions in the input box
AI will automatically select appropriate tools for calling
Real-time display of tool calling process and results
```

#### 3. **Example Conversation Scenarios**
```
🎨 Data Visualization:
"Help me generate a trend chart of AI paper publication numbers over the past five years"
"Create a pie chart showing research funding proportions across different disciplines"

🔍 Information Search:
"Search for the latest applications of deep learning in medical imaging"
"Find recent research on the impact of climate change on agriculture"

✍️ Text Processing:
"Polish this research methodology description"
"Translate this English abstract into Chinese"
"Check the grammar errors in this introduction"

📊 Format Conversion:
"Convert this data analysis result into a report-friendly format"
```

### ⚙️ Advanced Configuration & Extension

#### Custom Service Integration
Custom academic agent services can be added by modifying the `mcp_servers.json` file:

```python
# Add new academic agent service
"custom-academic-agent": AcademicAgentConfig(
    name="Custom Academic Service",
    url="https://your-academic-agent.com/api",
    headers={"Authorization": "Bearer your-api-key"},
    description="Your custom academic agent service description",
    enabled=True
)
```

#### Service Configuration Example
All services are managed through a unified configuration file, supporting dynamic enabling and disabling:

```json
{
    "FreeAcademicWrite": {
        "name": "Academic Agent Free Academic Writing Service",
        "url": "https://academicwrite.freemcps.aiearth.vip/sse",
        "headers": {"Authorization": "Bearer aioagi.tech"},
        "description": "Professional academic text processing and optimization service",
        "enabled": true
    }
}
```

### 🌍 Service Support Scope

#### Multi-language Support
- **Chinese**: Complete support for Simplified and Traditional Chinese academic text processing
- **English**: Professional English academic text grammar checking and optimization
- **Multilingual Translation**: Supports academic content translation for major international languages

#### Discipline Coverage
- Computer Science & Artificial Intelligence
- Biomedical & Life Sciences
- Physics & Materials Science
- Chemistry & Chemical Engineering
- Mathematics & Statistics
- Economics & Management Science
- Humanities & Social Sciences

## 📈 More Academic Agent MCP Services

We are actively expanding more professional academic agent services, which will be released through our free MCP service project. We are committed to providing comprehensive, free agent services for academic research, covering all aspects of academic research.

### 🔬 Upcoming Services

- **📚 Academic Literature Management Service (FreeAcademicLibrary)** - Intelligent literature retrieval and recommendation, automatic citation format generation, literature notes and annotation management, academic knowledge graph construction
- **📊 Data Analysis Service (FreeAcademicAnalysis)** - Statistical analysis tool integration, machine learning model training, experimental data processing, result visualization and interpretation
- **🤖 Academic AI Assistant Service (FreeAcademicAssistant)** - Personalized research suggestions, academic schedule management, peer review assistance, research project planning
- **🌐 Academic Collaboration Service (FreeAcademicCollaboration)** - Cross-institutional research collaboration, academic resource sharing, online academic conference support, intellectual property protection

### 🎯 Long-term Vision

Our goal is to build a complete **Academic Agents Ecosystem** covering the entire lifecycle of academic research:

1. **Pre-research Phase**: Literature survey, topic analysis, proposal design
2. **Research Process**: Data collection, experiment execution, result analysis
3. **Result Output**: Paper writing, chart creation, academic publication
4. **Knowledge Dissemination**: Academic exchange, peer review, knowledge sharing

### 🌐 Project Address

More free academic agent MCP services will be released through our dedicated project, welcome to follow and Star:

👉 [https://github.com/AcademicAgentsStudio/Academic-Free-MCP-Servers](https://github.com/AcademicAgentsStudio/Academic-Free-MCP-Servers)

In this project, you can find:

- **📋 Latest Service List**: Complete list of all free academic agent MCP services
- **🔧 Detailed Configuration Guide**: Including service configuration files and API usage instructions
- **🚀 Quick Start Tutorial**: Deploy and use all services from scratch
- **📚 Complete Technical Documentation**: Function descriptions, usage scenarios, and API documentation for each service
- **🔄 Update Log**: Service version updates and feature enhancement records
- **🐛 Issue Reporting**: Report problems and make suggestions via GitHub Issues
- **💬 Community Support**: Join our academic exchange group for real-time help

### 🆓 Service Features

- **Completely Free**: All academic agent services are permanently free for academic users
- **Out-of-the-box**: Provides standardized MCP protocol configuration, easy integration into existing workflows
- **Continuous Updates**: Continuous optimization and service function expansion based on user feedback
- **Professional Support**: Professional support provided by technical teams with academic research backgrounds

> 💡 **Tip**: Follow our MCP service project to get the latest service updates first. All new services will be released in this project first and integrated into the main platform after community testing.
> 
> **🌟 Let's build a better academic research tool ecosystem together!**
> 
> **🎯 Experience Now**: Visit our [Online Demo](https://agents.aiearth.vip) to experience the complete academic agent functionality!

---

### Ⅰ: Academic Agents Studio Development Versions:
- version 1.0 (2025.9.17-2025.10.24): 
  - **New Academic Agent Interface Optimization & Function Integration** - Tech-style UI design, dynamic border glow, frosted glass effects, smart interaction enhancement, academic agent external tool calling, multi-user session isolation

- Known Issues
    - Some browser translation plugins interfere with the operation of this software's frontend
    - Official Gradio currently has many compatibility issues, please **use `requirement.txt` to install Gradio**

### Ⅱ: Themes
Change themes by modifying the `THEME` option (config.py)
1. `Chuanhu-Small-and-Beautiful` [URL](https://github.com/GaiZhenbiao/ChuanhuChatGPT/)

### Ⅲ: Development Branches of This Project

1. `master` branch: Main branch, stable version
2. How to [integrate other large models](request_llms/README.md)

### V: References & Learning

```
The code references designs from many other excellent projects:

# Qwen-Agent:
https://github.com/QwenLM/Qwen-Agent

# Model Context Protocol:
https://github.com/modelcontextprotocol

# GPT Academic:
https://github.com/binary-husky/gpt_academic

# Tsinghua ChatGLM2-6B:
https://github.com/THUDM/ChatGLM2-6B

# Tsinghua JittorLLMs:
https://github.com/Jittor/JittorLLMs

# ChatPaper:
https://github.com/kaixindelele/ChatPaper

# Edge-GPT:
https://github.com/acheong08/EdgeGPT

# ChuanhuChatGPT:
https://github.com/GaiZhenbiao/ChuanhuChatGPT

# Oobabooga one-click installer:
https://github.com/oobabooga/one-click-installers

# More：
https://github.com/gradio-app/gradio
https://github.com/fghrsh/live2d_demo
```

---

## 🌟 Join Our Community

Welcome to the **Academic Agents Studio** academic agent community! Here you can:

- 💬 **Exchange usage experiences**: Share usage tips, get best practices
- 🐛 **Report issues**: Report bugs, suggest improvements
- 🎯 **Feature discussions**: Participate in new feature design, propose requirement suggestions
- 📚 **Academic exchange**: Exchange research insights with other scholars
- 🚀 **Early access**: Experience new features and version updates first

### 📱 Scan QR Code to Join Group Chat

<div align="center">
<table>
<tr>
<td align="center">
<img src="./docs/images/QQ_group.png" width="200" alt="QQ Group QR Code"/><br>
<strong>🐧 QQ Discussion Group</strong><br>
<em>Academic Agents Discussion Group</em>
</td>
<td align="center">
<img src="./docs/images/Wechat_group.png" width="200" alt="WeChat Group QR Code"/><br>
<strong>💬 WeChat Discussion Group</strong><br>
<em>Academic Agents Discussion Group</em>
</td>
</tr>
</table>

</div>

> [!TIP]
> **Group Benefits**:
> - 🎁 New user exclusive configuration guide
> - 📖 Exclusive usage tutorials and templates
> - 🔥 Early testing of latest features
> - 💡 One-on-one technical support
> - 📊 Academic resource sharing

### 💌 Other Contact Methods

- 📧 **Email**: aioagi@aioagi.tech
- 🐙 **GitHub Issues**: [Submit issues and suggestions](https://github.com/AcademicAgentsStudio/issues)
- 📝 **Documentation Center**: [Online documentation](https://github.com/AcademicAgentsStudio/Academic-Agents-Studio/wiki)

---

<div align="center">

**🎯 Academic Agents Studio - Let AI be your powerful academic research assistant!**

😊 If this project helps you, please give us a ⭐ Star!

[⬆️ Back to top](#academic-agents-studio)

</div>
```