"""游戏路径查找和管理模块"""
import os
from config import Config


class GameManager:
    """游戏路径查找和管理"""

    def __init__(self):
        self.game_path = None
        self.data_dir = None

    def find_game_directory(self):
        """查找游戏目录"""
        self.game_path = Config.get_game_path()
        if self.game_path:
            self.data_dir = Config.get_data_dir(self.game_path)
            return True
        return False
