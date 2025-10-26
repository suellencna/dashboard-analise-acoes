/**
 * Sistema de Detecção de Tema e Responsividade
 * Detecta automaticamente o tema do sistema e aplica classes apropriadas
 */

(function() {
    'use strict';

    // Detectar tema do sistema
    function detectSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    // Aplicar tema
    function applyTheme(theme) {
        const body = document.body;
        const html = document.documentElement;
        
        // Remover classes de tema anteriores
        body.classList.remove('theme-light', 'theme-dark');
        html.classList.remove('theme-light', 'theme-dark');
        
        // Aplicar nova classe de tema
        body.classList.add(`theme-${theme}`);
        html.classList.add(`theme-${theme}`);
        
        // Atualizar meta theme-color para mobile
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        
        if (theme === 'dark') {
            metaThemeColor.content = '#1e1e1e';
        } else {
            metaThemeColor.content = '#667eea';
        }
    }

    // Detectar mudanças de tema
    function setupThemeListener() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            // Aplicar tema inicial
            applyTheme(detectSystemTheme());
            
            // Escutar mudanças
            mediaQuery.addListener(function(e) {
                applyTheme(e.matches ? 'dark' : 'light');
            });
        } else {
            // Fallback para navegadores antigos
            applyTheme('light');
        }
    }

    // Detectar tamanho da tela e aplicar classes responsivas
    function setupResponsiveClasses() {
        function updateResponsiveClasses() {
            const width = window.innerWidth;
            const body = document.body;
            
            // Remover classes anteriores
            body.classList.remove('screen-xs', 'screen-sm', 'screen-md', 'screen-lg', 'screen-xl');
            
            // Aplicar classes baseadas no tamanho
            if (width < 480) {
                body.classList.add('screen-xs');
            } else if (width < 768) {
                body.classList.add('screen-sm');
            } else if (width < 1024) {
                body.classList.add('screen-md');
            } else if (width < 1200) {
                body.classList.add('screen-lg');
            } else {
                body.classList.add('screen-xl');
            }
        }

        // Aplicar classes iniciais
        updateResponsiveClasses();
        
        // Escutar mudanças de tamanho
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(updateResponsiveClasses, 100);
        });
    }

    // Melhorar acessibilidade de botões
    function improveButtonAccessibility() {
        // Adicionar suporte a teclado para botões
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                const target = e.target;
                if (target.classList.contains('stButton') || target.tagName === 'BUTTON') {
                    e.preventDefault();
                    target.click();
                }
            }
        });

        // Melhorar foco visual
        document.addEventListener('focusin', function(e) {
            const target = e.target;
            if (target.tagName === 'INPUT' || target.tagName === 'BUTTON' || target.tagName === 'SELECT') {
                target.style.outline = '2px solid var(--primary-color)';
                target.style.outlineOffset = '2px';
            }
        });

        document.addEventListener('focusout', function(e) {
            const target = e.target;
            if (target.tagName === 'INPUT' || target.tagName === 'BUTTON' || target.tagName === 'SELECT') {
                target.style.outline = '';
                target.style.outlineOffset = '';
            }
        });
    }

    // Otimizar performance de scroll
    function optimizeScrollPerformance() {
        let ticking = false;
        
        function updateScrollElements() {
            // Adicionar classes de scroll para animações
            const scrollY = window.scrollY;
            const body = document.body;
            
            if (scrollY > 100) {
                body.classList.add('scrolled');
            } else {
                body.classList.remove('scrolled');
            }
            
            ticking = false;
        }
        
        function requestTick() {
            if (!ticking) {
                requestAnimationFrame(updateScrollElements);
                ticking = true;
            }
        }
        
        window.addEventListener('scroll', requestTick, { passive: true });
    }

    // Inicializar quando o DOM estiver pronto
    function init() {
        setupThemeListener();
        setupResponsiveClasses();
        improveButtonAccessibility();
        optimizeScrollPerformance();
        
        // Adicionar classe de inicialização
        document.body.classList.add('theme-initialized');
    }

    // Executar quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expor funções globalmente para uso manual se necessário
    window.ThemeDetector = {
        applyTheme: applyTheme,
        detectSystemTheme: detectSystemTheme
    };

})();
