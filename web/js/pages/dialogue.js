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
                this.showToast('保存成功！', 'green');
            } else {
                this.showToast('保存失败: ' + (r.error || ''), 'red');
            }
        },
        applyToGame() {
            this.showConfirm('确认应用', '确定要将修改应用到游戏吗？\n这将修改游戏的文本文件。',
                '确认应用', '#1f6aa5', async () => {
                    const r = await pywebview.api.apply_changes();
                    this.showToast(r.msg, r.ok ? 'green' : 'red');
                });
        },
        restoreAll() {
            this.showConfirm('确认还原', '确定要还原所有文本到原始状态吗？\n所有修改将会丢失，此操作不可撤销！',
                '确认还原', '#e65100', async () => {
                    const r = await pywebview.api.restore_original();
                    this.showToast(r.msg, r.ok ? 'green' : 'red');
                    if (r.ok) { this.currentPage = 0; this.fetchTexts(); }
                });
        },
        showConfirm(title, message, okText, okColor, onOk) {
            this.confirm = { visible: true, title, message, okText, okColor, onOk };
        },
        doConfirm() { const fn = this.confirm.onOk; this.confirm.visible = false; if (fn) fn(); },
        catColor(cat) {
            return { dialogue:'#1565c0', item:'#2e7d32', skill:'#6a1b9a',
                     ui:'#e65100', attribute:'#880e4f', location:'#006064', other:'#424242' }[cat] || '#424242';
        },
    },
    template: `
<div class="page dialogue-page">
    <div v-if="noData && !loading" class="empty-state-center">
        <h2>⚠ 暂无数据</h2>
        <p style="margin-bottom:16px">游戏文本尚未提取，点击下方按钮开始</p>
        <button class="btn btn-primary" @click="triggerExtraction">▶ 开始提取文本</button>
    </div>
    <template v-else>
        <div class="toolbar">
            <input class="search-input" type="text" placeholder="搜索文本内容..."
                   v-model="search" @input="onSearchInput">
            <select class="category-select" v-model="category" @change="onCategoryChange">
                <option value="all">全部</option>
                <option value="dialogue">对话文本</option>
                <option value="item">物品描述</option>
                <option value="skill">技能描述</option>
                <option value="ui">系统UI</option>
                <option value="attribute">属性/状态</option>
                <option value="location">地名/标题</option>
                <option value="other">其他</option>
            </select>
            <span class="stats-label">共 {{ total }} 条记录</span>
            <div class="toolbar-right">
                <button class="btn btn-warning" @click="restoreAll">↺ 还原所有文本</button>
                <button class="btn btn-primary" @click="applyToGame">▶ 应用到游戏</button>
            </div>
        </div>
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th style="width:80px">ID</th>
                        <th style="width:110px">分类</th>
                        <th>简体中文（双击编辑）</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(item, i) in items" :key="item.offset"
                        :class="i % 2 === 0 ? 'even' : 'odd'"
                        @dblclick="openEditDialog(item)">
                        <td class="center">{{ item.id }}</td>
                        <td class="center">
                            <span class="cat-badge" :style="{backgroundColor: catColor(item.category)}">
                                {{ item.category_name }}
                            </span>
                        </td>
                        <td class="text-cell">{{ item.zh_cn }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div class="pagination">
            <button class="btn-icon" :disabled="currentPage === 0" @click="prevPage">◀</button>
            <span class="page-info">{{ currentPage + 1 }} / {{ pages }}</span>
            <button class="btn-icon" :disabled="currentPage >= pages - 1" @click="nextPage">▶</button>
        </div>
    </template>
    <div v-if="editRow" class="modal-overlay" @click.self="closeEditDialog">
        <div class="modal">
            <div class="modal-header">
                <h3>编辑文本</h3>
                <span class="modal-meta">ID: {{ editRow.id }} | 分类: {{ editRow.category_name }}</span>
            </div>
            <div class="modal-body">
                <textarea class="edit-textarea" v-model="editText" ref="editTextarea"
                          @keydown.ctrl.s.prevent="saveEdit"></textarea>
            </div>
            <div class="modal-footer">
                <button class="btn btn-primary" @click="saveEdit">保存 (Ctrl+S)</button>
                <button class="btn btn-secondary" @click="closeEditDialog">取消 (Esc)</button>
            </div>
        </div>
    </div>
    <div v-if="confirm.visible" class="modal-overlay">
        <div class="modal modal-sm">
            <div class="modal-header"><h3>{{ confirm.title }}</h3></div>
            <div class="modal-body"><p>{{ confirm.message }}</p></div>
            <div class="modal-footer">
                <button class="btn" :style="{backgroundColor: confirm.okColor}" @click="doConfirm">{{ confirm.okText }}</button>
                <button class="btn btn-secondary" @click="confirm.visible=false">取消</button>
            </div>
        </div>
    </div>
</div>
    `,
};
