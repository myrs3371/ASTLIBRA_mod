# 功能运行逻辑文档

本文档描述 ASTLIBRA MOD 工具各功能的内部运行逻辑，按用户操作流程组织。

---

## 1. 应用启动与初始化

**入口**: [main.py](main.py)

```
1. os.chdir(PROJECT_ROOT)              # 工作目录 = 游戏根目录
2. api = Api()                        # 创建桥接实例
3. tkinter 获取屏幕尺寸（用于居中）
4. pywebview.create_window(..., js_api=api)
   └─ new Api()
       ├─ new GameManager()
       │    └─ find_game_directory()  ← 立即检测并缓存游戏目录
       └─ if found: new ModManager(game_path)
5. api.set_window(window)             # 注入窗口引用（供导出对话框用）
6. webview.start()                    # 阻塞，运行事件循环
```

**工作目录耦合**: 所有相对路径以游戏根目录为基准。打包后 EXE 放在游戏根目录即可运行；源码模式需将仓库根目录设为游戏根目录。

**Vue 应用初始化**: [web/js/app.js](web/js/app.js)

`rootApp` 挂载 `#app`，三个页面组件（homePage / dialoguePage / modPage）通过动态组件 `<component :is>` 切换。`startup()` 在 `mounted()` 中调用 `get_game_info()` 检测游戏目录：
- `!gameDetected` → 全屏遮罩提示"未找到游戏目录"
- `gameDetected` → 正常进入主页（不自动触发提取）

首次提取由用户在"对话文本"页面手动触发：进入该页时若无 CSV（`noData=true`），页面中央显示"暂无文本数据"空状态及"开始提取文本"按钮；用户点击后弹出全屏进度遮罩。

---

## 2. 游戏目录检测

**入口**: [config.py](config.py) → `Config.get_game_path()`

```
get_game_path()
  ├─ frozen 模式 → 从 sys.executable 所在目录向上搜索
  └─ 源码模式   → 从 PROJECT_ROOT 向上搜索
       └─ _check_game_files(path)
            ├─ ASTLIBRA.exe 存在？
            └─ DATA/ 是目录？
```

搜索直到找到同时包含 `ASTLIBRA.exe` 和 `DATA/` 的目录。`GameManager.find_game_directory()` 缓存一次结果；`Config.get_game_path()` 每次重新检测（静态方法）。

---

## 3. 线程模型与状态轮询

所有耗时操作在**守护线程**中执行，主线程立即返回，前端通过**定时轮询**获取进度。

```
api._extraction_status = {step, done, success, error}   # 提取/导入状态
api._mod_status        = {step, done, success, error}   # MOD 激活状态
```

Python 端无锁写入 dict（字典赋值是原子的），前端每 500ms 调用一次 `get_extraction_status()` 或 `get_mod_status()`，收到 `done=true` 时停止。

---

## 4. 首次文本提取（5 步流水线）

**触发**: 用户在"对话文本"页点击"开始提取文本"

```
dialoguePage.triggerExtraction()
  └─ pywebview.api.start_extraction()
       ├─ 重置 _extraction_status
       └─ threading.Thread(target=_do_extraction, daemon=True).start()
            └─ _do_extraction() 顺序执行 5 个步骤
```

### 步骤 1 — 文件检查 `check_files()`

```
TextExtractor.check_files()
  ├─ ASTLIBRA.exe 存在？
  └─ DATA/ 是目录？
```

### 步骤 2 — 解包 DAT.dxa `unpack_dat_dxa()`

```
检查 DATA/DAT.dxa 存在？
  ├─ 不存在，但 DATA_BACK.dxa 存在 → 已解包过，跳过
  └─ 不存在且无备份 → 报错中断
shutil.rmtree(DATA/DAT/)（删除旧文件夹）
subprocess.run([ASTLIBRA_Dec.exe, DAT.dxa], cwd=DATA/)
  └─ CREATE_NO_WINDOW，不弹出控制台
DAT.dxa → DAT_BACK.dxa（重命名备份）
```

