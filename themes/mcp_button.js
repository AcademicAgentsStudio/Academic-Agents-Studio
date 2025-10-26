/**
 * MCP 智能体按钮状态管理
 * 科技感集成按钮的状态控制逻辑
 */

// MCP按钮状态管理器
window.MCPButtonManager = {
    // 状态常量
    STATUS: {
        DISABLED: 'mcp-disabled',
        ENABLED: 'mcp-enabled',
        ERROR: 'mcp-error'
    },

    // 获取按钮元素
    getButton: function() {
        return document.getElementById('mcp_toggle_btn');
    },

    // 清除所有状态类
    clearStatusClasses: function(button) {
        if (!button) return;
        Object.values(this.STATUS).forEach(status => {
            button.classList.remove(status);
        });
    },

    // 设置按钮状态
    setStatus: function(status) {
        const button = this.getButton();
        if (!button) {
            console.warn('MCP按钮未找到');
            return;
        }

        // 清除现有状态
        this.clearStatusClasses(button);

        // 添加新状态
        if (status && this.STATUS[status.toUpperCase()]) {
            button.classList.add(this.STATUS[status.toUpperCase()]);
        }

        // 触发状态更新动画
        this.triggerUpdateAnimation(button);
    },

    // 触发更新动画
    triggerUpdateAnimation: function(button) {
        if (!button) return;

        // 添加更新动画类
        button.classList.add('mcp-updating');

        // 移除动画类
        setTimeout(() => {
            button.classList.remove('mcp-updating');
        }, 500);
    },

    // 初始化按钮事件
    initialize: function() {
        const button = this.getButton();
        if (!button) return;

        // 添加点击波纹效果
        button.addEventListener('click', this.addRippleEffect.bind(this));

        // 初始化状态
        this.setStatus('disabled');

        console.log('MCP按钮管理器初始化完成');
    },

    // 添加点击波纹效果
    addRippleEffect: function(e) {
        const button = e.currentTarget;
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        // 创建波纹元素
        const ripple = document.createElement('div');
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            pointer-events: none;
            transform: scale(0);
            animation: mcp-ripple-effect 0.6s ease-out;
            z-index: 1;
        `;

        button.appendChild(ripple);

        // 动画结束后移除元素
        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.parentNode.removeChild(ripple);
            }
        }, 600);
    }
};

// 添加波纹动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes mcp-ripple-effect {
        0% {
            transform: scale(0);
            opacity: 1;
        }
        100% {
            transform: scale(2);
            opacity: 0;
        }
    }

    .mcp-updating {
        animation: mcp-update-pulse 0.5s ease-in-out !important;
    }

    @keyframes mcp-update-pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
`;
document.head.appendChild(style);

// 全局函数供Python调用
window.updateMCPButtonStatus = function(isEnabled, hasError = false) {
    if (hasError) {
        window.MCPButtonManager.setStatus('error');
    } else if (isEnabled) {
        window.MCPButtonManager.setStatus('enabled');
    } else {
        window.MCPButtonManager.setStatus('disabled');
    }
};

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        window.MCPButtonManager.initialize();
    });
} else {
    window.MCPButtonManager.initialize();
}