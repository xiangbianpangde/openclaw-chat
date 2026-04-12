"""
MCP (Model Context Protocol) Skill

简化版 MCP 配置工具
"""

class MCPConfig:
    """MCP 配置类"""
    
    def __init__(self):
        self.servers = {}
    
    def add_server(self, name, config):
        """添加 MCP 服务器"""
        self.servers[name] = config
    
    def get_config(self):
        """获取完整配置"""
        return {
            "mcpServers": self.servers
        }
    
    def save(self, path):
        """保存配置到文件"""
        import json
        with open(path, 'w') as f:
            json.dump(self.get_config(), f, indent=2)

# 默认配置
default_mcp = MCPConfig()
default_mcp.add_server("filesystem", {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
})

print("✅ MCP Skill 已配置（简化版）")
