import flet as ft
import pandas as pd
from core.read_csv import read_csv


class DialoguePage:
    """对话文本编辑页面"""

    def __init__(self):
        # 读取CSV数据并转换为字典列表
        df = read_csv(with_classification=True)
        self.all_data = []  # 保存所有数据
        self.original_data = []  # 保存原始数据备份（用于还原）
        self.has_data = len(df) > 0  # 标记是否有数据

        for idx, row in df.iterrows():
            item = {
                "id": idx,
                "offset": row['Offset_start'] if not pd.isna(row['Offset_start']) else 0,  # 保存偏移量
                "zh_cn": row['ZH_CN'] if not pd.isna(row['ZH_CN']) else "",
                "category": row['Category'] if 'Category' in row else 'other',
                "category_name": row['Category_Name'] if 'Category_Name' in row else '其他'
            }
            self.all_data.append(item)
            # 深拷贝保存原始数据
            self.original_data.append(item.copy())

        self.data = self.all_data.copy()  # 当前显示的数据
        self.selected_category = "all"  # 当前选择的分类

        self.current_page = 0
        self.items_per_page = 50
        self.total_pages = self._calculate_total_pages()
        self.selected_row = None

        # UI组件引用
        self.data_table = None
        self.pagination_text = None
        self.prev_button = None
        self.next_button = None
        self.category_dropdown = None
        self.search_field = None
        self.stats_text = None
        self.page = None  # 保存page引用，用于显示对话框

        # 编辑对话框组件
        self.edit_dialog = None
        self.edit_text_field = None

    def _calculate_total_pages(self):
        """计算总页数"""
        return (len(self.data) + self.items_per_page - 1) // self.items_per_page if self.data else 1

    def build(self):
        """构建对话文本页面"""
        # 如果没有数据，显示提示信息
        if not self.has_data:
            return ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.icons.INFO_OUTLINE, size=64, color=ft.colors.BLUE_400),
                                ft.Text(
                                    "暂无数据",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    "请先在 MOD 管理页面提取游戏文本",
                                    size=16,
                                    color=ft.colors.GREY_700,
                                ),
                                ft.Text(
                                    "提取步骤：MOD 管理 → 提取 DAT 文件 → 提取文本",
                                    size=14,
                                    color=ft.colors.GREY_600,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20,
                        ),
                        padding=50,
                    ),
                ],
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.alignment.center,
            )

        # 创建编辑对话框
        self.edit_text_field = ft.TextField(
            label="编辑文本",
            multiline=True,
            min_lines=5,
            max_lines=15,
            width=600,
        )

        self.edit_dialog = ft.AlertDialog(
            title=ft.Text("编辑文本", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=self.edit_text_field,
                width=600,
                height=300,
            ),
            actions=[
                ft.TextButton("取消", on_click=self.close_edit_dialog),
                ft.ElevatedButton("保存", on_click=self.save_edit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        # 搜索框
        self.search_field = ft.TextField(
            hint_text="搜索文本内容...",
            prefix_icon=ft.icons.SEARCH,
            width=350,
            height=40,
            on_change=self.on_search,
            border_color=ft.colors.GREY_400,
            focused_border_color=ft.colors.BLUE_400,
        )

        # 分类筛选下拉框
        self.category_dropdown = ft.Dropdown(
            label="分类筛选",
            width=180,
            height=60,
            options=[
                ft.dropdown.Option("all", "全部"),
                ft.dropdown.Option("dialogue", "对话文本"),
                ft.dropdown.Option("item", "物品描述"),
                ft.dropdown.Option("skill", "技能描述"),
                ft.dropdown.Option("ui", "系统UI"),
                ft.dropdown.Option("attribute", "属性/状态"),
                ft.dropdown.Option("location", "地名/标题"),
                ft.dropdown.Option("other", "其他"),
            ],
            value="all",
            on_change=self.on_category_change,
            border_color=ft.colors.GREY_400,
            focused_border_color=ft.colors.BLUE_400,
        )

        # 统计信息文本
        self.stats_text = ft.Text(
            f"共 {len(self.data)} 条记录",
            size=14,
            color=ft.colors.GREY_700
        )

        # 工具栏
        toolbar = ft.Row(
            [
                self.search_field,
                self.category_dropdown,
                self.stats_text,
                ft.Container(width=20),  # 间隔
                ft.ElevatedButton(
                    "应用到游戏",
                    icon=ft.icons.PLAY_ARROW,
                    on_click=self.apply_to_game,
                    bgcolor=ft.colors.BLUE_400,
                    color=ft.colors.WHITE,
                ),
                ft.ElevatedButton(
                    "还原所有文本",
                    icon=ft.icons.RESTORE,
                    on_click=self.restore_all_texts,
                    bgcolor=ft.colors.ORANGE_400,
                    color=ft.colors.WHITE,
                ),
            ],
            spacing=15,
        )

        # 数据表格（添加分类列）
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD, size=14)),
                ft.DataColumn(ft.Text("分类", weight=ft.FontWeight.BOLD, size=14)),
                ft.DataColumn(ft.Text("简体中文", weight=ft.FontWeight.BOLD, size=14)),
                ft.DataColumn(ft.Text("操作", weight=ft.FontWeight.BOLD, size=14)),
            ],
            rows=self._create_table_rows(),
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_300),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_300),
            column_spacing=20,
        )

        # 分页控件（参考 Element UI 样式）
        self.prev_button = ft.IconButton(
            icon=ft.icons.CHEVRON_LEFT,
            on_click=self.on_prev_page,
            disabled=self.current_page == 0,
            tooltip="上一页",
        )

        self.pagination_text = ft.Text(
            f"{self.current_page + 1} / {self.total_pages}",
            size=14,
        )

        self.next_button = ft.IconButton(
            icon=ft.icons.CHEVRON_RIGHT,
            on_click=self.on_next_page,
            disabled=self.current_page >= self.total_pages - 1,
            tooltip="下一页",
        )

        pagination = ft.Row(
            [
                self.prev_button,
                self.pagination_text,
                self.next_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        )

        # 主布局
        return ft.Column(
            [
                toolbar,
                ft.Divider(height=1),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                content=self.data_table,
                                border=ft.border.all(1, ft.colors.GREY_400),
                                border_radius=10,
                                padding=10,
                            ),
                            pagination,
                        ],
                        spacing=15,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    expand=True,
                    padding=10,
                ),
            ],
            expand=True,
            spacing=10,
        )

    def _create_table_rows(self):
        """创建表格行（添加分类列和颜色）"""
        rows = []
        # 计算当前页的数据范围
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.data))

        # 分类颜色映射
        category_colors = {
            'dialogue': ft.colors.BLUE_100,
            'item': ft.colors.GREEN_100,
            'skill': ft.colors.PURPLE_100,
            'ui': ft.colors.ORANGE_100,
            'attribute': ft.colors.PINK_100,
            'location': ft.colors.CYAN_100,
            'other': ft.colors.GREY_100,
        }

        for item in self.data[start_idx:end_idx]:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(item["id"]), size=12)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    item["category_name"],
                                    size=11,
                                    weight=ft.FontWeight.W_500,
                                    no_wrap=False,
                                ),
                                bgcolor=category_colors.get(item["category"], ft.colors.GREY_100),
                                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                border_radius=5,
                                width=100,  # 固定宽度确保文字完整显示
                                alignment=ft.alignment.center,
                            )
                        ),
                        ft.DataCell(ft.Text(item["zh_cn"], size=12)),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                tooltip="编辑",
                                icon_size=20,
                                on_click=lambda e, row=item: self.on_edit_row(e, row),
                            )
                        ),
                    ],
                )
            )
        return rows

    def on_category_change(self, e):
        """分类筛选事件"""
        self.selected_category = e.control.value
        self._apply_filters()

    def on_search(self, e):
        """搜索对话"""
        self._apply_filters()

    def _apply_filters(self):
        """应用筛选条件（分类+搜索）"""
        # 从所有数据开始筛选
        filtered = self.all_data.copy()

        # 应用分类筛选
        if self.selected_category != "all":
            filtered = [item for item in filtered if item["category"] == self.selected_category]

        # 应用搜索筛选
        if self.search_field and self.search_field.value:
            search_text = self.search_field.value.lower()
            filtered = [item for item in filtered if search_text in item["zh_cn"].lower()]

        self.data = filtered
        self.total_pages = self._calculate_total_pages()
        self.current_page = 0

        # 更新统计信息
        if self.stats_text:
            self.stats_text.value = f"共 {len(self.data)} 条记录"

        self._update_table()

    def on_prev_page(self, e):
        """上一页"""
        if self.current_page > 0:
            self.current_page -= 1
            self._update_table()

    def on_next_page(self, e):
        """下一页"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._update_table()

    def _update_table(self):
        """更新表格和分页控件"""
        # 更新表格行
        self.data_table.rows = self._create_table_rows()

        # 更新分页文本
        self.pagination_text.value = f"{self.current_page + 1} / {self.total_pages}"

        # 更新按钮状态
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= self.total_pages - 1

        # 刷新UI
        if self.data_table.page:
            self.data_table.update()
            self.pagination_text.update()
            self.prev_button.update()
            self.next_button.update()
            if self.stats_text:
                self.stats_text.update()

    def on_edit_row(self, e, row):
        """编辑行"""
        self.selected_row = row
        # 设置编辑框的内容
        self.edit_text_field.value = row["zh_cn"]
        # 显示对话框
        if self.page:
            self.page.dialog = self.edit_dialog
            self.edit_dialog.open = True
            self.page.update()

    def close_edit_dialog(self, e):
        """关闭编辑对话框"""
        if self.page:
            self.edit_dialog.open = False
            self.page.update()

    def save_edit(self, e):
        """保存编辑"""
        if self.selected_row and self.edit_text_field.value:
            # 更新数据
            new_text = self.edit_text_field.value
            row_id = self.selected_row["id"]

            # 在all_data中更新
            for item in self.all_data:
                if item["id"] == row_id:
                    item["zh_cn"] = new_text
                    break
            # 在data中更新
            for item in self.data:
                if item["id"] == row_id:
                    item["zh_cn"] = new_text
                    break

            # 立即保存到CSV文件
            try:
                from config import Config
                game_path = Config.get_game_path()
                if game_path:
                    csv_path = Config.get_extracted_texts_csv(game_path)
                    # 读取完整CSV（读取所有列）
                    df = pd.read_csv(csv_path, encoding='utf-8',         
                    names=["id_текста", "Offset_start", "JPN", "US", "ZH_CN", "ZH_TW", "KO", "ES", ""],)
                    # 获取当前行的Offset_start
                    offset = self.selected_row.get("offset", 0)
                    print(f"保存: offset={offset}, new_text={new_text}")
                    # 转换为数值类型后比较
                    df['Offset_start'] = pd.to_numeric(df['Offset_start'], errors='coerce').fillna(0).astype(int)
                    offset = int(offset)

                    print(f"匹配的行数: {len(df[df['Offset_start'] == offset])}")

                    # 使用Offset_start定位行并修改ZH_CN列
                    df.loc[df['Offset_start'] == offset, 'ZH_CN'] = new_text

                    # 保存回CSV（保留所有列，确保格式正确）
                    df.to_csv(csv_path, index=False, encoding='utf-8', quoting=1, header=False)
                    print("CSV保存成功")
            except Exception as ex:
                print(f"保存CSV失败: {ex}")
                import traceback
                traceback.print_exc()

            # 关闭对话框
            self.close_edit_dialog(e)

            # 刷新表格
            self._update_table()

            # 显示成功提示
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("保存成功！"),
                    bgcolor=ft.colors.GREEN_400,
                )
                self.page.snack_bar.open = True
                self.page.update()

    def restore_all_texts(self, e):
        """还原所有文本到原始状态"""
        if self.page:
            # 显示确认对话框
            def confirm_restore(e):
                confirm_dialog.open = False
                self.page.update()

                try:
                    from backend.services.text_importer import TextImporter
                    from config import Config

                    # 获取游戏路径
                    game_path = Config.get_game_path()
                    if not game_path:
                        raise Exception("未找到游戏目录")

                    importer = TextImporter(game_path)

                    # 调用还原方法，重新生成CSV
                    success, message = importer.restore_original()
                    if not success:
                        raise Exception(message)

                    # 重新加载数据
                    from core.read_csv import read_csv
                    df = read_csv(with_classification=True)
                    self.all_data = []
                    for _, row in df.iterrows():
                        self.all_data.append({
                            "id": len(self.all_data) + 1,
                            "offset": int(row['Offset_start']),
                            "zh_cn": str(row['ZH_CN']),
                            "category": row['Category'],
                            "category_name": row['Category_Name']
                        })
                    self.original_data = [item.copy() for item in self.all_data]
                    self.data = self.all_data.copy()

                    # 重新应用当前的筛选条件
                    self._apply_filters()

                    # 显示成功提示
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("已还原所有文本到原始状态！"),
                        bgcolor=ft.colors.GREEN_400,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()

                except Exception as ex:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"还原失败: {str(ex)}"),
                        bgcolor=ft.colors.RED_400,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()

            def cancel_restore(e):
                confirm_dialog.open = False
                self.page.update()

            confirm_dialog = ft.AlertDialog(
                title=ft.Text("确认还原", size=18, weight=ft.FontWeight.BOLD),
                content=ft.Text(
                    "确定要还原所有文本到原始状态吗？\n\n所有修改将会丢失，此操作不可撤销！",
                    size=14,
                ),
                actions=[
                    ft.TextButton("取消", on_click=cancel_restore),
                    ft.ElevatedButton(
                        "确认还原",
                        on_click=confirm_restore,
                        bgcolor=ft.colors.ORANGE_400,
                        color=ft.colors.WHITE,
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            self.page.dialog = confirm_dialog
            confirm_dialog.open = True
            self.page.update()

    def apply_to_game(self, e):
        """应用修改到游戏"""
        if not self.page:
            return

        # 显示确认对话框
        def confirm_apply(e):
            confirm_dialog.open = False
            self.page.update()

            try:
                from backend.services.text_importer import TextImporter
                from config import Config

                # 获取游戏路径
                game_path = Config.get_game_path()
                if not game_path:
                    raise Exception("未找到游戏目录")

                importer = TextImporter(game_path)

                # 应用修改（只打包DAT，不保存CSV）
                success, message = importer.apply_changes()
                if not success:
                    raise Exception(message)

                # 完成
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("修改已成功应用到游戏！"),
                    bgcolor=ft.colors.GREEN_400,
                )
                self.page.snack_bar.open = True
                self.page.update()

            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"应用失败: {str(ex)}"),
                    bgcolor=ft.colors.RED_400,
                )
                self.page.snack_bar.open = True
                self.page.update()

        def cancel_apply(e):
            confirm_dialog.open = False
            self.page.update()

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("确认应用", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Text(
                "确定要将修改应用到游戏吗？\n\n这将修改游戏的文本文件。",
                size=14,
            ),
            actions=[
                ft.TextButton("取消", on_click=cancel_apply),
                ft.ElevatedButton(
                    "确认应用",
                    on_click=confirm_apply,
                    bgcolor=ft.colors.BLUE_400,
                    color=ft.colors.WHITE,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = confirm_dialog
        confirm_dialog.open = True
        self.page.update()
