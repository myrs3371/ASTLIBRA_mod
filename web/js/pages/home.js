const homePage = {
    name: 'HomePage',
    props: ['showToast'],
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
                    <span class="step-desc">首次使用时，工具会自动从 DAT.dxa 提取游戏文本数据</span>
                </div>
                <div class="step-item">
                    <div class="step-number">2</div>
                    <span class="step-desc">在「对话文本」页面浏览、编辑文本，完成后点击「应用到游戏」写入游戏文件</span>
                </div>
                <div class="step-item">
                    <div class="step-number">3</div>
                    <span class="step-desc">将 MOD 文件夹放入 MODS 目录，在「MOD 管理」页面勾选并激活，还可随时一键还原原版文件</span>
                </div>
            </div>
        </div>

    </div>
</div>
    `,
};
