const homePage = {
    name: 'HomePage',
    props: ['showToast'],
    template: `
<div class="page home-page">
    <div class="home-container">
        <div class="home-header">
            <h1 class="home-title">ASTLIBRA MOD 工具</h1>
            <p class="home-subtitle">轻松制作和管理游戏 MOD</p>
        </div>
        <div class="feature-cards">
            <div class="feature-card">
                <div class="card-icon">💬</div>
                <h3 class="card-title">对话文本编辑</h3>
                <p class="card-desc">提取、编辑、导入游戏对话文本<br>目前仅支持简体中文，12000+ 条对话</p>
            </div>
            <div class="feature-card">
                <div class="card-icon">🧩</div>
                <h3 class="card-title">MOD 管理</h3>
                <p class="card-desc">文件覆盖式 MOD 系统<br>支持图像、音频、字体等任意文件替换</p>
            </div>
        </div>
        <div class="quick-start">
            <h2>快速开始</h2>
            <ol>
                <li>点击左侧导航栏选择功能模块</li>
                <li>对话文本：提取 DAT 文件，编辑后导入</li>
                <li>MOD 管理：创建 MOD 包，激活后即可在游戏中使用</li>
            </ol>
        </div>
    </div>
</div>
    `,
};
