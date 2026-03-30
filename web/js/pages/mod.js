const modPage = {
    name: 'ModPage',
    props: ['showToast'],
    data() {
        return {
            mods: [],
            selectedMod: null,
            confirm: { visible: false, title: '', message: '', okText: '', okColor: '', onOk: null },
        };
    },
    mounted() { this.fetchMods(); },
    methods: {
        async fetchMods() {
            const mods = await pywebview.api.get_mods();
            this.mods = mods;
            if (this.selectedMod) {
                this.selectedMod = mods.find(m => m.folder_name === this.selectedMod.folder_name) || null;
            }
            if (!this.selectedMod && mods.length > 0) this.selectedMod = mods[0];
        },
        selectMod(mod) { this.selectedMod = mod; },
        async activateMod() {
            if (!this.selectedMod) { this.showToast('请先选择一个 MOD', 'orange'); return; }
            const r = await pywebview.api.activate_mod(this.selectedMod.folder_name);
            this.showToast(r.msg, r.ok ? 'green' : 'red');
            if (r.ok) await this.fetchMods();
        },
        restoreAll() {
            this.showConfirm(
                '确认还原',
                '确定要还原所有原版文件吗？\n\n这将删除以下文件夹：\n• DAT\n• Image\n• Image2K\n• Sound\n• Image4K\n• Image720p\n\n然后重新解压 DAT_BACK.dxa 备份文件。',
                '确认还原',
                '#e65100',
                async () => {
                    const r = await pywebview.api.restore_all_mods();
                    this.showToast(r.msg, r.ok ? 'green' : 'red');
                    if (r.ok) await this.fetchMods();
                }
            );
        },
        deleteMod() {
            if (!this.selectedMod) return;
            const warningMsg = this.selectedMod.is_active
                ? `确定要删除 MOD "${this.selectedMod.name}" 吗？\n\n⚠️ 警告：此 MOD 已激活，删除后将无法恢复。\n建议先使用"还原原版"功能。`
                : `确定要删除 MOD "${this.selectedMod.name}" 吗？`;

            this.showConfirm(
                '确认删除',
                warningMsg,
                '确认删除',
                '#c62828',
                async () => {
                    const r = await pywebview.api.delete_mod(this.selectedMod.folder_name);
                    this.showToast(r.msg, r.ok ? 'green' : 'red');
                    if (r.ok) {
                        this.selectedMod = null;
                        await this.fetchMods();
                    }
                }
            );
        },
        showConfirm(title, message, okText, okColor, onOk) {
            this.confirm = { visible: true, title, message, okText, okColor, onOk };
        },
        doConfirm() { const fn = this.confirm.onOk; this.confirm.visible = false; if (fn) fn(); },
    },
    template: `
<div class="page mod-page">
    <div class="page-header"><h2>MOD 管理</h2></div>
    <div class="mod-layout">
        <div class="mod-list-panel">
            <div class="panel-header">
                <span>MOD 列表</span>
                <button class="btn-icon" @click="fetchMods" title="刷新">↻</button>
            </div>
            <div class="mod-list">
                <div v-if="mods.length === 0" class="empty-state">没有找到 MOD</div>
                <div v-for="mod in mods" :key="mod.folder_name"
                     class="mod-item" :class="{selected: selectedMod && selectedMod.folder_name === mod.folder_name}"
                     @click="selectMod(mod)">
                    <span class="mod-status-icon">{{ mod.is_active ? '✅' : '⭕' }}</span>
                    <div class="mod-item-info">
                        <div class="mod-item-name">{{ mod.name }}</div>
                        <div class="mod-item-desc" v-if="mod.description">
                            {{ mod.description.length > 40 ? mod.description.slice(0,40) + '…' : mod.description }}
                        </div>
                    </div>
                </div>
            </div>
            <div class="mod-actions">
                <button class="btn btn-primary btn-block" @click="activateMod">▶ 激活选中的 MOD</button>
                <button class="btn btn-secondary btn-block" @click="restoreAll">↺ 还原原版</button>
            </div>
        </div>
        <div class="mod-detail-panel">
            <div v-if="!selectedMod" class="empty-state-center"><p>请选择一个 MOD</p></div>
            <div v-else class="mod-detail">
                <h3>MOD 详情</h3>
                <hr>
                <div class="mod-name-row">
                    <span class="mod-detail-name">{{ selectedMod.name }}</span>
                    <span class="badge" :class="selectedMod.is_active ? 'badge-active' : 'badge-inactive'">
                        {{ selectedMod.is_active ? '已激活' : '未激活' }}
                    </span>
                </div>
                <p class="mod-desc">{{ selectedMod.description }}</p>
                <p class="mod-meta">作者: {{ selectedMod.author || '未知' }} &nbsp;&nbsp; 版本: {{ selectedMod.version || '1.0' }}</p>
                <hr>
                <strong style="font-size:13px">包含文件:</strong>
                <ul class="file-list">
                    <li v-for="f in (selectedMod.files || [])" :key="f">{{ f }}</li>
                    <li v-if="!(selectedMod.files && selectedMod.files.length)" style="color:#8b949e">（无文件）</li>
                </ul>
                <button class="btn btn-danger" @click="deleteMod" style="margin-top:16px">🗑 删除此 MOD</button>
            </div>
        </div>
    </div>
    <div v-if="confirm.visible" class="modal-overlay">
        <div class="modal modal-sm">
            <div class="modal-header"><h3>{{ confirm.title }}</h3></div>
            <div class="modal-body"><p style="white-space: pre-line;">{{ confirm.message }}</p></div>
            <div class="modal-footer">
                <button class="btn" :style="{backgroundColor: confirm.okColor}" @click="doConfirm">{{ confirm.okText }}</button>
                <button class="btn btn-secondary" @click="confirm.visible=false">取消</button>
            </div>
        </div>
    </div>
</div>
    `,
};
