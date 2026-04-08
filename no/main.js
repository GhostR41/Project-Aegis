document.addEventListener('DOMContentLoaded', () => {
    // ── Custom Cursor ──
    const cursor = document.getElementById('custom-cursor');
    if (cursor) {
        document.addEventListener('mousemove', (e) => {
            cursor.style.left = e.clientX + 'px';
            cursor.style.top = e.clientY + 'px';
        });
        document.addEventListener('mouseenter', () => cursor.style.opacity = '1');
        document.addEventListener('mouseleave', () => cursor.style.opacity = '0');
    }

    // ── Core DOM References ──
    const mainTitle = document.getElementById('main-title');
    const topBar = document.getElementById('top-bar');
    const sections = document.querySelectorAll('.content-section');

    // ── Reveal sections on scroll via IntersectionObserver ──
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
            }
        });
    }, { root: null, rootMargin: '0px', threshold: 0.15 });

    sections.forEach(section => sectionObserver.observe(section));

    // DART image wrapper slide-in
    const dartImageWrapper = document.querySelector('.dart-image-wrapper');
    if (dartImageWrapper) sectionObserver.observe(dartImageWrapper);

    // Incident cards
    document.querySelectorAll('.incident-card').forEach(card => sectionObserver.observe(card));

    // ── DART Labels logic ──
    const dartTrigger = document.getElementById('dart-sensor-trigger');
    const diagramLabels = document.querySelectorAll('.diagram-label');
    
    if (dartTrigger) {
        const dartObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    diagramLabels.forEach(label => label.classList.add('visible'));
                } else {
                    diagramLabels.forEach(label => label.classList.remove('visible'));
                }
            });
        }, { threshold: 0.4 });
        dartObserver.observe(dartTrigger);
    }



    let lastScrollY = window.scrollY;
    let ticking = false;

    window.addEventListener('scroll', () => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                const currentScrollY = window.scrollY;
                const windowHeight = window.innerHeight;

                // Title fade-out
                const progress = Math.min(currentScrollY / (windowHeight * 0.4), 1);
                if (mainTitle) {
                    mainTitle.style.opacity = Math.max(0, 1 - progress);
                    mainTitle.style.transform = `translate(-50%, -50%) scale(${1 + (progress * 0.2)})`;
                }

                // Utility Bar: visible during video, hide/show after
                const videoSectionHeight = windowHeight * 0.85;
                if (currentScrollY < videoSectionHeight) {
                    topBar.classList.add('visible');
                } else {
                    if (currentScrollY < lastScrollY) {
                        topBar.classList.add('visible');
                    } else if (currentScrollY > lastScrollY) {
                        topBar.classList.remove('visible');
                    }
                }

                // Incident card parallax
                const incidentCards = document.querySelectorAll('.incident-card');
                incidentCards.forEach(card => {
                    const speed = parseFloat(card.dataset.speed) || 0;
                    const rect = card.getBoundingClientRect();
                    if (rect.top < windowHeight && rect.bottom > 0) {
                        const offset = (windowHeight - rect.top) * speed;
                        card.style.transform = card.classList.contains('in-view') ? `translateY(${offset}px)` : '';
                    }
                });

                lastScrollY = currentScrollY;
                ticking = false;
            });
            ticking = true;
        }
    });

    // ── Smooth scroll for anchor links ──
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetElement = document.querySelector(this.getAttribute('href'));
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // ── "Start with it" Expressive Typography Transition ──
    const startBtn = document.getElementById('start-with-it-btn');
    if (startBtn) {
        startBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const href = startBtn.getAttribute('href');
            const overlay = document.createElement('div');
            overlay.className = 'page-transition-overlay';
            const textEl = document.createElement('div');
            textEl.className = 'transition-text';
            'Project: Aegis'.split('').forEach((char, i) => {
                const span = document.createElement('span');
                span.className = 'char';
                span.textContent = char === ' ' ? '\u00A0' : char;
                span.style.animationDelay = `${i * 0.05}s`;
                textEl.appendChild(span);
            });
            overlay.appendChild(textEl);
            document.body.appendChild(overlay);
            requestAnimationFrame(() => overlay.classList.add('active'));
            setTimeout(() => { window.location.href = href; }, 1200);
        });
    }

    window.dispatchEvent(new Event('scroll'));
    console.log('Project Aegis UI loaded.');
});
