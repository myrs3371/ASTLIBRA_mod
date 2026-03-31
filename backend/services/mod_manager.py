"""MOD管理服务"""
import os
import json
import shutil
import subprocess
from datetime import datetime
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

        改进的激活机制：
        1. 首次激活时，将原文件备份为 .original 后缀（永久保留）
        2. 后续激活时，直接覆盖当前文件
        3. 支持多个MOD同时激活
        """
        if not mod_folder_names:
            return False, "未选择任何MOD"

        total_files = 0
        activated_mods = []

        try:
            for mod_folder_name in mod_folder_names:
                mod_path = os.path.join(self.mods_dir, mod_folder_name)

                if not os.path.exists(mod_path):
                    print(f"警告: MOD文件夹不存在 {mod_path}")
                    continue

                # 读取MOD信息（如果有）
                mod_info_path = os.path.join(mod_path, "mod_info.json")
                mod_files = []

                if os.path.exists(mod_info_path):
                    try:
                        with open(mod_info_path, 'r', encoding='utf-8') as f:
                            mod_info = json.load(f)
                            mod_files = mod_info.get('files', [])
                    except Exception as e:
                        print(f"读取MOD信息失败 {mod_folder_name}: {e}")

                # 如果没有files信息，扫描MOD文件夹中的所有文件
                if not mod_files:
                    mod_files = self._scan_mod_files(mod_path)

                # 复制文件
                activated_files = []
                for file_path in mod_files:
                    # MOD文件路径
                    mod_file = os.path.join(mod_path, file_path)
                    if not os.path.exists(mod_file):
                        print(f"警告: MOD文件不存在 {mod_file}")
                        continue

                    # 游戏文件路径（移除DATA/前缀）
                    relative_path = file_path.replace('DATA/', '').replace('DATA\\', '')
                    game_file = os.path.join(self.game_path, relative_path)

                    # 首次激活时创建 .original 备份
                    original_backup = game_file + '.original'
                    if os.path.exists(game_file) and not os.path.exists(original_backup):
                        shutil.copy2(game_file, original_backup)

                    # 复制MOD文件到游戏目录
                    os.makedirs(os.path.dirname(game_file), exist_ok=True)
                    shutil.copy2(mod_file, game_file)
                    activated_files.append(relative_path)
                    total_files += 1

                if activated_files:
                    activated_mods.append({
                        'name': mod_folder_name,
                        'activated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'files': activated_files
                    })

            if not activated_mods:
                return False, "没有找到可激活的MOD文件"

            # 记录到激活列表
            active_mods = self.get_active_mods()
            active_mods.extend(activated_mods)
            self._save_active_mods(active_mods)

            return True, f"成功激活 {len(activated_mods)} 个MOD，共 {total_files} 个文件"

        except Exception as e:
            return False, f"激活MOD失败: {e}"

    def _scan_mod_files(self, mod_path: str) -> List[str]:
        """扫描MOD文件夹中的所有文件，返回相对路径列表"""
        files = []
        for root, _, filenames in os.walk(mod_path):
            for filename in filenames:
                if filename == 'mod_info.json':
                    continue
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, mod_path)
                files.append(rel_path.replace('\\', '/'))
        return files

    def activate_mod(self, mod_folder_name: str) -> Tuple[bool, str]:
        """激活单个MOD（保留兼容性）"""
        return self.activate_mods([mod_folder_name])

    def deactivate_mod(self, mod_folder_name: str) -> Tuple[bool, str]:
        """停用MOD - 根据CLAUDE.md规范，停用就是删除MOD"""
        return self.delete_mod(mod_folder_name)

    def restore_all(self) -> Tuple[bool, str]:
        """还原所有原版文件 - 删除游戏文件夹并重新解压备份文件"""
        try:
            # 需要删除的文件夹列表（根据CLAUDE.md规范）
            folders_to_delete = ['DAT', 'Image', 'Image2K', 'Sound', 'Image4K', 'Image720p']

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

    def create_mod(self, name: str, description: str, author: str, files: List[str]) -> Tuple[bool, str]:
        """创建新MOD

        Args:
            name: MOD名称
            description: MOD描述
            author: 作者
            files: 文件路径列表（相对于游戏目录）
        """
        # 生成文件夹名（移除特殊字符）
        folder_name = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        mod_path = os.path.join(self.mods_dir, folder_name)

        if os.path.exists(mod_path):
            return False, f"MOD已存在: {folder_name}"

        try:
            os.makedirs(mod_path, exist_ok=True)

            # 复制文件到MOD目录
            mod_files = []
            for file_path in files:
                # 源文件（游戏目录）
                src_file = os.path.join(self.game_path, file_path)
                if not os.path.exists(src_file):
                    print(f"警告: 文件不存在 {src_file}")
                    continue

                # 目标文件（MOD目录，保持DATA/结构）
                dst_file = os.path.join(mod_path, 'DATA', file_path)
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                shutil.copy2(src_file, dst_file)
                mod_files.append(f"DATA/{file_path}")

            # 创建mod_info.json
            mod_info = {
                'name': name,
                'version': '1.0',
                'author': author,
                'description': description,
                'files': mod_files,
                'created_at': datetime.now().strftime('%Y-%m-%d')
            }

            mod_info_path = os.path.join(mod_path, 'mod_info.json')
            with open(mod_info_path, 'w', encoding='utf-8') as f:
                json.dump(mod_info, f, ensure_ascii=False, indent=2)

            return True, f"成功创建MOD: {folder_name}"

        except Exception as e:
            return False, f"创建MOD失败: {e}"

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

    def get_mod_info(self, mod_folder_name: str) -> Optional[Dict]:
        """获取MOD信息"""
        mod_info_path = os.path.join(self.mods_dir, mod_folder_name, 'mod_info.json')

        if not os.path.exists(mod_info_path):
            return None

        try:
            with open(mod_info_path, 'r', encoding='utf-8') as f:
                mod_info = json.load(f)
                mod_info['folder_name'] = mod_folder_name
                return mod_info
        except Exception as e:
            print(f"读取MOD信息失败: {e}")
            return None