### 步骤 3 — 修补游戏 EXE `patch_exe()`

```
subprocess.run(['python', 'core/patch_exe.py', ASTLIBRA.exe], cwd=core/)
  └─ patch_exe.py:
       1. 读取 ASTLIBRA.exe 全部字节
       2. 搜索字节序列 → 替换为 NOP 指令
          查找: [0x89,0x41,0xF8,0x8B,0x41,0xFC,0xC1,0xC8,0x04,0x89,0x41,0xFC]
          替换: [0x90,0x90,0x90,0x8B,0x41,0xFC,0xC1,0xC8,0x04,0x90,0x90,0x90]
       3. shutil.copy2 → ASTLIBRA_back.exe（备份）
       4. 写入修改后的字节
```

将两条汇编指令 NOP 化，绕过游戏的文本资源校验，使游戏能读取解压后的文本文件。

### 步骤 4 — 提取文本 `extract_texts()`

```
subprocess.run([
    'python', '_ALOC.py', 'LOCALIZE_.DAT_dec',
    '_temp_extracted.csv', '-e'
], cwd=core/)
  └─ _ALOC.py -e（export）:
       读取 LOCALIZE_.DAT_dec（ALOC 二进制格式）
       解析索引块 → 6 个语言列偏移量
       latin-1 解码文本，换行符转为 [n_rn]/[n_nr]
       输出 CSV: id_текста, Offset_start, JPN, US, ZH_CN, ZH_TW, KO, ES
shutil.copy2(_temp_extracted.csv → DATA/DAT/_extracted_texts.csv)
os.remove(_temp_extracted.csv)
```

### 步骤 5 — 重新打包 LOCALIZE_.DAT `pack_to_dat()`

```
shutil.copy2(DATA/DAT/_extracted_texts.csv → core/_temp_pack.csv)
subprocess.run([
    'python', '_ALOC.py', 'LOCALIZE_.DAT_dec',
    '_temp_pack.csv', '-p'
], cwd=core/)
  └─ _ALOC.py -p（pack）:
       读取 LOCALIZE_.DAT_dec 头部（前 478776 字节固定不变）
       按 CSV 每行重建索引块（重新计算各语言偏移量）
       文本数据以 UTF-8 写入，每段按 8 字节对齐
       生成 core/LOCALIZE_.DAT
shutil.copy2(core/LOCALIZE_.DAT → DATA/DAT/LOCALIZE_.DAT)
os.remove(core/_temp_pack.csv)
os.remove(core/LOCALIZE_.DAT)
```

**ALOC 二进制格式**（[core/_ALOC.py](core/_ALOC.py)）:
- 头部 52 字节（`ALOC` 魔数 + 元数据）
- 索引块 10968 条（每条含 ID + 6 个语言偏移量，32 字节/条）
- 文本区从偏移 478776 开始，每段 8 字节对齐，不足补 `\x00`
- 模板文件 `core/LOCALIZE_.DAT_dec` 永不修改，作为只读输入

---

## 5. 文本编辑与保存

**触发**: 双击表格行 → 编辑框 → 保存

```
dialoguePage.openEditDialog(item)
  └─ editRow = { ...item }, editText = item.zh_cn

dialoguePage.saveEdit()
  └─ pywebview.api.update_text(offset, newText)
```

**后端逻辑**（[api.py](frontend/api.py) → `update_text()`）:

```python
df = pd.read_csv(csv_path, encoding="utf-8",
    names=["id_текста", "Offset_start", "JPN", "US",
           "ZH_CN", "ZH_TW", "KO", "ES", ""])
# 注意: header=0（默认），第一行 CSV 表头被当作数据行读入
df["Offset_start"] = pd.to_numeric(df["Offset_start"], errors="coerce")
df.loc[df["Offset_start"] == int(offset), "ZH_CN"] = new_text
df.to_csv(csv_path, index=False, encoding="utf-8", quoting=1, header=False)
```

