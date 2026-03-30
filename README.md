# ASTLIBRA MOD 工具

一个用于 ASTLIBRA 游戏的文本提取、编辑和导入工具，支持游戏本地化和 MOD 制作。

## 功能特性

- 🎮 **自动检测游戏目录** - 启动时自动查找游戏安装位置
- 📝 **文本提取** - 从游戏文件中提取对话和界面文本（支持 6 种语言，12000+ 条文本）
- ✏️ **文本编辑** - 现代化 Web UI 编辑游戏文本，支持搜索、分类筛选、分页浏览
- 📦 **文本导入** - 将修改后的文本重新打包到游戏中
- 🔧 **MOD 管理** - 文件覆盖式 MOD 系统，支持图像、音频、字体等任意文件替换

## 系统要求

- Windows 操作系统
- Python 3.11+ 或直接使用打包好的 exe 文件
- ASTLIBRA 游戏本体

## 使用方法（两种方式）

### 方式一：使用打包好的 exe（推荐）

1. 下载 `ASTLIBRA_MOD_Tool.exe`
2. 将 exe 文件放到游戏目录的子文件夹中：
   ```
   ASTLIBRA/
   ├── ASTLIBRA.exe
   ├── DATA/
   └── tools/
       └── ASTLIBRA_MOD_Tool.exe  ← 放在这里
   ```
3. 双击运行即可

### 方式二：从源码运行

1. 克隆或下载本项目到游戏目录的子文件夹中：
   ```
   ASTLIBRA/
   ├── ASTLIBRA.exe
   ├── DATA/
   └── astlibra_mod_tool/  ← 将工具放在这里
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 启动工具：
   ```bash
   python main.py
   ```

### 首次使用

1. 启动工具后会自动检测游戏目录
2. 如果是首次运行，工具会自动执行以下操作：
   - 解包 `DAT.dxa` 文件
   - 修改游戏 EXE 文件（创建备份）
   - 提取游戏文本到 CSV 文件
   - 重新打包为 DAT 文件

3. 提取完成后，可以在"对话文本"页面查看和编辑文本

### 编辑文本

1. 点击左侧导航栏的"对话文本"
2. 使用搜索框或分类筛选找到要修改的文本
3. 双击表格行打开编辑对话框
4. 修改文本后点击"保存"（自动保存到 CSV）
5. 点击"应用到游戏"将所有修改打包到游戏中
6. 重启游戏查看效果

### 使用 MOD

1. 点击左侧导航栏的"MOD 管理"
2. 将 MOD 文件夹放到游戏目录的 `MODS/` 文件夹中
3. 在列表中选择要激活的 MOD
4. 点击"激活选中的 MOD"
5. 重启游戏即可使用 MOD
6. 点击"还原原版"可恢复所有原始文件

## 项目结构

```
astlibra_mod_tool/
├── main.py                    # 程序入口（pywebview 启动）
├── config.py                  # 配置管理
├── requirements.txt           # 依赖列表
├── web/                       # Web 前端（Vue 3）
│   ├── index.html            # 主页面
│   ├── css/                  # 样式文件
│   └── js/                   # JavaScript 组件
│       ├── app.js           # 主应用
│       └── pages/           # 页面组件
│           ├── home.js      # 首页
│           ├── dialogue.js  # 文本编辑
│           └── mod.js       # MOD 管理
├── frontend/                  # Python API 层
│   └── api.py                # pywebview JS API 桥接
├── backend/                   # 后端业务逻辑
│   └── services/             # 业务服务
│       ├── game_manager.py   # 游戏目录检测
│       ├── text_extractor.py # 文本提取
│       ├── text_importer.py  # 文本导入
│       └── mod_manager.py    # MOD 管理
└── core/                      # 核心工具
    ├── _ALOC.py              # ALOC 格式处理
    ├── patch_exe.py          # EXE 修补
    ├── text_classifier.py    # 文本分类
    └── read_csv.py           # CSV 读取
```

## 技术栈

- **UI 框架**: Vue 3 + pywebview（原生窗口 + Web UI）
- **后端**: Python 3.11+
- **数据处理**: Pandas
- **打包工具**: PyInstaller

## 注意事项

⚠️ **重要提示**：
- 工具会自动备份原始游戏文件（`DAT_BACK.dxa`）
- 首次运行会修改游戏 EXE 文件，建议提前备份
- 修改文本后需要点击"导入到游戏"才能在游戏中生效
- 建议在修改前备份整个游戏目录

## 常见问题

### Q: 提示"未找到游戏目录"怎么办？
A: 确保工具放在游戏目录的子文件夹中，且游戏目录包含 `ASTLIBRA.exe` 和 `DATA` 文件夹。

### Q: 修改文本后游戏中没有变化？
A: 确保点击了"导入到游戏"按钮，并重启游戏。

### Q: 如何恢复原始游戏文件？
A: 将 `DATA/DAT_BACK.dxa` 重命名为 `DAT.dxa` 即可恢复。

## 开发相关

### 打包为 exe

```bash
# 方式一：使用打包脚本（Windows）
build.bat

# 方式二：手动打包
pip install pyinstaller
pyinstaller build.spec
```

打包后的文件位于 `dist/ASTLIBRA_MOD_Tool.exe`

## 架构说明

项目采用 **Python 后端 + Web 前端** 的混合架构：

- **前端**: Vue 3 单页应用，提供现代化的用户界面
- **桥接层**: pywebview 提供原生窗口和 Python-JavaScript 通信
- **后端**: Python 处理游戏文件操作、文本提取/导入、MOD 管理

数据流：`Web UI → JS API → Python API (api.py) → Backend Services → Core Tools`

详细架构文档请查看 [CLAUDE.md](CLAUDE.md)

## 许可证

本项目仅供学习和个人使用，请勿用于商业用途。

## 免责声明

本工具仅用于学习和研究目的。使用本工具修改游戏文件的风险由用户自行承担。请支持正版游戏。

## 致谢
感谢提供工具包的Gize大佬
感谢遗忘的银灵