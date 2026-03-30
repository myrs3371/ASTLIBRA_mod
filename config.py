"""项目配置模块"""
import os
import sys


class Config:
    """项目配置类"""

    # 项目根目录
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    # 核心目录
    CORE_DIR = os.path.join(PROJECT_ROOT, 'core')

    # ALOC工具路径
    ALOC_TOOL = os.path.join(CORE_DIR, '_ALOC.py')

    # ASTLIBRA_DEC工具路径
    ASTLIBRA_DEC = os.path.join(CORE_DIR, 'ASTLIBRA_Dec.exe')

    @classmethod
    def get_game_path(cls):
        """查找游戏目录"""
        if getattr(sys, 'frozen', False):
            current_dir = os.path.dirname(os.path.abspath(sys.executable))
        else:
            current_dir = cls.PROJECT_ROOT

        if cls._check_game_files(current_dir):
            return current_dir
        return None

    @classmethod
    def _check_game_files(cls, path):
        """检查游戏文件是否存在"""
        exe_path = os.path.join(path, 'ASTLIBRA.exe')
        data_dir = os.path.join(path, 'DATA')
        return os.path.exists(exe_path) and os.path.isdir(data_dir)

    @classmethod
    def get_exe_file(cls, game_path):
        """获取游戏EXE文件路径"""
        return os.path.join(game_path, 'ASTLIBRA.exe')

    @classmethod
    def get_data_dir(cls, game_path):
        """获取DATA目录"""
        return os.path.join(game_path, 'DATA')

    @classmethod
    def get_dat_file(cls, game_path):
        """获取DAT.dxa文件路径"""
        return os.path.join(cls.get_data_dir(game_path), 'DAT.dxa')

    @classmethod
    def get_dat_backup_file(cls, game_path):
        """获取DAT_BACK.dxa备份文件路径"""
        return os.path.join(cls.get_data_dir(game_path), 'DAT_BACK.dxa')

    @classmethod
    def get_dat_folder(cls, game_path):
        """获取解包后的DAT文件夹路径"""
        return os.path.join(cls.get_data_dir(game_path), 'DAT')

    @classmethod
    def get_extracted_texts_csv(cls, game_path):
        """获取提取的文本CSV文件路径（在用户DAT文件夹下）"""
        return os.path.join(cls.get_dat_folder(game_path), '_extracted_texts.csv')

    @classmethod
    def get_patch_exe_script(cls):
        """获取patch_exe.py脚本路径"""
        return os.path.join(cls.CORE_DIR, 'patch_exe.py')

    @classmethod
    def get_mods_dir(cls, game_path):
        """获取MODS目录"""
        return os.path.join(game_path, 'MODS')

