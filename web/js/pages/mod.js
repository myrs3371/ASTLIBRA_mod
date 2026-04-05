/* ── SVG icons (Lucide-style) ── */
const MOD_ICONS = {
    refresh: `<svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-.48-3.17"/></svg>`,
    play:    `<svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>`,
    undo:    `<svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.17"/></svg>`,
    trash:   `<svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>`,
    box:     `<svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>`,
    check:   `<svg viewBox="0 0 24 24" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
    xmark:   `<svg viewBox="0 0 24 24" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`,
};

const modPage = {
    name: 'ModPage',
    props: ['showToast'],
    data() {
        return {
            mods: [],
            selectedMod: null,
            checkedMods: [],
            confirm: { visible: false, title: '', message: '', okText: '', okColor: '', onOk: null },
            modProgress: { visible: false, step: '', success: false, error: null },
            _pollTimer: null,
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
        toggleCheck(mod) {
            const idx = this.checkedMods.indexOf(mod.folder_name);
            if (idx > -1) this.checkedMods.splice(idx, 1);
            else this.checkedMods.push(mod.folder_name);
        },
        isChecked(mod) { return this.checkedMods.includes(mod.folder_name); },
        async activateMod() {
            if (this.checkedMods.length === 0) {
                this.showToast('请先勾选要激活的 MOD', 'orange');
                return;
            }
            this.modProgress = { visible: true, step: '正在准备...', success: false, error: null };
            const r = await pywebview.api.activate_mods(this.checkedMods);
            if (!r.ok && r.msg !== 'started') {
                this.modProgress.step = r.msg;
                this.modProgress.error = r.msg;
                return;
            }
            this._pollTimer = setInterval(async () => {
                const s = await pywebview.api.get_mod_status();
                this.modProgress.step = s.step;
                if (s.done) {
                    clearInterval(this._pollTimer);
                    this._pollTimer = null;
                    this.modProgress.success = s.success;
                    this.modProgress.error = s.error;
                    if (s.success) {
                        this.checkedMods = [];
                        await this.fetchMods();
                    }
                }
            }, 400);
        },
        closeModProgress() {
            if (this._pollTimer) { clearInterval(this._pollTimer); this._pollTimer = null; }
            const ok  = this.modProgress.success;
            const err = this.modProgress.error;
            this.modProgress = { visible: false, step: '', success: false, error: null };
            if (ok)  this.showToast('MOD 激活成功！', 'green');
            else if (err) this.showToast(err, 'red');
        },
        restoreAll() {
            this.showConfirm(
                '确认还原原版',
                '确定要还原所有原版文件吗？\n\n这将删除以下文件夹：\n• DAT\n• Image / Image2K / Image4K / Image720p\n• Sound\n\n然后重新解压 DAT_BACK.dxa 备份文件。',
                '确认还原', '#f59e0b',
                async () => {
                    const r = await pywebview.api.restore_all_mods();
                    this.showToast(r.msg, r.ok ? 'green' : 'red');
                    if (r.ok) await this.fetchMods();
                }
            );
        },
        deleteMod() {
            if (!this.selectedMod) return;
            this.showConfirm(
                '确认删除',
                `确定要删除 MOD「${this.selectedMod.name}」吗？\n\n此操作不可撤销。`,
                '确认删除', '#ef4444',
                async () => {
                    const r = await pywebview.api.delete_mod(this.selectedMod.folder_name);
                    this.showToast(r.msg, r.ok ? 'green' : 'red');
                    if (r.ok) { this.selectedMod = null; await this.fetchMods(); }
                }
            );
        },
        showConfirm(title, message, okText, okColor, onOk) {
            this.confirm = { visible: true, title, message, okText, okColor, onOk };
        },
        doConfirm() { const fn = this.confirm.onOk; this.confirm.visible = false; if (fn) fn(); },
        icn(name) { return MOD_ICONS[name] || ''; },
    },
    template: `
<div class="page mod-page">
    <div class="page-header">
        <h2>MOD 管理</h2>
    </div>

    <div class="mod-layout">
        <!-- 左侧 MOD 列表 -->
        <div class="mod-list-panel">
            <div class="panel-header">
                <span>MOD 列表</span>
                <button class="btn-icon" @click="fetchMods" title="刷新列表">
                    <span v-html="icn('refresh')"></span>
                </button>
            </div>

            <div class="mod-list">
                <div v-if="mods.length === 0" class="empty-state">
                    没有找到 MOD<br>
                    <span style="font-size:11px;color:var(--text-muted);margin-top:4px;display:block">
                        请将 MOD 文件夹放入 MODS 目录
                    </span>
                </div>
                <div v-for="mod in mods" :key="mod.folder_name"
                     class="mod-item"
                     :class="{ selected: selectedMod && selectedMod.folder_name === mod.folder_name }">
                    <input type="checkbox"
                           :checked="isChecked(mod)"
                           @change="toggleCheck(mod)"
                           @click.stop>
                    <div class="mod-item-info" @click="selectMod(mod)">
                        <div class="mod-item-name">{{ mod.name }}</div>
                        <div class="mod-item-desc" v-if="mod.description">
                            {{ mod.description.length > 38 ? mod.description.slice(0, 38) + '…' : mod.description }}
                        </div>
                    </div>
                    <span class="mod-item-badge" :class="mod.is_active ? 'active' : 'inactive'">
                        {{ mod.is_active ? '已激活' : '未激活' }}
                    </span>
                </div>
            </div>

            <div class="mod-actions">
                <button class="btn btn-primary btn-block" @click="activateMod"
                        :disabled="checkedMods.length === 0">
                    <span v-html="icn('play')"></span>
                    激活勾选的 MOD
                    <span v-if="checkedMods.length > 0"
                          style="margin-left:2px;opacity:0.75;font-size:12px">({{ checkedMods.length }})</span>
                </button>
                <button class="btn btn-secondary btn-block" @click="restoreAll">
                    <span v-html="icn('undo')"></span>
                    还原原版文件
                </button>
            </div>
        </div>

        <!-- 右侧详情面板 -->
        <div class="mod-detail-panel">
            <div v-if="!selectedMod" class="mod-detail-empty">
                <span class="mod-detail-empty-icon" v-html="icn('box')"></span>
                <span>从左侧选择一个 MOD 查看详情</span>
            </div>

            <div v-else>
                <div class="mod-detail-section-title">MOD 详情</div>

                <div class="mod-name-row">
                    <span class="mod-detail-name">{{ selectedMod.name }}</span>
                    <span class="badge" :class="selectedMod.is_active ? 'badge-active' : 'badge-inactive'">
                        {{ selectedMod.is_active ? '已激活' : '未激活' }}
                    </span>
                </div>

                <p class="mod-desc">{{ selectedMod.description || '该 MOD 暂无描述信息。' }}</p>

                <div class="mod-meta-row">
                    <div class="mod-meta-item">
                        <span class="mod-meta-label">作者</span>
                        <span class="mod-meta-value">{{ selectedMod.author || '未知' }}</span>
                    </div>
                    <div class="mod-meta-item">
                        <span class="mod-meta-label">版本</span>
                        <span class="mod-meta-value">{{ selectedMod.version || '—' }}</span>
                    </div>
                    <div class="mod-meta-item">
                        <span class="mod-meta-label">文件夹</span>
                        <span class="mod-meta-value" style="font-family:monospace;font-size:12px">{{ selectedMod.folder_name }}</span>
                    </div>
                </div>

                <hr class="mod-detail-divider">

                <button class="btn btn-danger" @click="deleteMod">
                    <span v-html="icn('trash')"></span>
                    删除此 MOD
                </button>
            </div>
        </div>
    </div>

    <!-- MOD 激活进度弹窗 -->
    <div v-if="modProgress.visible" class="modal-overlay">
        <div class="modal modal-sm">
            <div class="modal-header"><h3>激活 MOD</h3></div>
            <div class="modal-body" style="text-align:center;padding:28px 20px">
                <!-- 进行中 -->
                <div v-if="!modProgress.success && !modProgress.error"
                     class="spinner" style="margin:0 auto 14px"></div>
                <!-- 成功 -->
                <div v-if="modProgress.success"
                     class="status-icon status-icon-success"
                     v-html="icn('check')"></div>
                <!-- 失败 -->
                <div v-if="modProgress.error"
                     class="status-icon status-icon-error"
                     v-html="icn('xmark')"></div>

                <p style="font-size:14px;color:var(--text-secondary);margin:0">{{ modProgress.step }}</p>
                <p v-if="modProgress.error"
                   style="font-size:12px;color:var(--danger);margin-top:8px;line-height:1.5">{{ modProgress.error }}</p>
            </div>
            <div class="modal-footer" v-if="modProgress.success || modProgress.error">
                <button class="btn btn-primary" @click="closeModProgress">确定</button>
            </div>
        </div>
    </div>

    <!-- 确认对话框 -->
    <div v-if="confirm.visible" class="modal-overlay" @click.self="confirm.visible = false">
        <div class="modal modal-sm">
            <div class="modal-header"><h3>{{ confirm.title }}</h3></div>
            <div class="modal-body"><p style="white-space:pre-line">{{ confirm.message }}</p></div>
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
