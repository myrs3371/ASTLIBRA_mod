import flet as ft


class ImagePage:
    """图像资源编辑页面"""

    def __init__(self):
        # 模拟文件树数据
        self.mock_files = [
            "Image/Char/NPC1.dig",
            "Image/Char/NPC2.dig",
            "Image/Accesory/Equip/ARMOR/item001.dig",
            "Image2K/Char/NPC1.dig",
            "Image2K/Accesory/Equip/ARMOR/item001.dig",
        ]
        self.selected_file = None

    def build(self):
        """构建图像页面"""
        # 文件树
        file_tree = ft.ListView(
            controls=[
                ft.ListTile(
                    leading=ft.Icon(ft.icons.FOLDER),
                    title=ft.Text("Image/"),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.IMAGE),
                    title=ft.Text("  Char/NPC1.dig"),
                    on_click=lambda e, f="Image/Char/NPC1.dig": self.on_file_select(e, f),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.IMAGE),
                    title=ft.Text("  Char/NPC2.dig"),
                    on_click=lambda e, f="Image/Char/NPC2.dig": self.on_file_select(e, f),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.FOLDER),
                    title=ft.Text("Image2K/"),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.IMAGE),
                    title=ft.Text("  Char/NPC1.dig"),
                    on_click=lambda e, f="Image2K/Char/NPC1.dig": self.on_file_select(e, f),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.FOLDER),
                    title=ft.Text("Image4K/"),
                ),
            ],
            expand=True,
        )

        # 图像预览区
        preview_area = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(
                            ft.icons.IMAGE_OUTLINED,
                            size=100,
                            color=ft.colors.GREY_400,
                        ),
                        alignment=ft.alignment.center,
                        height=400,
                        border=ft.border.all(2, ft.colors.GREY_300),
                        border_radius=10,
                    ),
                    ft.Text(
                        "选择一个 DIG 文件以预览",
                        size=14,
                        color=ft.colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            expand=True,
            padding=20,
        )

        # 文件信息和操作面板
        info_panel = ft.Container(
            content=ft.Column(
                [
                    ft.Text("文件信息", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text("文件路径:", weight=ft.FontWeight.BOLD),
                    ft.Text("未选择文件", size=12, color=ft.colors.GREY_600),
                    ft.Divider(),
                    ft.Text("图像属性:", weight=ft.FontWeight.BOLD),
                    ft.Row([ft.Text("宽度:", size=12), ft.Text("-", size=12)]),
                    ft.Row([ft.Text("高度:", size=12), ft.Text("-", size=12)]),
                    ft.Row([ft.Text("通道数:", size=12), ft.Text("-", size=12)]),
                    ft.Divider(),
                    ft.Text("操作", weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(
                        "解码为 PNG",
                        icon=ft.icons.ARROW_FORWARD,
                        width=200,
                        on_click=self.on_decode,
                    ),
                    ft.ElevatedButton(
                        "编码为 DIG",
                        icon=ft.icons.ARROW_BACK,
                        width=200,
                        on_click=self.on_encode,
                    ),
                    ft.ElevatedButton(
                        "批量解码",
                        icon=ft.icons.FOLDER_OPEN,
                        width=200,
                        on_click=self.on_batch_decode,
                    ),
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=250,
            padding=20,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=10,
        )

        # 主布局
        return ft.Column(
            [
                ft.Text("图像资源编辑", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("文件浏览", weight=ft.FontWeight.BOLD),
                                    ft.Container(
                                        content=file_tree,
                                        border=ft.border.all(1, ft.colors.GREY_400),
                                        border_radius=10,
                                        padding=10,
                                        expand=True,
                                    ),
                                ],
                                spacing=10,
                            ),
                            width=300,
                        ),
                        ft.VerticalDivider(),
                        preview_area,
                        ft.VerticalDivider(),
                        info_panel,
                    ],
                    expand=True,
                    spacing=10,
                ),
            ],
            expand=True,
            spacing=10,
        )

    def on_file_select(self, e, file_path):
        """选择文件"""
        self.selected_file = file_path

    def on_decode(self, e):
        """解码 DIG 为 PNG"""
        if not self.selected_file:
            # TODO: 显示提示
            pass

    def on_encode(self, e):
        """编码 PNG 为 DIG"""
        # TODO: 实现编码功能
        pass

    def on_batch_decode(self, e):
        """批量解码"""
        # TODO: 实现批量解码功能
        pass
