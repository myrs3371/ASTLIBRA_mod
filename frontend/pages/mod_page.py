import flet as ft


class ModPage:
    """MOD 管理页面"""

    def __init__(self):
        # 模拟 MOD 数据
        self.mock_mods = [
            {
                "name": "Saber MOD",
                "enabled": True,
                "description": "将角色立绘替换为 Saber",
                "files": [
                    "Image2K/Char/NPC1.dig",
                    "Image2K/Accesory/Equip/ARMOR/item001.dig",
                    "Sound/SE/Voice/voice001.wav",
                ],
            },
            {
                "name": "中文字体 MOD",
                "enabled": False,
                "description": "优化中文字体显示效果",
                "files": ["Font/chinese.dft"],
            },
            {
                "name": "音效增强 MOD",
                "enabled": False,
                "description": "增强游戏音效",
                "files": ["Sound/SE/Battle/hit001.wav"],
            },
        ]
        self.selected_mod = self.mock_mods[0]

    def build(self):
        """构建 MOD 管理页面"""
        # MOD 列表
        mod_list = ft.ListView(
            controls=self._create_mod_list_items(),
            expand=True,
            spacing=5,
        )

        # MOD 详情面板
        detail_panel = ft.Container(
            content=ft.Column(
                [
                    ft.Text("MOD 详情", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text(
                        self.selected_mod["name"],
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        self.selected_mod["description"],
                        size=14,
                        color=ft.colors.GREY_700,
                    ),
                    ft.Divider(),
                    ft.Text("包含文件:", weight=ft.FontWeight.BOLD),
                    ft.ListView(
                        controls=[
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.INSERT_DRIVE_FILE, size=20),
                                title=ft.Text(file, size=12),
                            )
                            for file in self.selected_mod["files"]
                        ],
                        height=200,
                    ),
                    ft.Divider(),
                    ft.Text("操作", weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "编辑",
                                icon=ft.icons.EDIT,
                                on_click=self.on_edit_mod,
                            ),
                            ft.ElevatedButton(
                                "删除",
                                icon=ft.icons.DELETE,
                                on_click=self.on_delete_mod,
                            ),
                            ft.ElevatedButton(
                                "导出",
                                icon=ft.icons.UPLOAD,
                                on_click=self.on_export_mod,
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            padding=20,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=10,
        )

        # 主布局
        return ft.Column(
            [
                ft.Text("MOD 管理", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(
                                                "MOD 列表",
                                                weight=ft.FontWeight.BOLD,
                                                expand=True,
                                            ),
                                            ft.IconButton(
                                                icon=ft.icons.ADD,
                                                tooltip="创建新 MOD",
                                                on_click=self.on_create_mod,
                                            ),
                                        ]
                                    ),
                                    ft.Container(
                                        content=mod_list,
                                        border=ft.border.all(1, ft.colors.GREY_400),
                                        border_radius=10,
                                        padding=10,
                                        expand=True,
                                    ),
                                    ft.Divider(),
                                    ft.ElevatedButton(
                                        "激活选中的 MOD",
                                        icon=ft.icons.PLAY_ARROW,
                                        width=300,
                                        on_click=self.on_activate_mods,
                                    ),
                                    ft.ElevatedButton(
                                        "还原原版",
                                        icon=ft.icons.RESTORE,
                                        width=300,
                                        on_click=self.on_restore_original,
                                    ),
                                ],
                                spacing=10,
                            ),
                            width=350,
                        ),
                        ft.VerticalDivider(),
                        detail_panel,
                    ],
                    expand=True,
                    spacing=10,
                ),
            ],
            expand=True,
            spacing=10,
        )

    def _create_mod_list_items(self):
        """创建 MOD 列表项"""
        items = []
        for mod in self.mock_mods:
            items.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Checkbox(
                                value=mod["enabled"],
                                on_change=lambda e, m=mod: self.on_toggle_mod(e, m),
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        mod["name"],
                                        weight=ft.FontWeight.BOLD,
                                        size=14,
                                    ),
                                    ft.Text(
                                        mod["description"],
                                        size=11,
                                        color=ft.colors.GREY_600,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=10,
                    border_radius=5,
                    bgcolor=ft.colors.SURFACE_VARIANT
                    if mod == self.selected_mod
                    else None,
                    on_click=lambda e, m=mod: self.on_select_mod(e, m),
                )
            )
        return items

    def on_toggle_mod(self, e, mod):
        """切换 MOD 启用状态"""
        mod["enabled"] = e.control.value

    def on_select_mod(self, e, mod):
        """选择 MOD"""
        self.selected_mod = mod

    def on_create_mod(self, e):
        """创建新 MOD"""
        # TODO: 实现创建 MOD 功能
        pass

    def on_activate_mods(self, e):
        """激活选中的 MOD"""
        # TODO: 实现激活 MOD 功能
        pass

    def on_restore_original(self, e):
        """还原原版"""
        # TODO: 实现还原功能
        pass

    def on_edit_mod(self, e):
        """编辑 MOD"""
        # TODO: 实现编辑 MOD 功能
        pass

    def on_delete_mod(self, e):
        """删除 MOD"""
        # TODO: 实现删除 MOD 功能
        pass

    def on_export_mod(self, e):
        """导出 MOD"""
        # TODO: 实现导出 MOD 功能
        pass
