# ASTLIBRA MOD 工具

一个用于 ASTLIBRA 游戏的文本提取、编辑和导入工具，支持游戏本地化和 MOD 制作。

## 功能特性

- **自动检测游戏目录** — 启动时自动查找游戏安装位置
- **文本提取** — 手动触发从游戏文件提取对话和界面文本（支持 6 种语言，12000+ 条文本）
- **文本编辑** — Web UI 编辑游戏文本，支持搜索、分类筛选、分页浏览
- **文本导入** — 将修改后的文本重新打包到游戏中，支持导出 `LOCALIZE_.DAT`
- **MOD 管理** — 文件覆盖式 MOD 系统，支持图像、音频、字体等任意文件替换，支持批量激活
- **一键还原** — 还原游戏 EXE 及所有数据文件到原版状态
- **DIG 图像工具** — `core/TOOLS/` 提供游戏专属 `.dig` 图像格式的解码与编码脚本

## 系统要求

- **Windows**（仅支持 Windows，依赖 Win32 API）
- Python 3.11+（从源码运行时）或直接使用打包好的 exe
- ASTLIBRA 游戏本体

## 使用方法

### 方式一：使用打包好的 exe（推荐）

1. 下载 `ASTLIBRA_MOD_TOOL.exe`
2. 将 exe 文件放到**游戏根目录**（与 `ASTLIBRA.exe` 同级）：
   ```
   ASTLIBRA/
   ├── ASTLIBRA.exe
   ├── DATA/
   └── ASTLIBRA_MOD_TOOL.exe  ← 放在这里
   ```
3. 双击运行即可

### 方式二：从源码运行

1. 将项目克隆到**游戏根目录**：
   ```
   ASTLIBRA/
   ├── ASTLIBRA.exe
   ├── DATA/
   ├── config.py        ← 项目根目录必须与游戏根目录一致
   └── main.py
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

1. 启动工具后自动检测游戏目录
2. 进入「对话文本」页，点击「**开始提取文本**」手动触发提取流程：
   - 解包 `DAT.dxa` → 备份为 `DAT_BACK.dxa`
   - 修改游戏 EXE（原版自动备份为 `ASTLIBRA_back.exe`）
   - 提取文本到 CSV
   - 重新打包为 `LOCALIZE_.DAT`
3. 提取完成后即可在「对话文本」页查看和编辑

### 编辑文本

1. 进入「对话文本」页
2. 使用搜索框或分类筛选找到要修改的文本
3. 双击表格行打开编辑对话框，修改后点击「保存」
4. 点击「**应用到游戏**」将所有修改打包写入游戏文件
5. 重启游戏查看效果

### 使用 MOD

1. 将 MOD 文件夹放到游戏目录的 `MODS/` 文件夹中，结构示例：
   ```
   MODS/
   └── MyMod/
       ├── mod_info.json   （可选，包含名称/版本/作者/描述）
       ├── Image/          （图像替换）
       ├── Sound/          （音频替换）
       └── DAT/            （文本替换，需包含 LOCALIZE_.DAT）
   ```
2. 进入「MOD 管理」页，选中要激活的 MOD
3. 点击「**激活选中的 MOD**」（支持批量）
4. 重启游戏即可生效
5. 点击「**还原原版**」可恢复所有原始文件

### 还原游戏文件

- **还原文本**：「对话文本」页 → 「还原原版」（从模板重新生成 CSV 和 DAT）
- **还原所有**：首页「**一键还原**」→ 同时还原 EXE 和所有游戏数据文件夹

### DIG 图像工具（standalone 脚本）

```bash
# 解码：.dig → .png
python core/TOOLS/dig_decoder.py <file.dig>
# 输出 <file.dig>comp.png

# 编码：修改后的 png → .dig（自动创建 .bak 备份）
python core/TOOLS/dig_encoder.py <file.dig.png>
# 覆盖写回原 .dig 文件
```

支持 1/2/3/4 通道 DIG 文件（zlib 压缩 + PNG 滤波，BGRA 字节序）。

## 项目结构

```
ASTLIBRA_MOD_TOOL.spec     # PyInstaller 打包配置
main.py                    # 程序入口（pywebview 原生窗口）
config.py                  # 路径管理与游戏目录检测
requirements.txt           # Python 依赖
web/                       # Vue 3 前端（由 pywebview 托管）
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── app.js         # Vue 应用初始化与路由
│       └── pages/
│           ├── home.js    # 首页 + 一键还原
│           ├── dialogue.js # 文本提取与编辑
│           └── mod.js     # MOD 管理
frontend/api.py            # Python API 桥接（暴露给 JS 的所有方法）
backend/services/
│   ├── game_manager.py    # 游戏目录检测
│   ├── text_extractor.py  # 5 步提取流水线
│   ├── text_importer.py   # 文本导入/还原
│   └── mod_manager.py     # MOD 激活（7 步）/ 还原
core/
│   ├── _ALOC.py           # ALOC 二进制格式读写
│   ├── patch_exe.py       # 游戏 EXE 修补
│   ├── text_classifier.py # 文本分类规则
│   ├── read_csv.py        # CSV 读取（含分类）
│   ├── ASTLIBRA_Dec.exe   # .dxa 解包器
│   └── TOOLS/
│       ├── dig_decoder.py # .dig → PNG
│       └── dig_encoder.py # PNG → .dig
```

## 技术栈

- **UI 框架**: Vue 3（本地打包，无 CDN）+ pywebview（edgechromium 后端）
- **Python 后端**: 3.11+，Pandas 处理 CSV，threading 异步任务
- **打包**: PyInstaller（`console=False`，输出 `dist/ASTLIBRA_MOD_TOOL.exe`）

## 打包为 exe

```bash
pip install pyinstaller
pyinstaller ASTLIBRA_MOD_TOOL.spec
```

输出：`dist/ASTLIBRA_MOD_TOOL.exe`

调试时在 `ASTLIBRA_MOD_TOOL.spec` 第 32 行将 `console=False` 改为 `console=True` 再打包。

## 注意事项

- 工具会自动备份原始游戏文件（`DAT_BACK.dxa`、`ASTLIBRA_back.exe`），建议初次运行前手动备份整个游戏目录
- 修改文本后需点击「应用到游戏」才能在游戏中生效
- MOD 激活时会重新解压游戏数据，耗时较长，请勿中途关闭

## 常见问题

**Q: 提示"未找到游戏目录"？**  
A: 确保工具（exe 或源码项目根目录）与 `ASTLIBRA.exe` 位于**同一文件夹**，且游戏目录包含 `DATA` 子文件夹。

**Q: 修改文本后游戏中没有变化？**  
A: 确认已点击「应用到游戏」，然后重启游戏。

**Q: 如何恢复原始游戏文件？**  
A: 首页点击「一键还原」，或手动将 `DATA/DAT_BACK.dxa` 重命名为 `DAT.dxa`。

## 致谢

感谢提供工具包的 Gize 大佬  
感谢遗忘的银灵（FORSAKENSILVER）提供 DIG 图像格式工具

## 许可证

本项目仅供学习和个人使用，请勿用于商业用途。使用本工具修改游戏文件的风险由用户自行承担，请支持正版游戏。
