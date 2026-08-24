/**
 * THE MIDDLEMAN KILLER - Master SPA Controller & Multi-Language Router
 */

window.MKApp = {
    userSession: null,
    activeView: 'landingView',
    currentTheme: localStorage.getItem('mk_theme_mode') || 'dark',

    init() {
        this.initTheme();
        this.initLucide();
        this.initTicker();
        this.initAuthSession();
        this.renderMarketplace();
        this.renderRegionalTable();

        // Apply saved language
        if (window.MKI18n) {
            window.MKI18n.setLanguage(window.MKI18n.currentLang);
        }

        // Initialize sub-modules
        if (window.MKAuction) window.MKAuction.initAuction();
        if (window.MKCharts) {
            window.MKCharts.initFarmerCharts();
            window.MKCharts.initAdminCharts();
        }
        if (window.MKAI) window.MKAI.drawFairPriceRadar();
        if (window.MKLogistics) window.MKLogistics.initMap();

        console.log("🌾 The Middleman Killer Platform Initialized with Multi-Language & Gujarat Map!");
    },

    initTheme() {
        if (this.currentTheme === 'light') {
            document.body.classList.add('light-mode');
        } else {
            document.body.classList.remove('light-mode');
        }
    },

    toggleWebsiteTheme() {
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        localStorage.setItem('mk_theme_mode', this.currentTheme);
        this.initTheme();
        this.renderDynamicNavigation();
        if (window.MKLogistics && window.MKLogistics.map) {
            window.MKLogistics.setMapTileStyle(this.currentTheme);
            window.MKLogistics.renderMapToggleOverlay();
        }
        this.notify('THEME TOGGLED', `Switched website to ${this.currentTheme.toUpperCase()} mode`, 'gold');
    },

    initLucide() {
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    },

    initTicker() {
        const moveEl = document.getElementById('tickerMove');
        if (!moveEl) return;

        const itemsHTML = window.MKData.marketTicker.map(t => `
            <div class="ticker-item">
                <span>${t.crop}</span>
                <span style="font-weight:700;">${t.price}</span>
                <span class="${t.positive ? 'positive' : 'negative'}">${t.change}</span>
            </div>
        `).join('');

        moveEl.innerHTML = itemsHTML + itemsHTML;
    },

    // -------------------------------------------------------------
    // AUTHENTICATION & LOCALSTORAGE SESSION MANAGEMENT
    // -------------------------------------------------------------
    initAuthSession() {
        const saved = localStorage.getItem('mk_user_session');
        if (saved) {
            try {
                this.userSession = JSON.parse(saved);
            } catch(e) {
                this.userSession = null;
            }
        }
        this.renderDynamicNavigation();
    },

    loginUserSession(userObj) {
        this.userSession = userObj;
        localStorage.setItem('mk_user_session', JSON.stringify(userObj));
        this.renderDynamicNavigation();

        if (userObj.role === 'farmer') {
            this.switchView('farmerDashboardView');
        } else if (userObj.role === 'buyer') {
            this.switchView('marketplaceView');
        } else if (userObj.role === 'admin') {
            this.switchView('adminDashboardView');
        }
    },

    async loginWithCredentials(identifier, password) {
        if (!identifier || !identifier.trim()) {
            this.notify('LOGIN ERROR', 'Please enter your email or mobile number.', 'orange');
            return;
        }

        if (!password) {
            this.notify('LOGIN ERROR', 'Please enter your password.', 'orange');
            return;
        }

        const loginBtn = document.getElementById('loginSubmitBtn');
        if (loginBtn) loginBtn.innerHTML = '<i data-lucide="loader" class="animate-spin"></i> Authenticating...';

        const user = await window.MKAPI.login(identifier.trim(), password);

        if (loginBtn) loginBtn.innerHTML = 'Sign In';

        if (user) {
            this.loginUserSession({
                name: user.name,
                email: user.email,
                mobile: user.mobile,
                role: user.role,
                verified: user.verified,
                avatar: user.avatar || '🌱'
            });
            this.closeModal('authModal');
            this.notify('WELCOME BACK', `Logged in as ${user.name} (${user.role.toUpperCase()})`, 'green');
        } else {
            this.notify('INVALID CREDENTIALS', 'Invalid email/mobile number or password.', 'orange');
        }
    },

    logoutUser() {
        this.openModal('logoutModal');
    },

    confirmLogout() {
        this.userSession = null;
        localStorage.removeItem('mk_user_session');
        this.closeModal('logoutModal');
        this.closeSidebar();
        this.renderDynamicNavigation();
        this.switchView('landingView');
        this.notify('LOGGED OUT', 'You have ended your session safely.', 'gold');
    },

    // -------------------------------------------------------------
    // DYNAMIC ROLE NAVIGATION & MULTI-LANGUAGE RENDERER
    // -------------------------------------------------------------
    renderDynamicNavigation() {
        const navActions = document.getElementById('navActions');
        const sidebarMenu = document.getElementById('sidebarMenuList');
        const userProfileArea = document.getElementById('sidebarUserProfile');
        const publicNavMenu = document.getElementById('publicNavMenu');

        const role = this.userSession ? this.userSession.role : 'guest';
        const i18n = window.MKI18n;

        // Update Public Nav Top Links with i18n
        if (publicNavMenu) {
            if (role === 'farmer') {
                publicNavMenu.innerHTML = `
                    <li><a class="nav-link" onclick="MKApp.switchView('farmerDashboardView')"><i data-lucide="layout-dashboard"></i> ${i18n ? i18n.getText('navFarmerPortal') : 'Farmer Portal'}</a></li>
                    <li><a class="nav-link" onclick="MKApp.switchView('fairPriceRadarView')"><i data-lucide="radar"></i> ${i18n ? i18n.getText('navFairPrice') : 'Fair Price AI'}</a></li>
                    <li><a class="nav-link" onclick="MKApp.switchView('marketplaceView')"><i data-lucide="shopping-bag"></i> ${i18n ? i18n.getText('navMarketplace') : 'Marketplace'}</a></li>
                    <li><a class="nav-link" onclick="MKApp.switchView('liveAuctionView')"><i data-lucide="zap"></i> ${i18n ? i18n.getText('navAuctions') : 'Live Auctions'}</a></li>
                    <li><a class="nav-link" onclick="MKApp.switchView('logisticsView')"><i data-lucide="truck"></i> ${i18n ? i18n.getText('navLogistics') : 'Logistics'}</a></li>
                `;
            } else if (role === 'buyer') {
                publicNavMenu.innerHTML = `
                    <li><a class="nav-link" onclick="MKApp.switchView('marketplaceView')"><i data-lucide="shopping-bag"></i> ${i18n ? i18n.getText('navMarketplace') : 'Buyer Marketplace'}</a></li>
                    <li><a class="nav-link" onclick="MKApp.switchView('liveAuctionView')"><i data-lucide="zap"></i> ${i18n ? i18n.getText('navAuctions') : 'Live Auctions'}</a></li>
                    <li><a class="nav-link" onclick="MKApp.switchView('escrowPaymentView')"><i data-lucide="lock"></i> ${i18n ? i18n.getText('escrowTag') : 'My Escrow'}</a></li>
                    <li><a class="nav-link" onclick="MKApp.switchView('logisticsView')"><i data-lucide="truck"></i> ${i18n ? i18n.getText('navLogistics') : 'Tracking'}</a></li>
                `;
            } else if (role === 'admin') {
                publicNavMenu.innerHTML = `
                    <li><a class="nav-link" onclick="MKApp.switchView('adminDashboardView')"><i data-lucide="shield-check"></i> ${i18n ? i18n.getText('navAdmin') : 'Admin Command'}</a></li>
                    <li><a class="nav-link" onclick="MKApp.switchView('marketplaceView')"><i data-lucide="sprout"></i> ${i18n ? i18n.getText('navMarketplace') : 'Crop Management'}</a></li>
                    <li><a class="nav-link" onclick="MKApp.switchView('liveAuctionView')"><i data-lucide="zap"></i> ${i18n ? i18n.getText('navAuctions') : 'Auctions'}</a></li>
                `;
            } else {
                publicNavMenu.innerHTML = `
                    <li><a class="nav-link active" onclick="MKApp.switchView('landingView')"><i data-lucide="home"></i> ${i18n ? i18n.getText('navHome') : 'Home'}</a></li>
                    <li><a class="nav-link" onclick="MKApp.switchView('fairPriceRadarView')"><i data-lucide="radar"></i> ${i18n ? i18n.getText('navFairPrice') : 'Fair Price AI'}</a></li>
                    <li><a class="nav-link" onclick="MKApp.switchView('marketplaceView')"><i data-lucide="shopping-bag"></i> ${i18n ? i18n.getText('navMarketplace') : 'Marketplace'}</a></li>
                    <li><a class="nav-link" onclick="MKApp.switchView('liveAuctionView')"><i data-lucide="zap"></i> ${i18n ? i18n.getText('navAuctions') : 'Live Auction'}</a></li>
                `;
            }
        }

        // Language Switcher Selector Component
        const langSelectorHTML = `
            <select class="form-control" style="padding: 6px 12px; font-size: 0.82rem; background: rgba(18,55,42,0.8); border: 1px solid var(--border-glow); color: var(--accent-gold); font-weight:700; width:auto; cursor:pointer;" onchange="MKI18n.setLanguage(this.value)">
                <option value="en" ${i18n && i18n.currentLang === 'en' ? 'selected' : ''}>🇬🇧 English</option>
                <option value="gu" ${i18n && i18n.currentLang === 'gu' ? 'selected' : ''}>🇮🇳 ગુજરાતી</option>
                <option value="hi" ${i18n && i18n.currentLang === 'hi' ? 'selected' : ''}>🇮🇳 हिन्दी</option>
            </select>
        `;

        // Theme Toggle Button Component
        const themeToggleHTML = `
            <button class="btn theme-toggle-btn" style="padding: 6px 12px; font-size: 0.82rem; background: rgba(18,55,42,0.8); border: 1px solid var(--border-glow); color: var(--accent-gold); font-weight:700; cursor:pointer;" onclick="MKApp.toggleWebsiteTheme()" title="Toggle Dark/Light Mode">
                ${this.currentTheme === 'dark' ? '🌙 Dark' : '☀️ Light'}
            </button>
        `;

        // Update Top Right Actions
        if (navActions) {
            if (this.userSession) {
                const avatar = this.userSession.avatar || (role === 'farmer' ? '🌱' : role === 'buyer' ? '🏢' : '🛡️');
                navActions.innerHTML = `
                    ${themeToggleHTML}
                    ${langSelectorHTML}
                    <button class="user-profile-badge" onclick="MKApp.toggleSidebar()">
                        <span>${avatar}</span>
                        <div style="text-align:left;">
                            <div style="font-weight:700; font-size:0.85rem; color:var(--text-ivory);">${this.userSession.name}</div>
                            <div style="font-size:0.7rem; color:var(--accent-gold); text-transform:uppercase;">${role} ✓</div>
                        </div>
                        <i data-lucide="menu" style="margin-left:4px;"></i>
                    </button>
                `;
            } else {
                navActions.innerHTML = `
                    ${themeToggleHTML}
                    ${langSelectorHTML}
                    <button class="btn btn-secondary" onclick="MKApp.openModal('authModal')">
                        <i data-lucide="user"></i> ${i18n ? i18n.getText('navLoginRegister') : 'Login / Register'}
                    </button>
                    <button class="btn btn-primary" onclick="MKApp.openModal('authModal')">
                        ${i18n ? i18n.getText('navSellDirect') : 'Start Selling'}
                    </button>
                `;
            }
        }

        // Update Slide-Out Sidebar Drawer
        if (sidebarMenu && this.userSession) {
            const menuItems = window.MKData.roleNavMenus[role] || [];
            sidebarMenu.innerHTML = menuItems.map(m => `
                <li class="sidebar-item" onclick="${m.action === 'openCropModal' ? 'MKApp.openModal(\'cropRegModal\')' : m.action === 'toggleKrishi' ? 'MKApp.toggleKrishiChat()' : `MKApp.switchView('${m.id}')`}">
                    <i data-lucide="${m.icon}"></i>
                    <span>${i18n ? i18n.getText(m.labelKey) : m.labelKey}</span>
                </li>
            `).join('') + `
                <li class="sidebar-item" style="color:var(--accent-red-bright); margin-top:20px;" onclick="MKApp.logoutUser()">
                    <i data-lucide="log-out"></i>
                    <span>${i18n ? i18n.getText('btnLogout') : 'Log Out Session'}</span>
                </li>
            `;
        }

        if (userProfileArea && this.userSession) {
            userProfileArea.innerHTML = `
                <div style="display:flex; align-items:center; gap:12px; background:rgba(18,55,42,0.6); padding:12px; border-radius:12px; border:1px solid var(--border-subtle);">
                    <div style="font-size:1.8rem;">${this.userSession.avatar || '🌱'}</div>
                    <div>
                        <div style="font-weight:800; font-size:0.95rem; color:var(--text-ivory);">${this.userSession.name}</div>
                        <div style="font-size:0.75rem; color:var(--accent-green-bright); font-weight:700;">${this.userSession.role.toUpperCase()} • Verified ✓</div>
                    </div>
                </div>
            `;
        }

        this.initLucide();
    },

    toggleSidebar() {
        const sidebar = document.getElementById('sidebarDrawer');
        if (sidebar) sidebar.classList.toggle('active');
    },

    closeSidebar() {
        const sidebar = document.getElementById('sidebarDrawer');
        if (sidebar) sidebar.classList.remove('active');
    },

    switchView(viewId) {
        const role = this.userSession ? this.userSession.role : 'guest';

        if (viewId === 'trustScoreSection') {
            this.switchView('farmerDashboardView');
            setTimeout(() => {
                const el = document.getElementById('trustScoreSection');
                if (el) el.scrollIntoView({ behavior: 'smooth' });
            }, 150);
            return;
        }

        if (viewId === 'adminDashboardView' && role !== 'admin') {
            this.notify('ACCESS DENIED', 'Admin credentials required to access system command center.', 'orange');
            this.openModal('authModal');
            return;
        }

        if (viewId === 'farmerDashboardView' && role !== 'farmer' && role !== 'admin') {
            this.notify('FARMER ACCESS REQUIRED', 'Please login with a Farmer account.', 'orange');
            this.openModal('authModal');
            return;
        }

        const views = document.querySelectorAll('.view-section');
        views.forEach(v => v.style.display = 'none');

        const activeEl = document.getElementById(viewId);
        if (activeEl) {
            activeEl.style.display = 'block';
            this.activeView = viewId;
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        // Update active class on top navigation links
        document.querySelectorAll('#publicNavMenu .nav-link').forEach(link => {
            const onclickAttr = link.getAttribute('onclick') || '';
            if (onclickAttr.includes(`'${viewId}'`)) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });

        this.closeSidebar();
        this.initLucide();

        if (viewId === 'farmerDashboardView' && window.MKCharts) window.MKCharts.initFarmerCharts();
        else if (viewId === 'adminDashboardView' && window.MKCharts) window.MKCharts.initAdminCharts();
        else if (viewId === 'fairPriceRadarView' && window.MKAI) window.MKAI.drawFairPriceRadar();
        else if (viewId === 'logisticsView' && window.MKLogistics) window.MKLogistics.initMap();
    },

    renderMarketplace(filterCategory = 'ALL') {
        const grid = document.getElementById('cropGridContainer');
        if (!grid) return;

        let items = window.MKData.crops;
        if (filterCategory !== 'ALL') {
            items = items.filter(c => c.category === filterCategory);
        }

        const i18n = window.MKI18n;

        grid.innerHTML = items.map(c => `
            <div class="crop-card">
                <div style="position:relative;">
                    <img src="${c.image}" class="crop-card-image" alt="${c.title}" />
                    <div class="crop-card-badges">
                        ${c.verified ? `<span class="badge badge-green"><i data-lucide="check-circle"></i> Verified</span>` : ''}
                        ${c.isAuction ? `<span class="badge badge-orange"><i data-lucide="zap"></i> Live Auction</span>` : ''}
                    </div>
                    <div class="crop-quality-tag">
                        <i data-lucide="award"></i> AI Quality ${c.qualityScore}/100
                    </div>
                </div>
                <div class="crop-card-body">
                    <h3 class="crop-card-title">${c.title}</h3>
                    <div class="crop-farmer-meta">
                        <i data-lucide="map-pin"></i> ${c.farmer} (${c.location})
                    </div>
                    <div class="crop-price-row">
                        <div class="price-box">
                            <label>AI Fair Price</label>
                            <div class="val">${c.fairPrice}</div>
                        </div>
                        <div class="price-box" style="text-align:right;">
                            <label>${c.isAuction ? 'Current Bid' : 'Direct Buy'}</label>
                            <div class="val" style="color:var(--accent-orange);">${c.currentBid}</div>
                        </div>
                    </div>
                    <div style="margin-top: 16px; display:flex; gap:10px;">
                        ${c.isAuction ? `
                            <button class="btn btn-primary" style="flex:1;" onclick="MKApp.switchView('liveAuctionView')">
                                ${i18n ? i18n.getText('btnPlaceBid') : 'Place Bid'}
                            </button>
                        ` : `
                            <button class="btn btn-gold" style="flex:1;" onclick="MKApp.buyCropDirect('${c.title}', '${c.currentBid}')">
                                ${i18n ? i18n.getText('btnBuyDirect') : 'Buy Direct'}
                            </button>
                        `}
                    </div>
                </div>
            </div>
        `).join('');

        this.initLucide();
    },

    filterCategory(category, element) {
        document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
        if (element) element.classList.add('active');
        this.renderMarketplace(category);
    },

    buyCropDirect(title, price) {
        this.notify('ESCROW INITIATED', `Locked ${price} for ${title}. Proceeding to shipment tracking...`, 'gold');
        this.switchView('escrowPaymentView');
    },

    renderRegionalTable() {
        const tbody = document.getElementById('regionalTableBody');
        if (!tbody) return;

        tbody.innerHTML = window.MKData.regionalMapData.map(r => `
            <tr>
                <td style="font-weight:700; color:var(--accent-gold);">${r.city}</td>
                <td>${r.activeFarmers}</td>
                <td style="font-weight:700;">${r.tradeVolume}</td>
                <td>${r.topCrop}</td>
                <td><span class="risk-indicator risk-low">${r.riskLevel}</span></td>
            </tr>
        `).join('');
    },

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.add('active');
    },

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.remove('active');
    },

    toggleKrishiChat() {
        const panel = document.getElementById('krishiChatPanel');
        if (panel) panel.classList.toggle('active');
    },

    notify(title, message, type = 'orange') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `glass-card`;
        toast.style.cssText = `
            padding: 14px 20px;
            min-width: 300px;
            border-left: 4px solid ${type === 'gold' ? '#D6A84F' : type === 'green' ? '#2ECC71' : '#D96C3B'};
            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
            animation: floatSlow 0.3s ease-out;
        `;

        toast.innerHTML = `
            <div style="font-weight:800; font-size:0.9rem; color:var(--text-ivory);">${title}</div>
            <div style="font-size:0.8rem; color:var(--text-muted);">${message}</div>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-10px)';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    window.MKApp.init();
});