仅修改 CSV 的 `ZH_CN` 列，`LOCALIZE_.DAT` **不变**——点"应用到游戏"后才写入 DAT 文件。

---

## 6. 文本应用到游戏

**触发**: 点击"应用到游戏"

```
dialoguePage.applyToGame()
  └─ pywebview.api.apply_changes()
       └─ TextImporter(game_path).apply_changes()
```

逻辑与提取步骤 5 相同：将最新 CSV 重新打包为 DAT，覆盖 `DATA/DAT/LOCALIZE_.DAT`。

---

## 7. 还原原始文本

**触发**: 点击"还原所有文本"

```
pywebview.api.restore_original()
  └─ TextImporter(game_path).restore_original()

subprocess.run([
    'python', '_ALOC.py', 'LOCALIZE_.DAT_dec', '_temp_restore.csv', '-e'
], cwd=core/)
shutil.copy2(_temp_restore.csv → DATA/DAT/_extracted_texts.csv)
shutil.copy2(LOCALIZE_.DAT_dec → DATA/DAT/LOCALIZE_.DAT)
os.remove(_temp_restore.csv)
```

从 `LOCALIZE_.DAT_dec` 模板重新导出原始 CSV，并用模板文件覆盖 DAT。**所有用户编辑丢失。**

---

## 8. 导出 LOCALIZE_.DAT

**触发**: 点击"导出 DAT"

```
pywebview.api.export_localize_dat()
  └─ _window.create_file_dialog(SAVE_DIALOG, save_filename="LOCALIZE_.DAT")
  └─ shutil.copy2(DATA/DAT/LOCALIZE_.DAT → 用户选择路径)
```

打开系统保存对话框，让用户指定导出位置。

---

## 9. MOD 扫描

**触发**: 进入"MOD 管理"页面时 `mounted()` 调用

```
pywebview.api.get_mods()
  └─ ModManager.scan_mods()
       ├─ 遍历 MODS/ 下所有子文件夹
       ├─ 读取 mod_info.json（如存在）
       └─ 缺失或解析失败 → 用文件夹名作为 name，填充默认字段
```

返回列表不含激活状态；`get_mods()` 另读取 `active_mods.json` 后补充 `is_active` 字段。

`mod_info.json` 标准字段: `name`, `version`, `author`, `description`, `files`

---

## 10. MOD 激活（7 步流水线）

**触发**: 勾选 MOD → 点击"激活勾选的 MOD"

```
modPage.activateMod()
  └─ pywebview.api.activate_mods(checkedMods)
       ├─ 重置 _mod_status
       └─ threading.Thread(target=_do_activate_mods, daemon=True).start()
            └─ _do_activate_mods()
                 └─ _mod_manager.activate_mods(folder_names, status_callback=on_step)
```

进度每 500ms 轮询一次 `get_mod_status()`。

### 步骤 1 — 检测/修补 EXE

```
读取 ASTLIBRA.exe
检查是否已包含修补后的字节序列
  ├─ 已修补 → 跳过
  └─ 未修补 → patch_exe()（同提取步骤 3）
```

### 步骤 2 — 备份文件改回原名

```
for each DATA_BACK_LIST item:
  DAT_BACK.dxa → DAT.dxa
```

### 步骤 3 — 删除游戏数据文件夹（仅 MOD 涉及的）

```
扫描所有选中 MOD 的子文件夹（Image, DAT, Sound 等）
收集 MOD 实际覆盖的文件夹集合
shutil.rmtree(DATA/xxx/)（仅删除覆盖到的文件夹）
```

仅删除 MOD 覆盖的文件夹，其他保持不动，实现多个 MOD 的共存。

### 步骤 4 — 从原版 dxa 重新解压（仅步骤 3 涉及的）

```
for each 被删除的文件夹对应的原版 dxa:
  subprocess.run([ASTLIBRA_Dec.exe, xxx.dxa], cwd=DATA/)
    └─ 超时 300s，跳过失败项
    └─ CREATE_NO_WINDOW
```

### 步骤 5 — 复制 MOD 文件覆盖

