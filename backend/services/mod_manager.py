"""MOD管理服务"""
import os
import json
import shutil
import subprocess
from typing import List, Dict, Tuple, Optional
from config import Config
from core.patch_exe import patch_exe


class ModManager:
    """MOD管理器 - 负责MOD的扫描、激活、停用等操作"""

    def __init__(self, game_path: str):
        self.game_path = game_path
        self.mods_dir = Config.get_mods_dir(game_path)
        self.data_dir = Config.get_data_dir(game_path)
        self.active_mods_file = os.path.join(self.mods_dir, 'active_mods.json')

        # 确保目录存在
        os.makedirs(self.mods_dir, exist_ok=True)
    
    def scan_mods(self) -> List[Dict]:
        """扫描MODS目录，返回所有MOD信息列表"""
        mods = []

        if not os.path.exists(self.mods_dir):
            return mods

        for item in os.listdir(self.mods_dir):
            mod_path = os.path.join(self.mods_dir, item)

            # 跳过文件，只处理文件夹
            if not os.path.isdir(mod_path):
                continue

            # 读取mod_info.json
            mod_info_path = os.path.join(mod_path, "mod_info.json")
            if os.path.exists(mod_info_path):
                try:
                    with open(mod_info_path, 'r', encoding='utf-8') as f:
                        mod_info = json.load(f)
                        mod_info['folder_name'] = item
                        mods.append(mod_info)
                except Exception as e:
                    print(f"读取MOD信息失败 {item}: {e}")
                    # 读取失败时使用文件夹名称
                    mods.append({
                        'name': item,
                        'folder_name': item,
                        'version': '未知',
                        'author': '未知',
                        'description': '',
                    })
            else:
                # 没有mod_info.json时使用文件夹名称
                mods.append({
                    'name': item,
                    'folder_name': item,
                    'version': '未知',
                    'author': '未知',
                    'description': '',
                    'files': []
                })

        return mods

    def get_active_mods(self) -> List[Dict]:
        """获取已激活的MOD列表（按激活顺序）"""
        if not os.path.exists(self.active_mods_file):
            return []

        try:
            with open(self.active_mods_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('mods', [])
        except Exception as e:
            print(f"读取激活MOD列表失败: {e}")
            return []

    def _save_active_mods(self, active_mods: List[Dict]):
        """保存激活MOD列表"""
        try:
            with open(self.active_mods_file, 'w', encoding='utf-8') as f:
                json.dump({'mods': active_mods}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存激活MOD列表失败: {e}")

    def is_mod_active(self, mod_name: str) -> bool:
        """检查MOD是否已激活"""
        active_mods = self.get_active_mods()
        return any(mod['name'] == mod_name for mod in active_mods)

    def activate_mods(self, mod_folder_names: List[str],
                      status_callback=None) -> Tuple[bool, str]:
        """批量激活MOD - 支持同时激活多个MOD

        MOD文件夹结构: MODS/MyMod/Image/xxx.png, MODS/MyMod/Sound/xxx.ogg 等
        激活时将MOD中的数据文件夹(Image, Sound, DAT等)复制到游戏目录

        status_callback(step: str) 可选，每个阶段开始时调用以上报进度
        """
        def report(step: str):
            print(step)
            if status_callback:
                status_callback(step)

        if not mod_folder_names:
            return False, "未选择任何MOD"
        try:
            # ── 1. 检测/修补游戏 EXE ────────────────────────────────────────
            report("正在检测游戏 EXE...")
            exe_path = Config.get_exe_file(self.game_path)
            patched_bytes = bytes([0x90, 0x90, 0x90, 0x8B, 0x41, 0xFC, 0xC1, 0xC8, 0x04, 0x90, 0x90, 0x90])
            with open(exe_path, 'rb') as f:
                exe_data = f.read()
            if patched_bytes not in exe_data:
                report("正在修补游戏 EXE...")
                patch_exe(exe_path)
            else:
                print("游戏EXE已修补，跳过")

            # ── 2. 把备份文件改回原版文件名 ──────────────────────────────────
            report("正在还原游戏备份文件...")
            for backup_file in Config.DATA_BACK_LIST:
                backup_path = os.path.join(self.data_dir, backup_file)
                if os.path.isfile(backup_path):
                    original_name = Config.DATA_GAME_LIST[Config.DATA_BACK_LIST.index(backup_file)]
                    original_path = os.path.join(self.data_dir, original_name)
                    os.rename(backup_path, original_path)

            # ── 3. 删除所有游戏数据文件夹────────────────────────────────────
            report("正在清理旧版游戏数据...")
            for data_folder in Config.DATA_LIST:
                data_path = os.path.join(self.data_dir, data_folder)
                if os.path.isdir(data_path):
                    shutil.rmtree(data_path)

            # ── 4. 重新解压所有游戏原版 dxa 文件────────────────────────────
            report("正在解压原版游戏数据，请稍候...")
            for idx, data_folder in enumerate(Config.DATA_LIST):
                data_name = Config.DATA_GAME_LIST[idx]
                dxa_file = os.path.join(self.data_dir, data_name)
                if os.path.exists(dxa_file):
                    try:
                        subprocess.run(
                            [Config.ASTLIBRA_DEC, dxa_file],
                            cwd=self.data_dir,
                            capture_output=True,
                            timeout=300,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                    except Exception as e:
                        print(f"警告: 解压 {data_name} 失败: {e}")

            # ── 5. 复制 MOD 文件 ──────────────────────────────────────────────
            activated_count = 0
            for mod_folder_name in mod_folder_names:
                report(f"正在应用 MOD：{mod_folder_name}...")
                mod_path = os.path.join(self.mods_dir, mod_folder_name)
                if not os.path.exists(mod_path):
                    print(f"警告: MOD文件夹不存在 {mod_path}")
                    continue
                for data_folder in Config.DATA_LIST:
                    mod_data_path = os.path.join(mod_path, data_folder)
                    if os.path.exists(mod_data_path):
                        game_data_path = os.path.join(self.data_dir, data_folder)
                        shutil.copytree(mod_data_path, game_data_path, dirs_exist_ok=True)
                activated_count += 1

            # ── 6. 把原版 dxa 文件改回备份文件名 ─────────────────────────────
            report("正在重命名游戏文件为备份...")
            for file in Config.DATA_GAME_LIST:
                game_path = os.path.join(self.data_dir, file)
                if os.path.isfile(game_path):
                    back_name = Config.DATA_BACK_LIST[Config.DATA_GAME_LIST.index(file)]
                    back_path = os.path.join(self.data_dir, back_name)
                    os.rename(game_path, back_path)

            # ── 7. 重新打包 LOCALIZE_.DAT ────────────────────────────────────
            report("正在处理文本数据...")
            dat_folder = Config.get_dat_folder(self.game_path)
            aloc_tool = os.path.join(Config.CORE_DIR, '_ALOC.py')
            localize_dec = os.path.join(Config.CORE_DIR, 'LOCALIZE_.DAT_dec')

            # 检查是否有 MOD 提供了 DAT 文件夹（含文本替换）
            mod_has_dat = any(
                os.path.exists(os.path.join(self.mods_dir, name, 'DAT'))
                for name in mod_folder_names
            )
            if mod_has_dat:
                # MOD 自带 LOCALIZE_.DAT，已在第5步复制完毕，无需重新打包
                print("MOD 包含 DAT 文本文件，跳过重新打包")
            else:
                # 无文本 MOD：从 LOCALIZE_.DAT_dec 模板提取原版文本再打包
                # 确保 DAT 文件夹中始终有结构正确的 LOCALIZE_.DAT
                csv_temp = os.path.join(dat_folder, '_temp_localize.csv')
                try:
                    subprocess.run(
                        ['python', aloc_tool, localize_dec, csv_temp, '-e'],
                        cwd=dat_folder,
                        capture_output=True,
                        timeout=60,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    subprocess.run(
                        ['python', aloc_tool, localize_dec, csv_temp, '-p'],
                        cwd=dat_folder,
                        capture_output=True,
                        timeout=60,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    print("LOCALIZE_.DAT 重新打包成功")
                except Exception as e:
                    print(f"警告: 重新打包 LOCALIZE_.DAT 失败: {e}")
                finally:
                    if os.path.exists(csv_temp):
                        os.remove(csv_temp)

            return True, f"成功激活 {activated_count} 个MOD"
        except Exception as e:
            return False, f"激活MOD失败: {e}"

    def restore_all(self) -> Tuple[bool, str]:
        """还原所有原版文件 - 删除游戏文件夹并备份文件改名为原文件"""
        try:
            folders_to_delete = Config.DATA_LIST

            deleted_folders = []
            for folder_name in folders_to_delete:
                folder_path = os.path.join(self.data_dir, folder_name)
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
                    deleted_folders.append(folder_name)

            # 把备份的游戏文件改为原版文件
            for backup_file in Config.DATA_BACK_LIST:
                backup_path = os.path.join(self.data_dir, backup_file)
                if os.path.isfile(backup_path):
                    original_name = Config.DATA_GAME_LIST[Config.DATA_BACK_LIST.index(backup_file)]
                    original_path = os.path.join(self.data_dir, original_name)
                    os.rename(backup_path, original_path)

            # 清空激活列表
            self._save_active_mods([])

            return True, f"成功还原原版，已删除 {', '.join(deleted_folders)} 并恢复原版文件"

        except Exception as e:
            return False, f"还原失败: {e}"


    def delete_mod(self, mod_folder_name: str) -> Tuple[bool, str]:
        """删除MOD - 如果已激活则从激活列表中移除"""
        mod_path = os.path.join(self.mods_dir, mod_folder_name)
        if not os.path.exists(mod_path):
            return False, "MOD不存在"

        try:
            # 如果MOD已激活，从激活列表中移除
            if self.is_mod_active(mod_folder_name):
                active_mods = self.get_active_mods()
                active_mods = [m for m in active_mods if m['name'] != mod_folder_name]
                self._save_active_mods(active_mods)

            # 删除MOD文件夹
            shutil.rmtree(mod_path)
            return True, f"成功删除MOD: {mod_folder_name}"
        except Exception as e:
            return False, f"删除MOD失败: {e}"

