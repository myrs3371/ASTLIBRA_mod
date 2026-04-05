/* ── SVG icons (Lucide-style) ── */
const DLG_ICONS = {
    play:  `<svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>`,
    undo:  `<svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.17"/></svg>`,
    save:  `<svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>`,
};

const dialoguePage = {
    name: 'DialoguePage',
    props: ['showToast', 'startExtraction'],
    data() {
        return {
            items: [],
            total: 0,
            pages: 1,
            currentPage: 0,
            pageSize: 50,
            search: '',
            category: 'all',
            searchTimer: null,
            loading: false,
            noData: false,
            editRow: null,
            editText: '',
            confirm: { visible: false, title: '', message: '', okText: '', okColor: '', onOk: null },
        };
    },
    mounted() {
        document.addEventListener('keydown', this.onKeyDown);
        this.fetchTexts();
    },
    beforeUnmount() {
        document.removeEventListener('keydown', this.onKeyDown);
    },
    methods: {
        onKeyDown(e) {
            if (e.key === 'Escape' && this.editRow && !this.confirm.visible) {
                this.closeEditDialog();
            }
        },
        triggerExtraction() {
            if (this.startExtraction) {
                this.startExtraction(() => { this.fetchTexts(); });
            }
        },
        async fetchTexts() {
            this.loading = true;
            try {
                const r = await pywebview.api.get_texts(
                    this.currentPage, this.pageSize, this.search, this.category
                );
                this.items = r.items || [];
                this.total = r.total || 0;
                this.pages = r.pages || 1;
                this.noData = (this.total === 0 && !this.search && this.category === 'all');
            } catch (e) {
                console.error(e);
                this.noData = true;
            } finally {
                this.loading = false;
            }
        },
        onSearchInput() {
            clearTimeout(this.searchTimer);
            this.searchTimer = setTimeout(() => { this.currentPage = 0; this.fetchTexts(); }, 300);
        },
        onCategoryChange() { this.currentPage = 0; this.fetchTexts(); },
        prevPage() { if (this.currentPage > 0) { this.currentPage--; this.fetchTexts(); } },
        nextPage() { if (this.currentPage < this.pages - 1) { this.currentPage++; this.fetchTexts(); } },
        openEditDialog(item) {
            this.editRow = { ...item };
            this.editText = item.zh_cn;
            this.$nextTick(() => { const ta = this.$refs.editTextarea; if (ta) { ta.focus(); ta.select(); } });
        },
        closeEditDialog() { this.editRow = null; this.editText = ''; },
        async saveEdit() {
            if (!this.editRow) return;
            const r = await pywebview.api.update_text(this.editRow.offset, this.editText);
            if (r.ok) {
                const item = this.items.find(it => it.offset === this.editRow.offset);
                if (item) item.zh_cn = this.editText;
                this.closeEditDialog();
                this.showToast('保存成功', 'green');
            } else {
                this.showToast('保存失败: ' + (r.error || ''), 'red');
            }
        },
        applyToGame() {
            this.showConfirm(
                '确认应用',
                '确定要将所有修改应用到游戏吗？\n这将覆盖游戏的文本文件。',
                '确认应用', '#0ea5e9',
                async () => {
                    const r = await pywebview.api.apply_changes();
                    this.showToast(r.msg, r.ok ? 'green' : 'red');
                }
            );
        },
        restoreAll() {
            this.showConfirm(
                '确认还原',
                '确定要将所有文本还原到原始状态吗？\n\n所有已编辑的修改将会丢失，此操作不可撤销。',
                '确认还原', '#f59e0b',
                async () => {
                    const r = await pywebview.api.restore_original();
                    this.showToast(r.msg, r.ok ? 'green' : 'red');
                    if (r.ok) { this.currentPage = 0; this.fetchTexts(); }
                }
            );
        },
        showConfirm(title, message, okText, okColor, onOk) {
            this.confirm = { visible: true, title, message, okText, okColor, onOk };
        },
        doConfirm() { const fn = this.confirm.onOk; this.confirm.visible = false; if (fn) fn(); },
        catColor(cat) {
            return {
                dialogue:  '#1565c0',
                item:      '#2e7d32',
                skill:     '#6a1b9a',
                ui:        '#e65100',
                attribute: '#880e4f',
                location:  '#006064',
                other:     '#37474f',
            }[cat] || '#37474f';
        },
        icn(name) { return DLG_ICONS[name] || ''; },
    },
    template: `
<div class="page dialogue-page">

    <!-- 无数据：引导提取 -->
    <div v-if="noData && !loading" class="empty-state-center">
        <h2>暂无文本数据</h2>
        <p style="color:var(--text-secondary);font-size:13px;margin-bottom:18px">游戏文本尚未提取，点击下方按钮开始</p>
        <button class="btn btn-primary" @click="triggerExtraction">
            <span v-html="icn('play')"></span>
            开始提取文本
        </button>
    </div>

    <template v-else>
        <!-- 工具栏 -->
        <div class="toolbar">
            <input class="search-input" type="text" placeholder="搜索文本内容..."
                   v-model="search" @input="onSearchInput">
            <select class="category-select" v-model="category" @change="onCategoryChange">
                <option value="all">全部分类</option>
                <option value="dialogue">对话文本</option>
                <option value="item">物品描述</option>
                <option value="skill">技能描述</option>
                <option value="ui">系统 UI</option>
                <option value="attribute">属性/状态</option>
                <option value="location">地名/标题</option>
                <option value="other">其他</option>
            </select>
            <span class="stats-label">共 {{ total }} 条记录</span>
            <div class="toolbar-right">
                <button class="btn btn-warning" @click="restoreAll">
                    <span v-html="icn('undo')"></span>
                    还原所有文本
                </button>
                <button class="btn btn-primary" @click="applyToGame">
                    <span v-html="icn('play')"></span>
                    应用到游戏
                </button>
            </div>
        </div>

        <!-- 数据表格 -->
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th style="width:76px">ID</th>
                        <th style="width:108px">分类</th>
                        <th>简体中文（双击行编辑）</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-if="loading">
                        <td colspan="3" style="text-align:center;padding:24px;color:var(--text-secondary)">
                            <span class="spinner-sm" style="margin-right:8px"></span>加载中...
                        </td>
                    </tr>
                    <tr v-for="item in items" :key="item.offset"
                        @dblclick="openEditDialog(item)">
                        <td class="center" style="color:var(--text-secondary);font-size:12px">{{ item.id }}</td>
                        <td class="center">
                            <span class="cat-badge" :style="{ backgroundColor: catColor(item.category) }">
                                {{ item.category_name }}
                            </span>
                        </td>
                        <td class="text-cell">{{ item.zh_cn }}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 分页 -->
        <div class="pagination">
            <button class="btn-icon" :disabled="currentPage === 0" @click="prevPage">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <span class="page-info">第 {{ currentPage + 1 }} 页，共 {{ pages }} 页</span>
            <button class="btn-icon" :disabled="currentPage >= pages - 1" @click="nextPage">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
        </div>
    </template>

    <!-- 编辑弹窗 -->
    <div v-if="editRow" class="modal-overlay" @click.self="closeEditDialog">
        <div class="modal">
            <div class="modal-header">
                <h3>编辑文本</h3>
                <span class="modal-meta">ID: {{ editRow.id }} &nbsp;·&nbsp; 分类: {{ editRow.category_name }}</span>
            </div>
            <div class="modal-body">
                <textarea class="edit-textarea" v-model="editText" ref="editTextarea"
                          @keydown.ctrl.s.prevent="saveEdit"></textarea>
            </div>
            <div class="modal-footer">
                <button class="btn btn-primary" @click="saveEdit">
                    <span v-html="icn('save')"></span>
                    保存 (Ctrl+S)
                </button>
                <button class="btn btn-secondary" @click="closeEditDialog">取消 (Esc)</button>
            </div>
        </div>
    </div>

    <!-- 确认对话框 -->
    <div v-if="confirm.visible" class="modal-overlay" @click.self="confirm.visible = false">
        <div class="modal modal-sm">
            <div class="modal-header"><h3>{{ confirm.title }}</h3></div>
            <div class="modal-body"><p>{{ confirm.message }}</p></div>
            <div class="modal-footer">
                <button class="btn"
                        :style="{ background: confirm.okColor, borderColor: confirm.okColor, color: '#fff' }"
                        @click="doConfirm">{{ confirm.okText }}</button>
                <button class="btn btn-secondary" @click="confirm.visible = false">取消</button>
            </div>
        </div>
    </div>

</div>
    `,
};
