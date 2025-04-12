# 规则获取工具

这是一个用于获取 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script) 仓库中各种代理工具规则的工具。

## 功能

- 获取支持的代理规则工具列表（如Surge、QuantumultX等）
- 获取特定工具的规则文件列表
- 获取特定规则文件的链接（raw文件和GitHub页面）

## 安装

```bash
# 克隆仓库
git clone https://github.com/你的用户名/get_rule_from_blackmatrix7.git
cd get_rule_from_blackmatrix7

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 启动服务

```bash
python server.py
```

### API功能

- **获取支持的代理规则工具列表**
  - 通过 `get_tools()` 函数

- **获取特定工具的规则文件列表**
  - 通过 `get_files(tool_name)` 函数

- **获取特定工具的规则文件名列表**
  - 通过 `get_file_names(tool_name)` 函数

- **获取特定规则文件的链接**
  - 通过 `get_file_url(tool_name, file_name)` 函数

## 缓存机制

工具使用内存缓存来提高性能，缓存时间为1小时。

## 技术细节

- 使用FastMCP框架
- 通过GitHub API获取仓库内容
- 支持获取raw文件URL和GitHub页面URL

## 许可证

请遵循原仓库 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script) 的许可要求。