```
for each mod_folder_name:
  for each DATA_LIST item:
    if MODS/mod_name/DATA_LIST_item/ 存在:
      shutil.copytree(src, DATA/DATA_LIST_item/, dirs_exist_ok=True)
```

### 步骤 6 — 原版 dxa 改回备份名

```
for each DATA_GAME_LIST item:
  DAT.dxa → DAT_BACK.dxa
```

### 步骤 7 — 重新打包 LOCALIZE_.DAT

```
if 有 MOD 提供了 DAT/ 子文件夹:
  LOCALIZE_.DAT 已在步骤 5 复制，跳过
else:
  subprocess.run(['python', aloc_tool, localize_dec, temp.csv, '-e'], cwd=DATA/DAT/)
  subprocess.run(['python', aloc_tool, localize_dec, temp.csv, '-p'], cwd=DATA/DAT/)
  os.remove(temp.csv)
```

---

## 11. MOD 还原

**触发**: 点击"还原原版文件"

```
pywebview.api.restore_all_mods()
  └─ ModManager.restore_all()

shutil.rmtree(DATA/DAT/), shutil.rmtree(DATA/Image/), ...（删除所有游戏文件夹）
for each DATA_BACK_LIST item:
  DAT_BACK.dxa → DAT.dxa（重命名恢复）
_save_active_mods([])（清空激活列表）
```

删除**全部**游戏数据文件夹（不论来源），将备份 dxa 恢复为原名。**不重新执行解压**，游戏需要下次 MOD 激活时自动解压，或手动运行提取。

---

## 12. 一键还原

**触发**: 点击"一键还原 EXE 与游戏文件"

```
pywebview.api.restore_all_files()
  ├─ ASTLIBRA_back.exe → ASTLIBRA.exe（复制）
  └─ 删除 ASTLIBRA_back.exe（备份被消费）
  └─ _mod_manager.restore_all()
       └─ ModManager.restore_all()（同上）
```

EXE 备份被**消费式删除**，dxa 备份同样在重命名中被消费。所有原版文件通过重命名恢复，游戏需重新激活 MOD 才能运行。

---

## 13. MOD 删除

**触发**: 在 MOD 详情面板点击"删除此 MOD"

```
pywebview.api.delete_mod(folder_name)
  └─ ModManager.delete_mod(folder_name)

if 该 MOD 在 active_mods.json 中:
  从 active_mods.json 移除该 MOD
shutil.rmtree(MODS/folder_name/)
```

仅删除 MOD 文件夹，不影响已激活到游戏目录的文件。已在游戏中生效的 MOD 文件需通过"还原原版文件"恢复。

---

## 附录：关键数据结构

### CSV 文件格式
```
列: id_текста, Offset_start, JPN, US, ZH_CN, ZH_TW, KO, ES
换行符: [n_rn] = CRLF, [n_nr] = LF
注意: pandas 用 names=... 读取时，CSV 表头行被当作数据行
```

### active_mods.json
```json
{ "mods": [{ "name": "...", "folder_name": "...", ... }, ...] }
```

### mod_info.json
```json
{
  "name": "MOD名称",
  "version": "1.0",
  "author": "作者",
  "description": "描述",
  "files": ["Image/xxx.png", "DAT/LOCALIZE_.DAT"]
}
```

### 状态对象结构
```python
{ "step": "正在xxx...", "done": bool, "success": bool, "error": str|null }
```

### DATA_LIST 三表对照
| DATA_LIST  | DATA_BACK_LIST  | DATA_GAME_LIST |
|------------|-----------------|----------------|
| DAT        | DAT_BACK.dxa    | DAT.dxa        |
| Image      | Image_BACK.dxa  | Image.dxa      |
| Image2K    | Image2K_BACK.dxa| Image2K.dxa    |
| Image4K    | Image4K_BACK.dxa| Image4K.dxa    |
| Image720p  | Image720p_BACK.dxa| Image720p.dxa |
| Sound      | Sound_BACK.dxa  | Sound.dxa      |
