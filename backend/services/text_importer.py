"""文本导入和还原模块"""
import os
import subprocess
import shutil
from typing import Tuple
from config import Config


class TextImporter:
    """文本导入器"""

    def __init__(self, game_path: str):
        self.game_path = game_path
        self.data_dir = Config.get_data_dir(game_path)
        self.dat_folder = Config.get_dat_folder(game_path)
        self.aloc_tool = Config.ALOC_TOOL

        # core目录下的LOCALIZE_.DAT_dec文件
        self.localize_dec = os.path.join(Config.CORE_DIR, 'LOCALIZE_.DAT_dec')

        # 用户DAT文件夹下的CSV文件
        self.csv_file = Config.get_extracted_texts_csv(game_path)

        # 用户DAT文件夹下的LOCALIZE_.DAT文件
        self.localize_dat = os.path.join(self.dat_folder, 'LOCALIZE_.DAT')

    def apply_changes(self) -> Tuple[bool, str]:
        """应用按钮：使用_ALOC.py将修改后的CSV打包为LOCALIZE_.DAT"""
        if not os.path.exists(self.csv_file):
            return False, f"未找到CSV文件: {self.csv_file}"

        if not os.path.exists(self.aloc_tool):
            return False, f"未找到文本导入工具: {self.aloc_tool}"

        # 临时文件路径（在core目录）
        csv_temp = os.path.join(Config.CORE_DIR, '_temp_pack.csv')
        dat_temp = os.path.join(Config.CORE_DIR, 'LOCALIZE_.DAT')

        try:
            # 复制CSV到core目录
            shutil.copy2(self.csv_file, csv_temp)

            # 在core目录执行打包
            result = subprocess.run(
                ['python', '_ALOC.py', 'LOCALIZE_.DAT_dec', '_temp_pack.csv', '-p'],
                cwd=Config.CORE_DIR
            )

            if result.returncode != 0:
                return False, "应用修改失败"

            # 检查生成的DAT文件
            if not os.path.exists(dat_temp):
                return False, "未找到生成的LOCALIZE_.DAT文件"

            # 复制到用户DAT文件夹
            shutil.copy2(dat_temp, self.localize_dat)

            # 删除临时文件
            os.remove(csv_temp)
            os.remove(dat_temp)

            return True, "修改已成功应用"

        except Exception as e:
            # 清理临时文件
            if os.path.exists(csv_temp):
                os.remove(csv_temp)
            if os.path.exists(dat_temp):
                os.remove(dat_temp)
            return False, f"应用修改失败: {str(e)}"

    def restore_original(self) -> Tuple[bool, str]:
        """还原按钮：重新解包原始的LOCALIZE_.DAT_dec文件"""
        if not os.path.exists(self.aloc_tool):
            return False, f"未找到文本提取工具: {self.aloc_tool}"

        if not os.path.exists(self.localize_dec):
            return False, f"未找到LOCALIZE_.DAT_dec: {self.localize_dec}"

        # 临时CSV文件路径（在core目录）
        csv_temp = os.path.join(Config.CORE_DIR, '_temp_restore.csv')

        try:
            # 在core目录执行解包
            result = subprocess.run(
                ['python', '_ALOC.py', 'LOCALIZE_.DAT_dec', '_temp_restore.csv', '-e'],
                cwd=Config.CORE_DIR
            )

            if result.returncode != 0:
                return False, "还原失败"

            # 检查临时CSV是否生成
            if not os.path.exists(csv_temp):
                return False, "未找到生成的CSV文件"

            # 复制到用户DAT文件夹
            shutil.copy2(csv_temp, self.csv_file)

            # 将原始模板文件复制到用户DAT文件夹
            shutil.copy2(self.localize_dec, self.localize_dat)

            # 删除临时文件
            os.remove(csv_temp)

            return True, "已还原到原始状态"

        except Exception as e:
            # 清理临时文件
            if os.path.exists(csv_temp):
                os.remove(csv_temp)
            return False, f"还原失败: {str(e)}"
