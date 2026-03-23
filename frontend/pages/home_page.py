import flet as ft


class HomePage:
    """主页"""

    def build(self):
        """构建主页界面"""
        return ft.Column(
            [
                # 标题
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "ASTLIBRA MOD 工具",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "轻松制作和管理游戏 MOD",
                                size=16,
                                color=ft.colors.GREY_700,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=15,
                    ),
                    padding=ft.padding.only(top=30, bottom=50),
                ),

                # 功能卡片
                ft.Container(
                    content=ft.Row(
                        [
                            self._create_feature_card(
                                icon=ft.icons.CHAT,
                                title="对话文本编辑",
                                description="提取、编辑、导入游戏对话文本\n支持 6 种语言，12000+ 条对话",
                                color=ft.colors.BLUE,
                            ),
                            self._create_feature_card(
                                icon=ft.icons.IMAGE,
                                title="图像资源修改",
                                description="DIG 格式图像解码/编码\n支持 1/2/3/4 通道图像",
                                color=ft.colors.GREEN,
                            ),
                            self._create_feature_card(
                                icon=ft.icons.EXTENSION,
                                title="MOD 管理",
                                description="创建、激活、停用 MOD 包\n支持多 MOD 叠加和冲突检测",
                                color=ft.colors.ORANGE,
                            ),
                        ],
                        spacing=30,
                        wrap=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ),

                # 快速开始
                ft.Container(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "快速开始",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    "1. 点击左侧导航栏选择功能模块",
                                    size=14,
                                ),
                                ft.Text(
                                    "2. 对话文本：提取 DAT 文件，编辑后导入",
                                    size=14,
                                ),
                                ft.Text(
                                    "3. 图像资源：解码 DIG 为 PNG，编辑后编码回 DIG",
                                    size=14,
                                ),
                                ft.Text(
                                    "4. MOD 管理：创建 MOD 包，激活后即可在游戏中使用",
                                    size=14,
                                ),
                            ],
                            spacing=12,
                        ),
                        padding=25,
                        border_radius=10,
                    ),
                    padding=ft.padding.only(top=60),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _create_feature_card(self, icon, title, description, color):
        """创建功能卡片"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=48, color=color),
                    ft.Text(
                        title,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        description,
                        size=12,
                        color=ft.colors.GREY_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            ),
            width=280,
            padding=35,
            border_radius=10,
            bgcolor=ft.colors.SURFACE_VARIANT,
        )
