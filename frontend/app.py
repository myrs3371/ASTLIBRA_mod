import flet as ft
import os
from config import Config
from frontend.pages.home_page import HomePage
from frontend.pages.dialogue_page import DialoguePage
from frontend.pages.image_page import ImagePage
from frontend.pages.mod_page import ModPage
from backend.services.game_manager import GameManager
from backend.services.text_extractor import TextExtractor


class AstlibraModApp:
    """ASTLIBRA MOD 工具主应用"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "ASTLIBRA MOD 工具"
        self.page.window_width = 1280
        self.page.window_height = 800
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0

        self.game_manager = GameManager()

        self.home_page = HomePage()
        self.dialogue_page = DialoguePage()
        self.dialogue_page.page = page
        self.image_page = ImagePage()
        self.mod_page = ModPage()

        self.content_area = ft.Container(
            content=self.home_page.build(),
            expand=True,
            padding=20,
        )

        self.nav_rail = None

        self.auto_extract_on_startup()

    def auto_extract_on_startup(self):
        """启动时自动检测并解包"""
        # 首次启动：查找游戏目录
        if not self.game_manager.find_game_directory():
            self.show_error_dialog(
                "未找到游戏目录",
                "错误：未找到ASTLIBRA.exe或DATA文件夹\n\n请将工具放在游戏目录的子文件夹中\n程序将退出"
            )
            return

        game_path = self.game_manager.game_path

        # 检查CSV文件是否存在（第二次、第三次启动）
        csv_path = Config.get_extracted_texts_csv(game_path)
        if os.path.exists(csv_path):
            self.show_snackbar("已加载游戏文本数据", ft.colors.BLUE_400)
            return

        self.show_snackbar(f"找到游戏目录: {game_path}", ft.colors.BLUE_400)

        # 首次启动：执行完整解包流程
        self.show_extract_dialog(game_path)

    def show_extract_dialog(self, game_path: str):
        """显示文本提取进度对话框"""
        progress_text = ft.Text("正在检查文件...", size=16)
        progress_bar = ft.ProgressBar(width=400)

        dialog = ft.AlertDialog(
            title=ft.Text("首次启动", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    progress_text,
                    progress_bar,
                ], spacing=15, tight=True),
                width=400,
                height=100,
            ),
            modal=True,
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

        def extract():
            try:
                extractor = TextExtractor(game_path)

                # 步骤1: 检查文件
                progress_text.value = "正在检查文件..."
                self.page.update()
                success, message = extractor.check_files()
                if not success:
                    raise Exception(message)

                # 步骤2: 解包DAT.dxa
                progress_text.value = "正在解包 DAT.dxa..."
                self.page.update()
                success, message = extractor.unpack_dat_dxa()
                if not success:
                    raise Exception(message)

                # 步骤3: 修改EXE
                progress_text.value = "正在修改 EXE 文件..."
                self.page.update()
                success, message = extractor.patch_exe()
                if not success:
                    raise Exception(message)

                # 步骤4: 提取文本
                progress_text.value = "正在提取文本..."
                self.page.update()
                success, message = extractor.extract_texts()
                if not success:
                    raise Exception(message)

                # 步骤5: 打包为DAT
                progress_text.value = "正在打包为 DAT 文件..."
                self.page.update()
                success, message = extractor.pack_to_dat()
                if not success:
                    raise Exception(message)

                dialog.open = False
                self.page.update()
                self.show_snackbar("文本提取成功！", ft.colors.GREEN_400)

                self.dialogue_page = DialoguePage()
                self.dialogue_page.page = self.page

            except Exception as e:
                dialog.open = False
                self.page.update()
                self.show_snackbar(f"提取失败: {str(e)}", ft.colors.RED_400)

        import threading
        thread = threading.Thread(target=extract)
        thread.start()

    def show_error_dialog(self, title: str, message: str):
        """显示错误对话框并退出"""
        dialog = ft.AlertDialog(
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Icon(ft.icons.ERROR_OUTLINE, color=ft.colors.RED_400, size=64),
                        alignment=ft.alignment.center,
                        padding=ft.padding.only(bottom=20),
                    ),
                    ft.Text(
                        title,
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.RED_400,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        message,
                        size=15,
                        color=ft.colors.GREY_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=30),
                    ft.Container(
                        content=ft.ElevatedButton(
                            "退出程序",
                            icon=ft.icons.CLOSE,
                            on_click=lambda _: self.page.window_close(),
                            bgcolor=ft.colors.RED_400,
                            color=ft.colors.WHITE,
                            width=200,
                            height=45,
                        ),
                        alignment=ft.alignment.center,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
                padding=30,
                width=500,
            ),
            modal=True,
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_snackbar(self, message: str, bgcolor):
        """显示提示消息"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=bgcolor,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def build(self):
        """构建主界面"""
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.HOME_OUTLINED,
                    selected_icon=ft.icons.HOME,
                    label="主页"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.CHAT_OUTLINED,
                    selected_icon=ft.icons.CHAT,
                    label="对话文本"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.IMAGE_OUTLINED,
                    selected_icon=ft.icons.IMAGE,
                    label="图像模型"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.EXTENSION_OUTLINED,
                    selected_icon=ft.icons.EXTENSION,
                    label="MOD管理"
                ),
            ],
            on_change=self.on_nav_change,
        )

        self.page.add(
            ft.Row(
                [
                    self.nav_rail,
                    ft.VerticalDivider(width=1),
                    self.content_area,
                ],
                expand=True,
                spacing=0,
            )
        )

    def on_nav_change(self, e):
        """导航切换事件"""
        index = e.control.selected_index

        if index == 0:
            self.content_area.content = self.home_page.build()
        elif index == 1:
            self.content_area.content = self.dialogue_page.build()
        elif index == 2:
            self.content_area.content = self.image_page.build()
        elif index == 3:
            self.content_area.content = self.mod_page.build()

        self.page.update()
