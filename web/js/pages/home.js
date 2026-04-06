const homePage = {
    name: 'HomePage',
    props: ['showToast', 'askRestoreAll', 'restoring'],
    data() { return {}; },
    methods: {},
    template: `
<div class="page home-page">
    <div class="home-container">

        <!-- 标题区 -->
        <div class="home-hero">
<h1 class="home-title">文本编辑 & MOD 管理</h1>
            <p class="home-subtitle">为 ASTLIBRA 游戏提供文本提取、多语言编辑与文件覆盖式 MOD 系统</p>
        </div>

        <!-- 功能卡片 -->
        <div class="feature-cards">
            <div class="feature-card">
                <div class="card-icon-wrap card-icon-blue">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                    </svg>
                </div>
                <h3 class="card-title">对话文本编辑</h3>
                <p class="card-desc">提取、编辑并导入游戏对话文本。支持按分类筛选、关键词搜索，双击任意行即可打开编辑器。</p>
            </div>
            <div class="feature-card">
                <div class="card-icon-wrap card-icon-violet">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>
                    </svg>
                </div>
                <h3 class="card-title">MOD 管理</h3>
                <p class="card-desc">文件覆盖式 MOD 系统，将 MOD 文件夹放入 MODS 目录后即可激活。支持图像、音频、字体等任意文件替换。</p>
            </div>
        </div>

        <!-- 快速开始 -->
        <div class="quick-start">
            <div class="quick-start-title">快速开始</div>
            <div class="quick-start-steps">
                <div class="step-item">
                    <div class="step-track">
                        <div class="step-number">1</div>
                        <div class="step-connector"></div>
                    </div>
                    <div class="step-body">
                        <div class="step-title">提取游戏文本</div>
                        <div class="step-desc">在「对话文本」页点击「开始提取文本」，从 DAT.dxa 提取游戏文本数据</div>
                    </div>
                </div>
                <div class="step-item">
                    <div class="step-track">
                        <div class="step-number">2</div>
                        <div class="step-connector"></div>
                    </div>
                    <div class="step-body">
                        <div class="step-title">编辑并应用到游戏</div>
                        <div class="step-desc">浏览、编辑文本，完成后点击「应用到游戏」写入游戏文件</div>
                    </div>
                </div>
                <div class="step-item">
                    <div class="step-track">
                        <div class="step-number">3</div>
                    </div>
                    <div class="step-body">
                        <div class="step-title">激活 MOD</div>
                        <div class="step-desc">将 MOD 文件夹放入 MODS 目录，在「MOD 管理」页面勾选并激活</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 危险区域 -->
        <div class="danger-zone">
            <div class="danger-zone-info">
                <div class="danger-zone-label">
                    <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                        <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                    </svg>
                    一键还原游戏文件
                </div>
                <div class="danger-zone-hint">还原 EXE 原版 + 删除 MOD 覆盖的游戏数据文件夹，恢复备份文件名</div>
            </div>
            <button class="btn btn-danger" :disabled="restoring" @click="askRestoreAll">
                <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0">
                    <polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.17"/>
                </svg>
                {{ restoring ? '还原中...' : '立即还原' }}
            </button>
        </div>

    </div>

</div>
    `,
};
