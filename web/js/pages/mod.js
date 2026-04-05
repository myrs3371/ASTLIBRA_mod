const modPage = {
    name: 'ModPage',
    props: ['showToast'],
    data() {
        return {
            mods: [], //mod列表
            selectedMod: null, //当前选中展示的mod
            checkedMods: [],
            confirm: { visible: false, title: '', message: '', okText: '', okColor: '', onOk: null },
        };
    },
    mounted() { this.fetchMods(); },
    methods: {
        /**从python拿到mod列表
         * 如果没有选择的mod，则默认选择第一个
         */
        async fetchMods() {
            const mods = await pywebview.api.get_mods();
            this.mods = mods;
            if (this.selectedMod) {
                this.selectedMod = mods.find(m => m.folder_name === this.selectedMod.folder_name) || null;
            }
            if (!this.selectedMod && mods.length > 0) this.selectedMod = mods[0];
        },
        /** 选中某个mod，展示mod详情 **/
        selectMod(mod) { this.selectedMod = mod; },
        /** 勾选/取消勾选mod**/
        toggleCheck(mod) {
            const idx = this.checkedMods.indexOf(mod.folder_name);
            if (idx > -1) {
                this.checkedMods.splice(idx, 1);
            } else {
                this.checkedMods.push(mod.folder_name);
            }
        },
        /**判断是否已勾选**/
        isChecked(mod) {
            return this.checkedMods.includes(mod.folder_name);
        },
        async activateMod() {
            if (this.checkedMods.length === 0) {
                this.showToast('请先勾选要激活的 MOD', 'orange');
                return;
            }
            const r = await pywebview.api.activate_mods(this.checkedMods);
            this.showToast(r.msg, r.ok ? 'green' : 'red');
            if (r.ok) {
                this.checkedMods = [];
                await this.fetchMods();
            }
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
            const warningMsg = `确定要删除 MOD "${this.selectedMod.name}" 吗？\n\n此操作不可撤销。`;

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
                     class="mod-item" :class="{selected: selectedMod && selectedMod.folder_name === mod.folder_name}">
                    <input type="checkbox"
                           :checked="isChecked(mod)"
                           @change="toggleCheck(mod)"
                           @click.stop
                           style="margin-right: 8px; cursor: pointer;">
                    <div class="mod-item-info" @click="selectMod(mod)" style="flex: 1; cursor: pointer;">
                        <div class="mod-item-name">{{ mod.name }}</div>
                        <div class="mod-item-desc" v-if="mod.description">
                            {{ mod.description.length > 40 ? mod.description.slice(0,40) + '…' : mod.description }}
                        </div>
                    </div>
                </div>
            </div>
            <div class="mod-actions">
                <button class="btn btn-primary btn-block" @click="activateMod">
                    ▶ 激活勾选的 MOD ({{ checkedMods.length }})
                </button>
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
                </div>
                <p class="mod-desc">{{ selectedMod.description || '暂无描述' }}</p>
                <p class="mod-meta">作者: {{ selectedMod.author || '未知' }} &nbsp;&nbsp; 版本: {{ selectedMod.version || '未知' }}</p>
                <hr>
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
