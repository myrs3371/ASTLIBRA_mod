# 功能运行逻辑文档

本文档描述 ASTLIBRA MOD 工具各功能的内部运行逻辑，按用户操作流程组织。

---

## 1. 应用启动与初始化

**入口**: [main.py](main.py)

```
pywebview.create_window()
  └─ new Api()
       ├─ new GameManager()
       │    └─ find_game_directory()         ← 立即检测游戏目录
       └─ if found: new ModManager(game_path)
```

`main.py` 完成后通过 `api.set_window(window)` 将 pywebview 窗口引用注入 Api 实例，供后续 `evaluate_js()` 调用。

**Vue 应用初始化**: [web/js/app.js](web/js/app.js)

`rootApp` 挂载 `#app`，三个页面组件（homePage / dialoguePage / modPage）通过动态组件 `<component :is>` 切换。`startup()` 在 `mounted()` 中自动调用，仅通过 `pywebview.api.get_game_info()` 检测游戏目录：
- 未检测到游戏 → 全屏"未找到游戏目录"提示
- 检测到游戏 → 无额外操作（不自动触发文本提取）

---

## 2. 游戏目录检测

**入口**: [config.py](config.py) → `Config.get_game_path()`

```
get_game_path()
  ├─ frozen 模式（打包后）→ 从 sys.executable 所在目录开始查找
  └─ 源码模式 → 从 PROJECT_ROOT 开始查找
       └─ _check_game_files(path)
            ├─ 检查 ASTLIBRA.exe 是否存在
            └─ 检查 DATA/ 目录是否存在
```

工具必须放在游戏目录的子文件夹中，查找时会逐级向上扫描直到找到同时包含 `ASTLIBRA.exe` 和 `DATA/` 的目录。

`GameManager.find_game_directory()` 仅做一次检测并缓存结果；`Config.get_game_path()` 每次被调用时都会重新检测（静态方法）。

---

## 3. 首次文本提取（5 步流水线）

**触发时机**: 用户在"对话文本"页点击"开始提取文本"触发。

**调用链**:
```
dialoguePage.triggerExtraction()
  └─ props.startExtraction(callback)     ← app.js 注入的方法
       └─ pywebview.api.start_extraction()
            └─ threading.Thread(target=_do_extraction, daemon=True)
```

提取成功后 `callback` 被调用，触发 `fetchTexts()` 刷新表格。

**进度轮询**: 前端每 500ms 调用一次 `get_extraction_status()`，直到 `done=true`。

---

### 步骤 1 — 文件检查 `check_files()`

```
检查 exe_file 是否存在
检查 data_dir (DATA/) 是否为目录
任一不存在则中断
```

### 步骤 2 — 解包 DAT.dxa `unpack_dat_dxa()`

```
检查 DATA/DAT.dxa 是否存在
  ├─ 不存在但 DATA_BACK.dxa 存在 → 已解包，跳过
  └─ 不存在且备份也不存在 → 报错中断
删除旧的 DATA/DAT/ 文件夹（如存在）
subprocess.run([ASTLIBRA_Dec.exe, DAT.dxa], cwd=DATA/)
  └─ 返回码非 0 → 报错中断
检查 DATA/DAT/ 是否生成
os.rename(DATA/DAT.dxa → DATA/DAT_BACK.dxa)   ← 备份原文件
```

### 步骤 3 — 修改游戏 EXE `patch_exe()`

```
subprocess.run(['python', 'core/patch_exe.py', ASTLIBRA.exe], cwd=core/)
  └─ patch_exe.py 内部:
       1. 读取 ASTLIBRA.exe 全部字节
       2. 搜索字节序列 [0x89,0x41,0xF8,0x8B,0x41,0xFC,0xC1,0xC8,0x04,0x89,0x41,0xFC]
       3. 替换为 [0x90,0x90,0x90,0x8B,0x41,0xFC,0xC1,0xC8,0x04,0x90,0x90,0x90]
       4. shutil.copy2(ASTLIBRA.exe → ASTLIBRA.exe.backup)  ← 备份
       5. 写入修改后的字节
```

