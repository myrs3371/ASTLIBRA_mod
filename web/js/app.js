const { createApp } = Vue;

/* ── SVG icon strings (Lucide-style, 16×16, stroke-only) ── */
const ICONS = {
    home: `<svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`,
    list: `<svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>`,
    layers: `<svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>`,
};

const rootApp = createApp({
    components: { homePage, dialoguePage, modPage },
    data() {
        return {
            currentPage: 'home',
            pages: [
                { key: 'home',     iconSvg: ICONS.home,   label: '主页' },
                { key: 'dialogue', iconSvg: ICONS.list,   label: '对话文本' },
                { key: 'mod',      iconSvg: ICONS.layers, label: 'MOD 管理' },
            ],
            toast: { visible: false, message: '', type: 'blue' },
            extracting: false,
            extractionStep: '正在初始化...',
            extractionError: null,
            gameDetected: true,
        };
    },
    computed: {
        currentComponent() {
            return { home: homePage, dialogue: dialoguePage, mod: modPage }[this.currentPage];
        },
    },
    methods: {
        navigate(page) { this.currentPage = page; },
        showToast(message, type = 'blue') {
            this.toast = { visible: true, message, type };
            clearTimeout(this._toastTimer);
            this._toastTimer = setTimeout(() => { this.toast.visible = false; }, 3000);
        },
        async startup() {
            try {
                const info = await pywebview.api.get_game_info();
                if (!info.detected) { this.gameDetected = false; }
            } catch (e) { console.error('Startup error:', e); }
        },
        async startExtraction(onSuccess) {
            this.extracting = true;
            this.extractionError = null;
            const result = await pywebview.api.start_extraction();
            if (!result.started) {
                this.extracting = false;
                this.extractionError = result.error || '启动失败';
                return;
            }
            const poll = setInterval(async () => {
                const status = await pywebview.api.get_extraction_status();
                this.extractionStep = status.step;
                if (status.done) {
                    clearInterval(poll);
                    this.extracting = false;
                    if (status.success) {
                        this.showToast('文本提取成功！', 'green');
                        if (onSuccess) onSuccess();
                    } else {
                        this.extractionError = status.error || '提取失败';
                    }
                }
            }, 500);
        },
    },
    mounted() {
        window.addEventListener('pywebviewready', () => this.startup());
        if (window.pywebview) this.startup();
    },
    template: `
<div>
    <!-- 全屏遮罩：未找到游戏 / 正在提取 / 提取失败 -->
    <div v-if="extracting || extractionError || !gameDetected" class="overlay">
        <div class="dialog-box">
            <template v-if="!gameDetected">
                <h2 class="error-title">未找到游戏目录</h2>
                <p style="margin-top:14px;color:var(--text-secondary);font-size:13px;line-height:1.7">
                    请将工具放在游戏目录的子文件夹中，<br>确保上级目录中存在 ASTLIBRA.exe 和 DATA/
                </p>
            </template>
            <template v-else-if="extractionError">
                <h2 class="error-title">提取失败</h2>
                <p class="error-msg">{{ extractionError }}</p>
                <button class="btn btn-danger" style="margin-top:20px" @click="extractionError=null">关闭</button>
            </template>
            <template v-else>
                <div class="spinner" style="margin:0 auto 16px"></div>
                <h2 style="margin-bottom:10px;font-size:16px">首次启动，正在提取文本</h2>
                <p class="step-text">{{ extractionStep }}</p>
                <div class="progress-bar"><div class="progress-fill"></div></div>
            </template>
        </div>
    </div>

    <div class="app-container">
        <!-- 侧边栏 -->
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-logo">
                    <div class="sidebar-logo-icon">A</div>
                    <div class="sidebar-logo-text">
                        <span class="sidebar-logo-name">ASTLIBRA</span>
                        <span class="sidebar-logo-sub">MOD 工具</span>
                    </div>
                </div>
            </div>
            <nav class="sidebar-nav">
                <button v-for="page in pages" :key="page.key"
                        class="nav-btn" :class="{ active: currentPage === page.key }"
                        @click="navigate(page.key)">
                    <span class="nav-icon" v-html="page.iconSvg"></span>
                    <span>{{ page.label }}</span>
                </button>
            </nav>
            <div class="sidebar-footer">ASTLIBRA MOD Tool</div>
        </aside>

        <!-- 主内容区 -->
        <main class="main-content">
            <component :is="currentComponent"
                       :show-toast="showToast"
                       :start-extraction="startExtraction">
            </component>
        </main>
    </div>

    <!-- Toast 通知 -->
    <div v-if="toast.visible" class="toast" :class="'toast-' + toast.type">
        {{ toast.message }}
    </div>
</div>
    `,
});

rootApp.mount('#app');
