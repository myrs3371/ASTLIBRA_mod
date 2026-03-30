# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概览

ASTLIBRA MOD Tool - 用于 ASTLIBRA 游戏的文本提取、编辑和导入工具。支持本地化和 MOD 制作，处理 12,000+ 条多语言文本。

**技术栈**: Python 3.11+, Vue 3 (Web UI), pywebview (原生窗口), Pandas (数据处理), PyInstaller (打包)

## 开发命令

### 运行应用程序
```bash
# 安装依赖
pip install -r requirements.txt

# 从源码运行
python main.py
```

### 构建可执行文件
```bash
# 使用 PyInstaller 构建
pip install pyinstaller
pyinstaller ASTLIBRA_MOD_TOOL.spec
```
输出: `dist/ASTLIBRA_MOD_TOOL.exe`

## 架构

### 混合桌面应用架构
原生窗口 (pywebview) + Web UI (Vue 3) + Python 后端

**分层结构**:
- **前端层**: Vue 3 SPA，提供响应式 UI 组件
- **桥接层**: pywebview 提供 `window.pywebview.api.*` 用于 JS ↔ Python 通信
- **API 层**: [frontend/api.py](frontend/api.py) 向 JavaScript 暴露 Python 方法
- **服务层**: [backend/services/](backend/services/) 处理业务逻辑
- **核心层**: [core/](core/) 处理二进制文件操作

### 关键目录
```
astlibra_mod_tool/
├── main.py                    # 入口点 - 创建 pywebview 窗口
├── config.py                  # 路径管理和游戏目录检测
├── web/                       # Vue 3 前端
│   ├── index.html
│   └── js/
│       ├── app.js            # Vue 应用初始化和路由
│       └── pages/            # 页面组件 (home, dialogue, mod)
├── frontend/api.py            # pywebview JS API 桥接
├── backend/services/          # 业务逻辑
│   ├── game_manager.py       # 游戏目录检测
│   ├── text_extractor.py     # 文本提取流水线
│   ├── text_importer.py      # 文本导入流水线
│   └── mod_manager.py        # MOD 激活/停用
└── core/                      # 二进制处理工具
    ├── _ALOC.py              # ALOC 格式打包/解包器
    ├── patch_exe.py          # 游戏 EXE 补丁器
    ├── text_classifier.py    # 文本分类
    └── ASTLIBRA_Dec.exe      # DAT.dxa 解包器
```
关键工作流
文本提取流水线 (首次运行):

使用 ASTLIBRA_Dec.exe 解包 DAT.dxa → DAT/ 文件夹
给游戏 EXE 打补丁 (字节替换以启用文本读取)
使用 _ALOC.py 从 LOCALIZE_.DAT 提取文本 → CSV
重新打包为 DAT 格式
文本编辑流程:

Web UI 通过 JS API 调用从 Python 后端获取数据
用户在 Vue 组件 中编辑文本
更改发送到 Python API → 保存到 CSV
导入流水线重新打包 CSV → LOCALIZE_.DAT → 游戏文件
MOD 系统:

MODS/ 目录中的基于文件的覆盖系统
每个 MOD 是一个包含 mod_info.json + 替换文件的文件夹
激活时将文件复制到游戏目录 (不含备份),注意把原来的游戏文件的名字想解压文本一样带上_BACK后缀
还原时将游戏DAT、Image、Image2K、Sound、Image4K、Image720p删除,重新解压原本的文件
只需要扫描展示、激活、还原功能
关键路径管理
Config 类集中了所有路径逻辑:

通过搜索 ASTLIBRA.exe + DATA/ 自动检测游戏目录
工具必须放置在游戏文件夹的子目录中
所有路径都相对于检测到的游戏根目录解析
数据流
 复制
 插入
 新文件

DAT.dxa (二进制)
  → ASTLIBRA_Dec.exe → DAT/LOCALIZE_.DAT
  → _ALOC.py (导出) → _extracted_texts.csv
  → Web UI (Vue) ↔ Python API (api.py) ↔ CSV
  → _ALOC.py (导入) → LOCALIZE_.DAT
  → 游戏文件
架构模式
混合桌面应用: 原生窗口 + Web UI (Vue 3) + Python 后端

前端层: 带有响应式组件的 Vue 3 SPA
桥接层: pywebview 提供 window.pywebview.api.* 用于 JS → Python 调用
API 层: frontend/api.py 向 JavaScript 暴露 Python 方法
服务层: backend/services/ 处理业务逻辑
核心层: core/ 处理二进制文件操作
重要约束
Windows 文件路径
关键: 在 Windows 上使用编辑/写入工具时，文件路径必须使用反斜杠 (\)，而不是正斜杠 (/)
示例: e:\game\ASTLIBRA\...\file.py (正确) vs e:/game/... (错误)
大文件写入
不要在一次操作中写入大内容块
分割为最多 20-30 行的块
对于大文件，使用多次 Edit 调用或 bash heredoc
二进制格式详情
_ALOC.py 处理自定义 ALOC 二进制格式 (基于 struct 的解析)
文本编码: UTF-8，带有特殊标记 [n_rn] (CRLF) 和 [n_nr] (LF)
6 种语言列: JPN, US, ZH_CN, ZH_TW, KO, ES
线程
长时间运行的操作 (提取, 导入) 在后台线程中运行
Python API 方法启动线程并立即返回
前端通过 API 调用 (例如 get_extraction_status()) 轮询状态
不直接阻塞 UI 线程
开发说明
该工具修改游戏文件 - 始终创建备份 (DAT_BACK.dxa, EXE 的 .backup)
首次运行触发自动提取流水线
CSV 是文本编辑的事实来源
MOD 系统使用 JSON 清单 (mod_info.json) 存储元数据
Web UI 通过 pywebview 的双向 JS API 桥与 Python 通信
Vue.js 在本地打包 (web/js/vue.global.prod.js) 以消除 CDN 加载延迟
关键文件
main.py - 应用程序入口点，创建 pywebview 窗口
frontend/api.py - 暴露给 JavaScript 的 Python API
web/js/app.js - Vue 3 应用初始化和路由
config.py - 路径管理和游戏目录检测
core/_ALOC.py - 游戏文本文件的二进制格式解析器