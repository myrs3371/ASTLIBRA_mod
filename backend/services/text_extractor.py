"""文本提取模块"""
import os
import subprocess
import shutil
from typing import Tuple
from config import Config

_NO_WINDOW = subprocess.CREATE_NO_WINDOW


class TextExtractor:
    """文本提取器"""

    def __init__(self, game_path: str):
        self.game_path = game_path
        self.data_dir = Config.get_data_dir(game_path)
        self.dat_folder = Config.get_dat_folder(game_path)
        self.exe_file = Config.get_exe_file(game_path)
        self.aloc_tool = Config.ALOC_TOOL
        self.patch_exe_script = Config.get_patch_exe_script()

        # core目录下的LOCALIZE_.DAT_dec文件
        self.localize_dec = os.path.join(Config.CORE_DIR, 'LOCALIZE_.DAT_dec')

        # 用户DAT文件夹下的CSV文件
        self.csv_output = Config.get_extracted_texts_csv(game_path)

    def check_files(self) -> Tuple[bool, str]:
        """步骤1: 检查exe文件和DATA文件夹"""
        if not os.path.exists(self.exe_file):
            return False, f"错误：未找到游戏EXE文件\n路径: {self.exe_file}"

        if not os.path.isdir(self.data_dir):
            return False, f"错误：未找到DATA文件夹\n路径: {self.data_dir}"

        return True, "文件检查通过"

    def unpack_dat_dxa(self) -> Tuple[bool, str]:
        """步骤2: 使用ASTLIBRA_Dec.exe解包DAT.dxa"""
        dat_file = Config.get_dat_file(self.game_path)
        dat_backup = Config.get_dat_backup_file(self.game_path)

        # 检查 DAT.dxa 是否存在
        if not os.path.exists(dat_file):
            # 检查是否已经解包过（DAT_BACK.dxa 存在）
            if os.path.exists(dat_backup):
                return True, "DAT.dxa 已解包"
            return False, "未找到 DAT.dxa 文件"

        # 如果 DAT 文件夹已存在，先删除
        if os.path.exists(self.dat_folder):
            try:
                shutil.rmtree(self.dat_folder)
            except Exception as e:
                return False, f"删除旧DAT文件夹失败: {str(e)}"

        # 解包 DAT.dxa
        try:
            result = subprocess.run(
                [Config.ASTLIBRA_DEC, dat_file],
                cwd=self.data_dir,
                capture_output=True,
                creationflags=_NO_WINDOW
            )

            if result.returncode != 0:
                return False, f"解包 DAT.dxa 失败: {result.stderr or result.stdout or '未知错误'}"

            # 检查是否生成了 DAT 文件夹
            if not os.path.exists(self.dat_folder):
                items = os.listdir(self.data_dir)
                return False, f"解包后未找到 DAT 文件夹\nDATA目录内容: {', '.join(items)}"

            # 将 DAT.dxa 改名为 DAT_BACK.dxa
            if os.path.exists(dat_backup):
                os.remove(dat_backup)
            os.rename(dat_file, dat_backup)

            return True, "DAT.dxa 解包成功"

        except subprocess.TimeoutExpired:
            return False, "解包 DAT.dxa 超时"
        except Exception as e:
            return False, f"解包 DAT.dxa 失败: {str(e)}"

    def patch_exe(self) -> Tuple[bool, str]:
        """步骤3: 使用patch_exe.py修改exe文件"""
        if not os.path.exists(self.patch_exe_script):
            return False, f"未找到patch_exe.py: {self.patch_exe_script}"

        try:
            result = subprocess.run(
                ['python', self.patch_exe_script, self.exe_file],
                cwd=Config.CORE_DIR,
                capture_output=True,
                creationflags=_NO_WINDOW
            )

            if result.returncode != 0:
                return False, f"修改EXE失败: {result.stderr or '未知错误'}"

            return True, "EXE修改成功"

        except subprocess.TimeoutExpired:
            return False, "修改EXE超时"
        except Exception as e:
            return False, f"修改EXE失败: {str(e)}"

    def extract_texts(self) -> Tuple[bool, str]:
        """步骤4: 使用_ALOC.py解包core下的LOCALIZE_.DAT_dec文件"""
        if not os.path.exists(self.aloc_tool):
            return False, f"未找到文本提取工具: {self.aloc_tool}"

        # 从core目录读取LOCALIZE_.DAT_dec模板
        if not os.path.exists(self.localize_dec):
            return False, f"未找到LOCALIZE_.DAT_dec: {self.localize_dec}"

        # 临时CSV文件路径（在core目录）
        csv_temp = os.path.join(Config.CORE_DIR, '_temp_extracted.csv')

        try:
            # 在core目录执行解包
            result = subprocess.run(
                ['python', '_ALOC.py', 'LOCALIZE_.DAT_dec', '_temp_extracted.csv', '-e'],
                cwd=Config.CORE_DIR,
                capture_output=True,
                creationflags=_NO_WINDOW
            )

            if result.returncode != 0:
                return False, "提取文本失败"

            # 检查临时CSV是否生成
            if not os.path.exists(csv_temp):
                return False, "未找到生成的CSV文件"

            # 复制到用户DAT文件夹
            shutil.copy2(csv_temp, self.csv_output)

            # 删除临时文件
            os.remove(csv_temp)

            return True, "文本提取成功"

        except Exception as e:
            # 清理临时文件
            if os.path.exists(csv_temp):
                os.remove(csv_temp)
            return False, f"提取文本失败: {str(e)}"

    def pack_to_dat(self) -> Tuple[bool, str]:
        """步骤5: 使用_ALOC.py将CSV打包为LOCALIZE_.DAT文件"""
        if not os.path.exists(self.csv_output):
            return False, f"未找到CSV文件: {self.csv_output}"

        # 临时文件路径（在core目录）
        csv_temp = os.path.join(Config.CORE_DIR, '_temp_pack.csv')
        dat_temp = os.path.join(Config.CORE_DIR, 'LOCALIZE_.DAT')
        localize_dat = os.path.join(self.dat_folder, 'LOCALIZE_.DAT')

        try:
            # 复制CSV到core目录
            shutil.copy2(self.csv_output, csv_temp)

            # 在core目录执行打包
            result = subprocess.run(
                ['python', '_ALOC.py', 'LOCALIZE_.DAT_dec', '_temp_pack.csv', '-p'],
                cwd=Config.CORE_DIR,
                capture_output=True,
                creationflags=_NO_WINDOW
            )

            if result.returncode != 0:
                return False, "打包失败"

            # 检查生成的DAT文件
            if not os.path.exists(dat_temp):
                return False, "未找到生成的LOCALIZE_.DAT文件"

            # 复制到用户DAT文件夹
            shutil.copy2(dat_temp, localize_dat)

            # 删除临时文件
            os.remove(csv_temp)
            os.remove(dat_temp)

            return True, "打包成功"

        except Exception as e:
            # 清理临时文件
            if os.path.exists(csv_temp):
                os.remove(csv_temp)
            if os.path.exists(dat_temp):
                os.remove(dat_temp)
            return False, f"打包失败: {str(e)}"