字节替换将一条汇编指令（NOP 填充），使游戏在读取文本时绕过原有的文本资源保护。

### 步骤 4 — 提取文本到 CSV `extract_texts()`

```
subprocess.run([
    'python', '_ALOC.py', 'LOCALIZE_.DAT_dec', '_temp_extracted.csv', '-e'
], cwd=core/)
  └─ _ALOC.py -e:
       读取 core/LOCALIZE_.DAT_dec（ALOC 二进制格式）
       解析每条文本的 6 个语言列偏移量
       用 latin-1 编码读取原文，换行符转为 [n_rn]/[n_nr]
       输出 9 列 CSV（含行号列）
shutil.copy2(_temp_extracted.csv → DATA/DAT/_extracted_texts.csv)
os.remove(_temp_extracted.csv)
```

**ALOC 二进制格式**（[_ALOC.py](core/_ALOC.py)）:
- 头部 52 字节（含 `ALOC` 魔数）
- 前 10968 条为索引块（每条含 ID、6 个语言偏移量）
- 偏移 478776 开始为实际文本数据
- 每段文本按 8 字节对齐，不足补 `\x00`

### 步骤 5 — 重新打包 LOCALIZE_.DAT `pack_to_dat()`

```
shutil.copy2(DATA/DAT/_extracted_texts.csv → core/_temp_pack.csv)
subprocess.run([
    'python', '_ALOC.py', 'LOCALIZE_.DAT_dec', '_temp_pack.csv', '-p'
], cwd=core/)
  └─ _ALOC.py -p:
       读取 LOCALIZE_.DAT_dec 头部（前 478776 字节）
       按 CSV 每行重建索引块（重新计算各语言偏移量）
       将 6 种语言文本以 UTF-8 写入，每段按 8 字节对齐
       生成新的 LOCALIZE_.DAT
shutil.copy2(core/LOCALIZE_.DAT → DATA/DAT/LOCALIZE_.DAT)
os.remove(core/_temp_pack.csv)
os.remove(core/LOCALIZE_.DAT)
```

---

## 4. 文本编辑与保存

**用户操作**: 在"对话文本"页面双击表格行 → 弹出编辑框 → 修改文本 → 点击"保存"

**前端流程**（[dialogue.js](web/js/pages/dialogue.js)）:
```
openEditDialog(item)
  └─ editRow = { ...item }, editText = item.zh_cn

saveEdit()
  └─ pywebview.api.update_text(offset, newText)
```

**后端逻辑**（[api.py](frontend/api.py) → `update_text()`）:
```
pandas.read_csv(DATA/DAT/_extracted_texts.csv,
    names=["id","Offset_start","JPN","US","ZH_CN","ZH_TW","KO","ES",""])
df.loc[df["Offset_start"] == int(offset), "ZH_CN"] = new_text
df.to_csv(csv_path, index=False, encoding="utf-8", quoting=1, header=False)
```

仅修改 CSV 中 `ZH_CN` 列，原始 `LOCALIZE_.DAT` 不变——"应用到游戏"后才写入 DAT 文件。

---

## 5. 文本应用到游戏

**用户操作**: 点击"应用到游戏"

**调用链**:
```
dialoguePage.applyToGame()
  └─ pywebview.api.apply_changes()
       └─ TextImporter(game_path).apply_changes()
```

**内部逻辑**:
```
shutil.copy2(DATA/DAT/_extracted_texts.csv → core/_temp_pack.csv)
subprocess.run([
    'python', '_ALOC.py', 'LOCALIZE_.DAT_dec', '_temp_pack.csv', '-p'
], cwd=core/)
shutil.copy2(core/LOCALIZE_.DAT → DATA/DAT/LOCALIZE_.DAT)
os.remove(core/_temp_pack.csv)
os.remove(core/LOCALIZE_.DAT)
```

