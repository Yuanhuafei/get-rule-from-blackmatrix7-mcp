# server.py
from fastmcp import FastMCP
import sys
import os
import json
import requests
import time
from typing import Dict, List, Any

mcp = FastMCP("rule_script", instructions="""
    获取代理规则工具列表
    获取特定工具的规则文件列表
""", dependencies=["requests"])

# 常量配置
REPO_API_URL = "https://api.github.com/repositories/276008164/contents/rule"
RAW_BASE_URL = "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master"
GITHUB_BASE_URL = "https://github.com/blackmatrix7/ios_rule_script/blob/master"
CACHE_DURATION = 3600  # 缓存时间（1小时）

# 缓存管理
cache = {
    "tools": {"timestamp": 0, "data": []},
    "files": {}  # 格式: {"工具名": {"timestamp": 时间戳, "data": 数据}}
}

def get_from_cache(cache_key: str, tool_name: str = None) -> List[Dict[str, Any]]:
    """从缓存获取数据"""
    if cache_key == "tools":
        if time.time() - cache["tools"]["timestamp"] < CACHE_DURATION:
            return cache["tools"]["data"]
    elif cache_key == "files" and tool_name:
        if tool_name in cache["files"] and time.time() - cache["files"][tool_name]["timestamp"] < CACHE_DURATION:
            return cache["files"][tool_name]["data"]
    return []

def save_to_cache(cache_key: str, data: List[Dict[str, Any]], tool_name: str = None) -> None:
    """保存数据到缓存"""
    if cache_key == "tools":
        cache["tools"] = {"timestamp": time.time(), "data": data}
    elif cache_key == "files" and tool_name:
        cache["files"][tool_name] = {"timestamp": time.time(), "data": data}

@mcp.tool()
def get_tools() -> List[Dict[str, Any]]:
    """获取支持的代理规则工具列表
    
    返回:
        工具列表
    """
    # 尝试从缓存获取
    cached_data = get_from_cache("tools")
    if cached_data:
        return cached_data
    
    try:
        # 从GitHub API获取
        response = requests.get(REPO_API_URL)
        response.raise_for_status()
        
        # 过滤出目录类型的条目
        tools = [item for item in response.json() if item["type"] == "dir"]
        
        # 处理数据，提取需要的字段
        processed_tools = [{
            "name": item["name"],
            "path": item["path"],
            "url": item["html_url"]
        } for item in tools]
        
        # 保存到缓存
        save_to_cache("tools", processed_tools)
        
        return processed_tools
    except Exception as e:
        sys.stderr.write(f"获取工具列表出错: {e}\n")
        return []

@mcp.tool()
def get_files(tool_name: str) -> List[Dict[str, Any]]:
    """获取特定工具的规则文件列表
    
    参数:
        tool_name: 工具名称，如"Surge"、"QuantumultX"等
        
    返回:
        规则文件列表(包含完整信息)
    """
    # 尝试从缓存获取
    cached_data = get_from_cache("files", tool_name)
    if cached_data:
        return cached_data
    
    try:
        # 从GitHub API获取
        url = f"{REPO_API_URL}/{tool_name}"
        response = requests.get(url)
        response.raise_for_status()
        
        # 处理数据，提取需要的字段并构建下载链接
        files = [{
            "name": item["name"],
            "raw_url": f"{RAW_BASE_URL}/rule/{tool_name}/{item['name']}.list" if item["type"] == "dir" else item["download_url"],
            "github_url": f"{GITHUB_BASE_URL}/rule/{tool_name}/{item['name']}.list" if item["type"] == "dir" else item["html_url"],
            "type": item["type"]
        } for item in response.json()]
        
        # 保存到缓存
        save_to_cache("files", files, tool_name)
        
        return files
    except Exception as e:
        sys.stderr.write(f"获取文件列表出错: {e}\n")
        return []

@mcp.tool()
def get_file_names(tool_name: str) -> List[str]:
    """获取特定工具的规则文件名
    
    参数:
        tool_name: 工具名称，如"Surge"、"QuantumultX"等
        
    返回:
        规则文件名列表
    """
    try:
        # 获取完整文件信息
        files = get_files(tool_name)
        # 只返回文件名
        return [file["name"] for file in files]
    except Exception as e:
        sys.stderr.write(f"获取文件名列表出错: {e}\n")
        return []

@mcp.tool()
def get_file_url(tool_name: str, file_name: str) -> Dict[str, str]:
    """获取特定规则文件的链接
    
    参数:
        tool_name: 工具名称，如"Surge"、"QuantumultX"等
        file_name: 文件名称
        
    返回:
        包含raw_url和github_url的字典
    """
    try:
        # 获取完整文件信息
        files = get_files(tool_name)
        
        # 查找指定文件
        for file in files:
            if file["name"] == file_name:
                return {
                    "raw_url": file["raw_url"],
                    "github_url": file["github_url"]
                }
                
        # 未找到指定文件
        return {"error": f"未找到文件: {file_name}"}
    except Exception as e:
        sys.stderr.write(f"获取文件链接出错: {e}\n")
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run()