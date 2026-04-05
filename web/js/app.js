const { createApp } = Vue;

const rootApp = createApp({
    components: { homePage, dialoguePage, modPage },
    data() {
        return {
            currentPage: 'home',
            pages: [
                { key: 'home', icon: '🏠', label: '主页' },
                { key: 'dialogue', icon: '💬', label: '对话文本' },
                { key: 'mod', icon: '🧩', label: 'MOD管理' },
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
                if (!info.detected) { this.gameDetected = false; return; }
                if (!info.has_csv) {
                    await this.startExtraction();
                } else {
                    this.showToast('已加载游戏文本数据', 'blue');
                }
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
        // window.addEventListener('pywebviewready', () => this.startup());
        // if (window.pywebview) this.startup();
    },
    template: `
<div>
    <div v-if="extracting || extractionError || !gameDetected" class="overlay">
        <div class="dialog-box">
            <template v-if="!gameDetected">
                <h2 class="error-title">⚠ 未找到游戏目录</h2>
                <p style="margin-top:12px;color:var(--text-secondary)">请将工具放在游戏目录的子文件夹中</p>
            </template>
            <template v-else-if="extractionError">
                <h2 class="error-title">提取失败</h2>
                <p class="error-msg">{{ extractionError }}</p>
                <button class="btn btn-danger" style="margin-top:16px" @click="extractionError=null">关闭</button>
            </template>
            <template v-else>
                <h2 style="margin-bottom:16px">首次启动 - 提取文本</h2>
                <p class="step-text">{{ extractionStep }}</p>
                <div class="progress-bar" style="margin-top:16px"><div class="progress-fill"></div></div>
            </template>
        </div>
    </div>
    <div class="app-container">
        <aside class="sidebar">
            <div class="sidebar-header">
                <span class="sidebar-logo">ASTLIBRA<br>MOD工具</span>
            </div>
            <nav class="sidebar-nav">
                <button v-for="page in pages" :key="page.key"
                        class="nav-btn" :class="{active: currentPage === page.key}"
                        @click="navigate(page.key)">
                    <span class="nav-icon">{{ page.icon }}</span>
                    <span class="nav-label">{{ page.label }}</span>
                </button>
            </nav>
        </aside>
        <main class="main-content">
            <component :is="currentComponent" :show-toast="showToast" :start-extraction="startExtraction"></component>
        </main>
    </div>
    <div v-if="toast.visible" class="toast" :class="'toast-' + toast.type">
        {{ toast.message }}
    </div>
</div>
    `,
});

rootApp.mount('#app');