与提取步骤 5 完全相同的打包逻辑，将最新的 CSV 重新生成为 DAT 文件，覆盖 `DATA/DAT/LOCALIZE_.DAT`。

---

## 6. 还原原始文本

**用户操作**: 点击"还原所有文本"

**调用链**:
```
pywebview.api.restore_original()
  └─ TextImporter(game_path).restore_original()
```

**内部逻辑**:
```
subprocess.run([
    'python', '_ALOC.py', 'LOCALIZE_.DAT_dec', '_temp_restore.csv', '-e'
], cwd=core/)
  └─ 从 core/LOCALIZE_.DAT_dec 重新导出原始 CSV
shutil.copy2(core/_temp_restore.csv → DATA/DAT/_extracted_texts.csv)
shutil.copy2(core/LOCALIZE_.DAT_dec → DATA/DAT/LOCALIZE_.DAT)
  └─ 使用未修改的模板文件覆盖
os.remove(core/_temp_restore.csv)
```

还原后 CSV 和 DAT 文件均为首次提取时的原始状态，所有用户编辑丢失。

---

## 7. MOD 扫描

**触发时机**: 进入"MOD 管理"页面时 `mounted()` 调用 `fetchMods()`

**调用链**:
```
pywebview.api.get_mods()
  └─ ModManager(game_path).scan_mods()
```

**内部逻辑**:
```
遍历 MODS/ 目录下所有子文件夹（跳过文件）
对每个子文件夹 mod_path:
  读取 mod_path/mod_info.json（如存在）
    ├─ 解析 JSON，添加 folder_name 字段
    └─ 不存在或解析失败 → 使用文件夹名作为 name，填充默认字段
返回 MOD 信息列表（不写入文件）
```

`mod_info.json` 标准字段: `name`, `version`, `author`, `description`, `files`

---

## 8. MOD 激活（7 步流水线）

**触发时机**: 用户勾选 MOD 后点击"激活勾选的 MOD"

**调用链**:
```
modPage.activateMod()
  └─ pywebview.api.activate_mods(checkedMods)
       └─ threading.Thread(target=_do_activate_mods, daemon=True)

_do_activate_mods()
  └─ ModManager.activate_mods(folder_names, status_callback=on_step)
```

**进度轮询**: 前端每 400ms 调用 `get_mod_status()`，直到 `done=true`。

---

### 步骤 1 — 检测/修补游戏 EXE

```
读取 ASTLIBRA.exe 字节
检查字节序列 [0x90,0x90,0x90,0x8B,0x41,0xFC,0xC1,0xC8,0x04,0x90,0x90,0x90] 是否存在
  ├─ 存在 → 已修补，跳过
  └─ 不存在 → 调用 patch_exe() 修补
```

### 步骤 2 — 备份文件改回原版文件名

```
for each DATA_BACK_LIST item (DAT_BACK.dxa 等):
  os.rename(DATA_BACK.dxa → DAT.dxa)
```

### 步骤 3 — 删除已解压的游戏数据文件夹

```
for each DATA_LIST item (DAT, Image, Sound 等):
  if os.path.isdir(DATA/xxx/):
    shutil.rmtree(DATA/xxx/)
```

### 步骤 4 — 重新解压原版 dxa 文件

```
for each DATA_GAME_LIST item (DAT.dxa, Image.dxa 等):
  subprocess.run([ASTLIBRA_Dec.exe, xxx.dxa], cwd=DATA/)
    └─ 超时 300s，跳过失败项继续
    └─ CREATE_NO_WINDOW 标志，不弹出控制台窗口
```

### 步骤 5 — 复制 MOD 文件

```
for each mod_folder_name:
  for each DATA_LIST item:
    if MODS/mod_name/DATA_LIST_item/ 存在:
      shutil.copytree(src, DATA/DATA_LIST_item/, dirs_exist_ok=True)
```

MOD 中的子文件夹会覆盖步骤 4 解压出的原版文件，实现替换式覆盖。

### 步骤 6 — 原版 dxa 文件改回备份文件名

