const homePage = {
    name: 'HomePage',
    props: ['showToast'],
    data() {
        return {
            confirm: { visible: false, onOk: null },
            restoring: false,
        };
    },
    methods: {
        askRestore() {
            this.confirm = { visible: true, onOk: this.doRestore };
        },
        async doRestore() {
            this.confirm.visible = false;
            this.restoring = true;
            try {
                const r = await pywebview.api.restore_all_files();
                this.showToast(r.msg, r.ok ? 'green' : 'red');
            } catch (e) {
                this.showToast('还原失败: ' + e, 'red');
            } finally {
                this.restoring = false;
            }
        },
    },
    template: `
<div class="page home-page">
    <div class="home-container">

        <!-- 标题区 -->
        <div class="home-hero">
            <h1 class="home-title">ASTLIBRA MOD 工具</h1>
            <p class="home-subtitle">
                为 ASTLIBRA 游戏提供文本编辑与 MOD 管理功能<br>
                支持 12,000+ 条多语言文本的提取、编辑与导入
            </p>
        </div>

        <!-- 功能卡片 -->
        <div class="feature-cards">
            <div class="feature-card">
                <span class="card-icon">💬</span>
                <h3 class="card-title">对话文本编辑</h3>
                <p class="card-desc">
                    提取、编辑并导入游戏对话文本。支持按分类筛选、关键词搜索，双击任意行即可打开编辑器。
                </p>
                <span class="card-tag">12,000+ 条文本</span>
            </div>
            <div class="feature-card">
                <span class="card-icon">🧩</span>
                <h3 class="card-title">MOD 管理</h3>
                <p class="card-desc">
                    文件覆盖式 MOD 系统，将 MOD 文件夹放入 MODS 目录后即可激活。支持图像、音频、字体等任意文件替换。
                </p>
                <span class="card-tag">批量激活</span>
            </div>
        </div>

        <!-- 快速开始 -->
        <div class="quick-start">
            <div class="quick-start-title">快速开始</div>
            <div class="quick-start-steps">
                <div class="step-item">
                    <div class="step-number">1</div>
                    <span class="step-desc">在「对话文本」页点击「开始提取文本」，从 DAT.dxa 提取游戏文本数据</span>
                </div>
                <div class="step-item">
                    <div class="step-number">2</div>
                    <span class="step-desc">在「对话文本」页面浏览、编辑文本，完成后点击「应用到游戏」写入游戏文件</span>
                </div>
                <div class="step-item">
                    <div class="step-number">3</div>
                    <span class="step-desc">将 MOD 文件夹放入 MODS 目录，在「MOD 管理」页面勾选并激活</span>
                </div>
            </div>
        </div>

        <!-- 一键还原 -->
        <div class="restore-zone">
            <button class="btn btn-danger" :disabled="restoring" @click="askRestore">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0">
                    <polyline points="1 4 1 10 7 10"/>
                    <path d="M3.51 15a9 9 0 1 0 .49-3.17"/>
                </svg>
                {{ restoring ? '还原中...' : '一键还原游戏文件' }}
            </button>
            <p class="restore-hint">还原 EXE 原版 + 删除 MOD 覆盖的游戏数据文件夹，恢复备份文件名</p>
        </div>

    </div>

    <!-- 确认对话框 -->
    <div v-if="confirm.visible" class="modal-overlay" @click.self="confirm.visible = false">
        <div class="modal modal-sm">
            <div class="modal-header"><h3>确认还原</h3></div>
            <div class="modal-body">
                <p style="line-height:1.7">
                    此操作将：<br>
                    · 用 <code>ASTLIBRA_back.exe</code> 覆盖当前 EXE<br>
                    · 删除游戏数据文件夹（DAT / Image / Sound 等）<br>
                    · 将备份 dxa 文件恢复为原版文件名<br><br>
                    <span style="color:var(--danger)">已激活的 MOD 效果将全部消失，不可撤销。</span>
                </p>
            </div>
            <div class="modal-footer">
                <button class="btn btn-danger" @click="confirm.onOk && confirm.onOk()">确认还原</button>
                <button class="btn btn-secondary" @click="confirm.visible = false">取消</button>
            </div>
        </div>
    </div>
</div>
    `,
};
