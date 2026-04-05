"""pywebview JavaScript API bridge"""
import os
import shutil
import threading
import pandas as pd
import webview
from config import Config
from backend.services.game_manager import GameManager
from backend.services.mod_manager import ModManager
from backend.services.text_extractor import TextExtractor
from backend.services.text_importer import TextImporter
from core.read_csv import read_csv


class Api:
    def __init__(self):
        self._window = None
        self._game_manager = GameManager()
        self._mod_manager = None
        self._extraction_status = {
            "step": "", "done": False, "success": False, "error": None
        }
        self._mod_status = {
            "step": "", "done": False, "success": False, "error": None
        }
        if self._game_manager.find_game_directory():
            self._mod_manager = ModManager(self._game_manager.game_path)

    def set_window(self, window):
        self._window = window

    # ── Game info ────────────────────────────────────────────────────────────

    def get_game_info(self):
        detected = self._game_manager.find_game_directory()
        game_path = self._game_manager.game_path if detected else None
        has_csv = False
        if game_path:
            has_csv = os.path.exists(Config.get_extracted_texts_csv(game_path))
        return {"detected": detected, "game_path": game_path, "has_csv": has_csv}

    # ── Extraction ───────────────────────────────────────────────────────────

    def start_extraction(self):
        if not self._game_manager.game_path:
            return {"started": False, "error": "未找到游戏目录"}
        self._extraction_status = {
            "step": "正在初始化...", "done": False, "success": False, "error": None
        }
        threading.Thread(target=self._do_extraction, daemon=True).start()
        return {"started": True}

    def _do_extraction(self):
        game_path = self._game_manager.game_path
        extractor = TextExtractor(game_path)
        steps = [
            ("正在检查文件...", extractor.check_files),
            ("正在解包 DAT.dxa...", extractor.unpack_dat_dxa),
            ("正在修改 EXE 文件...", extractor.patch_exe),
            ("正在提取文本...", extractor.extract_texts),
            ("正在打包为 DAT 文件...", extractor.pack_to_dat),
        ]
        for step_name, step_fn in steps:
            self._extraction_status["step"] = step_name
            try:
                ok, msg = step_fn()
                if not ok:
                    self._extraction_status = {
                        "step": step_name, "done": True, "success": False, "error": msg
                    }
                    return
            except Exception as e:
                self._extraction_status = {
                    "step": step_name, "done": True, "success": False, "error": str(e)
                }
                return
        self._extraction_status = {
            "step": "完成", "done": True, "success": True, "error": None
        }
        if not self._mod_manager:
            self._mod_manager = ModManager(game_path)

    def get_extraction_status(self):
        return dict(self._extraction_status)

    # ── Texts ────────────────────────────────────────────────────────────────

    def get_texts(self, page=0, page_size=50, search="", category="all"):
        try:
            df = read_csv(with_classification=True)
            items = []
            for i, (_, row) in enumerate(df.iterrows()):
                items.append({
                    "id": i,
                    "offset": int(row["Offset_start"]) if not pd.isna(row["Offset_start"]) else 0,
                    "zh_cn": str(row["ZH_CN"]) if not pd.isna(row["ZH_CN"]) else "",
                    "category": row.get("Category", "other"),
                    "category_name": row.get("Category_Name", "其他"),
                })
            if category != "all":
                items = [r for r in items if r["category"] == category]
            if search:
                s = search.lower()
                items = [r for r in items if s in r["zh_cn"].lower()]
            total = len(items)
            pages = max(1, (total + page_size - 1) // page_size)
            start = int(page) * int(page_size)
            return {"items": items[start:start + int(page_size)], "total": total, "pages": pages}
        except Exception as e:
            return {"items": [], "total": 0, "pages": 1, "error": str(e)}

    def update_text(self, offset, new_text):
        try:
            game_path = Config.get_game_path()
            if not game_path:
                return {"ok": False, "error": "未找到游戏目录"}
            csv_path = Config.get_extracted_texts_csv(game_path)
            df = pd.read_csv(
                csv_path, encoding="utf-8",
                names=["id_текста", "Offset_start", "JPN", "US", "ZH_CN", "ZH_TW", "KO", "ES", ""]
            )
            df["Offset_start"] = pd.to_numeric(df["Offset_start"], errors="coerce").fillna(0).astype(int)
            df.loc[df["Offset_start"] == int(offset), "ZH_CN"] = new_text
            df.to_csv(csv_path, index=False, encoding="utf-8", quoting=1, header=False)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def apply_changes(self):
        try:
            game_path = Config.get_game_path()
            if not game_path:
                return {"ok": False, "msg": "未找到游戏目录"}
            ok, msg = TextImporter(game_path).apply_changes()
            return {"ok": ok, "msg": msg}
        except Exception as e:
            return {"ok": False, "msg": str(e)}

    def restore_original(self):
        try:
            game_path = Config.get_game_path()
            if not game_path:
                return {"ok": False, "msg": "未找到游戏目录"}
            ok, msg = TextImporter(game_path).restore_original()
            return {"ok": ok, "msg": msg}
        except Exception as e:
            return {"ok": False, "msg": str(e)}

    def export_localize_dat(self):
        try:
            game_path = Config.get_game_path()
            if not game_path:
                return {"ok": False, "msg": "未找到游戏目录"}
            src = os.path.join(Config.get_dat_folder(game_path), "LOCALIZE_.DAT")
            if not os.path.exists(src):
                return {"ok": False, "msg": "LOCALIZE_.DAT 不存在，请先提取或应用文本"}
            result = self._window.create_file_dialog(
                webview.SAVE_DIALOG,
                directory=os.path.expanduser("~"),
                save_filename="LOCALIZE_.DAT",
            )
            if not result:
                return {"ok": False, "msg": "已取消"}
            dest = result[0] if isinstance(result, (list, tuple)) else result
            shutil.copy2(src, dest)
            return {"ok": True, "msg": f"已导出到 {dest}"}
        except Exception as e:
            return {"ok": False, "msg": str(e)}

    # ── MODs ─────────────────────────────────────────────────────────────────

    def get_mods(self):
        if not self._mod_manager:
            return []
        try:
            mods = self._mod_manager.scan_mods()
            return mods
        except Exception:
            return []

    def activate_mods(self, folder_names):
        """批量激活MOD - 后台线程执行，前端轮询 get_mod_status() 获取进度"""
        if not self._mod_manager:
            return {"ok": False, "msg": "MOD管理器未初始化"}
        if not folder_names or len(folder_names) == 0:
            return {"ok": False, "msg": "请选择要激活的MOD"}
        self._mod_status = {"step": "正在准备...", "done": False, "success": False, "error": None}
        threading.Thread(target=self._do_activate_mods, args=(folder_names,), daemon=True).start()
        return {"ok": True, "msg": "started"}

    def _do_activate_mods(self, folder_names):
        def on_step(step: str):
            self._mod_status["step"] = step

        ok, msg = self._mod_manager.activate_mods(folder_names, status_callback=on_step)
        self._mod_status = {
            "step": "完成" if ok else self._mod_status["step"],
            "done": True,
            "success": ok,
            "error": None if ok else msg,
        }

    def get_mod_status(self):
        return dict(self._mod_status)


    def restore_all_mods(self):
        """还原原版 - 删除游戏文件夹并重新解压备份"""
        if not self._mod_manager:
            return {"ok": False, "msg": "MOD管理器未初始化"}
        ok, msg = self._mod_manager.restore_all()
        return {"ok": ok, "msg": msg}

    def restore_all_files(self):
        """一键还原：还原游戏 EXE + 所有游戏数据文件"""
        try:
            game_path = Config.get_game_path()
            if not game_path:
                return {"ok": False, "msg": "未找到游戏目录"}
            results = []

            # 还原 EXE
            exe_path = Config.get_exe_file(game_path)
            base, ext = os.path.splitext(exe_path)
            exe_backup = base + '_back' + ext
            if os.path.exists(exe_backup):
                shutil.copy2(exe_backup, exe_path)
                results.append("EXE 已还原")
            else:
                results.append("EXE 备份不存在，跳过")

            # 还原游戏数据文件
            if self._mod_manager:
                _, msg = self._mod_manager.restore_all()
                results.append(msg)
            else:
                results.append("游戏数据文件还原跳过（MOD管理器未初始化）")

            return {"ok": True, "msg": "；".join(results)}
        except Exception as e:
            return {"ok": False, "msg": str(e)}

    def delete_mod(self, folder_name):
        """删除MOD（停用就是删除）"""
        if not self._mod_manager:
            return {"ok": False, "msg": "MOD管理器未初始化"}
        ok, msg = self._mod_manager.delete_mod(folder_name)
        return {"ok": ok, "msg": msg}