```
for each DATA_GAME_LIST item:
  os.rename(DATA/xxx.dxa → DATA/xxx_BACK.dxa)
```

将步骤 4 解压产生的临时 dxa 文件改回备份名称，保证备份机制完整。

### 步骤 7 — 重新打包 LOCALIZE_.DAT

```
检查是否有 MOD 提供了 DAT/ 子文件夹（含文本替换）:
  ├─ 有 → LOCALIZE_.DAT 已在步骤 5 复制，跳过
  └─ 无 → 从 core/LOCALIZE_.DAT_dec 模板重新生成
       csv_temp = DATA/DAT/_temp_localize.csv
       subprocess.run(['python', aloc_tool, localize_dec, csv_temp, '-e'], cwd=DATA/DAT/)
       subprocess.run(['python', aloc_tool, localize_dec, csv_temp, '-p'], cwd=DATA/DAT/)
       os.remove(csv_temp)
```

`aloc_tool` 和 `localize_dec` 均指向 `core/` 目录下的文件，命令在 `DATA/DAT/` 目录下执行。

---

## 9. MOD 还原（原版恢复）

**触发时机**: 点击"还原原版文件"

**调用链**:
```
pywebview.api.restore_all_mods()
  └─ ModManager.restore_all()
```

**内部逻辑**:
```
for each DATA_LIST item (DAT, Image, Sound 等):
  if os.path.exists(DATA/xxx/):
    shutil.rmtree(DATA/xxx/)
for each DATA_BACK_LIST item (DAT_BACK.dxa 等):
  os.rename(DATA_BACK.dxa → DAT.dxa)
_save_active_mods([])   ← 清空激活列表
```

删除所有游戏数据文件夹（由 MOD 激活产生），将备份的 dxa 文件恢复为原名。**注意**：此操作不重新执行解压，`DAT.dxa` 恢复后需要配合 MOD 激活流程或手动解压才能使用。

---

## 10. MOD 删除

**触发时机**: 在 MOD 详情面板点击"删除此 MOD"

**调用链**:
```
pywebview.api.delete_mod(folder_name)
  └─ ModManager.delete_mod(folder_name)
```

**内部逻辑**:
```
if is_mod_active(folder_name):
  从 active_mods.json 中移除该 MOD
shutil.rmtree(MODS/folder_name/)
```

仅删除 MOD 文件夹，不影响已激活到游戏目录的文件。已在游戏中生效的 MOD 文件需通过"还原原版文件"恢复。

---

## 附录：关键数据结构

### CSV 文件格式
```
列: id_текста, Offset_start, JPN, US, ZH_CN, ZH_TW, KO, ES, (行号)
换行符: [n_rn] = CRLF, [n_nr] = LF
```

### active_mods.json 格式
```json
{ "mods": [{ "name": "MyMod", "folder_name": "MyMod", ... }, ...] }
```

### mod_info.json 格式
```json
{
  "name": "MOD名称",
  "version": "1.0",
  "author": "作者",
  "description": "描述",
  "files": ["Image/xxx.png", "DAT/LOCALIZE_.DAT"]
}
```

### _extraction_status / _mod_status 结构
```python
{
    "step": "正在xxx...",   # 当前步骤描述
    "done": False,          # 是否完成
    "success": False,       # 是否成功
    "error": None           # 错误信息（失败时有值）
}
```

### DATA_LIST / DATA_BACK_LIST / DATA_GAME_LIST 对照
| DATA_LIST   | DATA_BACK_LIST         | DATA_GAME_LIST   |
|-------------|------------------------|-------------------|
| DAT         | DAT_BACK.dxa           | DAT.dxa           |
| Image       | Image_BACK.dxa         | Image.dxa         |
| Image2K     | Image2K_BACK.dxa       | Image2K.dxa       |
| Image4K     | Image4K_BACK.dxa       | Image4K.dxa       |
| Image720p   | Image720p_BACK.dxa     | Image720p.dxa     |
| Sound       | Sound_BACK.dxa         | Sound.dxa         |
