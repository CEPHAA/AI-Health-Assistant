// ============================================
// THEME MANAGER - WORKING VERSION
// ============================================

(function() {
    'use strict';
    
    const THEMES = ['gradient', 'dark', 'light', 'glass'];
    const DEFAULT_THEME = 'gradient';
    
    // Apply theme to body
    function applyTheme(themeName) {
        if (!THEMES.includes(themeName)) {
            themeName = DEFAULT_THEME;
        }
        
        // Set data-theme attribute on body
        document.body.setAttribute('data-theme', themeName);
        
        // Save to localStorage
        try {
            localStorage.setItem('selectedTheme', themeName);
        } catch(e) {
            console.log('localStorage not available');
        }
        
        console.log('✅ Theme applied:', themeName);
    }
    
    // Get saved theme or default
    function getSavedTheme() {
        try {
            const saved = localStorage.getItem('selectedTheme');
            return THEMES.includes(saved) ? saved : DEFAULT_THEME;
        } catch(e) {
            return DEFAULT_THEME;
        }
    }
    
    // Change theme (called from buttons)
    window.changeTheme = function(themeName) {
        applyTheme(themeName);
        
        // Close menu
        const menu = document.getElementById('themeMenu');
        if (menu) {
            menu.classList.remove('show');
        }
        
        // Show notification
        showNotification('Theme changed to ' + themeName);
    };
    
    // Toggle theme menu
    window.toggleThemeMenu = function() {
        const menu = document.getElementById('themeMenu');
        if (menu) {
            menu.classList.toggle('show');
        }
    };
    
    // Show notification
    function showNotification(message) {
        const existing = document.querySelector('.theme-notification');
        if (existing) {
            existing.remove();
        }
        
        const notification = document.createElement('div');
        notification.className = 'theme-notification';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 2000);
    }
    
    // Create theme switcher UI
    function createThemeSwitcher() {
        // Check if already exists
        if (document.querySelector('.theme-switcher-wrapper')) {
            return;
        }
        
        const html = `
            <div class="theme-switcher-wrapper">
                <button class="theme-toggle-btn" onclick="toggleThemeMenu()" aria-label="Change theme">
                    <span>🎨</span>
                    <span>Theme</span>
                </button>
                <div class="theme-menu" id="themeMenu">
                    <h3>Choose Your Theme</h3>
                    <div class="theme-options">
                        <div class="theme-option" onclick="changeTheme('gradient')">
                            <div class="theme-preview gradient-preview"></div>
                            <span>Gradient</span>
                        </div>
                        <div class="theme-option" onclick="changeTheme('dark')">
                            <div class="theme-preview dark-preview"></div>
                            <span>Dark Mode</span>
                        </div>
                        <div class="theme-option" onclick="changeTheme('light')">
                            <div class="theme-preview light-preview"></div>
                            <span>Light Mode</span>
                        </div>
                        <div class="theme-option" onclick="changeTheme('glass')">
                            <div class="theme-preview glass-preview"></div>
                            <span>Glass</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', html);
    }
    
    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        const menu = document.getElementById('themeMenu');
        const button = document.querySelector('.theme-toggle-btn');
        
        if (menu && button && 
            !menu.contains(event.target) && 
            !button.contains(event.target)) {
            menu.classList.remove('show');
        }
    });
    
    // Initialize on DOM ready
    function init() {
        // Apply saved theme immediately
        const savedTheme = getSavedTheme();
        applyTheme(savedTheme);
        
        // Create theme switcher UI
        createThemeSwitcher();
        
        console.log('✅ Theme system initialized');
    }
    
    // Run initialization
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
