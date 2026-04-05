"""MOD管理服务"""
import os
import json
import shutil
import subprocess
from typing import List, Dict, Tuple, Optional
from config import Config


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

    def activate_mods(self, mod_folder_names: List[str]) -> Tuple[bool, str]:
        """批量激活MOD - 支持同时激活多个MOD

        MOD文件夹结构: MODS/MyMod/Image/xxx.png, MODS/MyMod/Sound/xxx.ogg 等
        激活时将MOD中的数据文件夹(Image, Sound, DAT等)复制到游戏目录
        """
        if not mod_folder_names:
            return False, "未选择任何MOD"
        try:
            # 如果备份的游戏文件存在就把改为原版文件
            for backup_file in Config.DATA_BACK_LIST:
                backup_path = os.path.join(self.data_dir, backup_file)
                print(backup_path)
                if os.path.isfile(backup_path):
                    original_name = Config.DATA_GAME_LIST[Config.DATA_BACK_LIST.index(backup_file)]
                    original_path = os.path.join(self.data_dir, original_name)
                    os.rename(backup_path, original_path)
            # 递归删除游戏目录下的文件
            for mod_dir in Config.DATA_LIST:
                if os.path.isdir(os.path.join(self.data_dir, mod_dir)):
                    shutil.rmtree(os.path.join(self.data_dir, mod_dir))
            # 重新解压游戏文件
            for data_name in Config.DATA_GAME_LIST:
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
            activated_count = 0
            for mod_folder_name in mod_folder_names:
                mod_path = os.path.join(self.mods_dir, mod_folder_name)
                if not os.path.exists(mod_path):
                    print(f"警告: MOD文件夹不存在 {mod_path}")
                    continue
                # 遍历MOD文件夹中的所有数据子文件夹(Image, Sound, DAT等)
                for data_folder in Config.DATA_LIST:
                    mod_data_path = os.path.join(mod_path, data_folder)
                    if os.path.exists(mod_data_path):
                        game_data_path = os.path.join(self.data_dir, data_folder)
                        shutil.copytree(mod_data_path, game_data_path, dirs_exist_ok=True)
                activated_count += 1
            for file in Config.DATA_GAME_LIST:
                game_path = os.path.join(self.data_dir, file)
                if os.path.isfile(game_path):
                    back_name = Config.DATA_BACK_LIST[Config.DATA_GAME_LIST.index(file)]
                    back_path = os.path.join(self.data_dir, back_name)
                    os.rename(game_path, back_path)
            return True, f"成功激活 {activated_count} 个MOD"
        except Exception as e:
            return False, f"激活MOD失败: {e}"

    def restore_all(self) -> Tuple[bool, str]:
        """还原所有原版文件 - 删除游戏文件夹并重新解压备份文件"""
        try:
            folders_to_delete = Config.DATA_LIST

            deleted_folders = []
            for folder_name in folders_to_delete:
                folder_path = os.path.join(self.data_dir, folder_name)
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
                    deleted_folders.append(folder_name)

            # 检查是否存在 DAT_BACK.dxa 备份文件
            dat_backup = Config.get_dat_backup_file(self.game_path)
            if not os.path.exists(dat_backup):
                return False, "未找到备份文件 DAT_BACK.dxa，无法还原"

            # 使用 ASTLIBRA_Dec.exe 重新解压 DAT_BACK.dxa
            try:
                result = subprocess.run(
                    [Config.ASTLIBRA_DEC, dat_backup],
                    cwd=self.data_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分钟超时
                )

                if result.returncode != 0:
                    return False, f"解压备份文件失败: {result.stderr or '未知错误'}"

                # 检查是否生成了 DAT 文件夹
                dat_folder = Config.get_dat_folder(self.game_path)
                if not os.path.exists(dat_folder):
                    return False, "解压后未找到 DAT 文件夹"

            except subprocess.TimeoutExpired:
                return False, "解压备份文件超时（超过5分钟）"
            except Exception as e:
                return False, f"解压备份文件失败: {e}"

            # 清空激活列表
            self._save_active_mods([])

            return True, f"成功还原原版，已删除 {', '.join(deleted_folders)} 并重新解压"

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

