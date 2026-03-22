

document.addEventListener('DOMContentLoaded', () => {
    const videoBg = document.getElementById('video-bg');
    const contentSection = document.getElementById('white-content');
    const mainTitle = document.getElementById('main-title');
    const titleContainer = document.getElementById('title-container');
    const topBar = document.getElementById('top-bar');

    // Configuration
    const fadeEnd = window.innerHeight; // When full transition should be complete

    window.addEventListener('scroll', () => {
        const scrollY = window.scrollY;

        // Normalize scroll progress (0 to 1) over the viewport height
        let progress = Math.min(Math.max(scrollY / fadeEnd, 0), 1);

        // 1. Video Background Opacity (Fades out as we scroll down)
        videoBg.style.opacity = 1 - progress;

        // 2. White Content Section Opacity/Appearance
        contentSection.style.opacity = Math.max(0, (progress - 0.3) * 1.43);
        if (progress >= 0.7) {
            contentSection.style.opacity = 1;
        }

        // 3. Main Title: Fades out quickly as we scroll (disappears before top bar is visible)
        // Fade out completely within the first 40% of scroll
        const titleOpacity = Math.max(0, 1 - (progress * 3));
        mainTitle.style.opacity = titleOpacity;

        // Dynamic text color based on background:
        // Start: White (#ffffff) on dark video background -> RGB(255, 255, 255)
        // End: Dark (#1a1a1a) as white content appears -> RGB(26, 26, 26)
        const startColor = { r: 255, g: 255, b: 255 };
        const endColor = { r: 26, g: 26, b: 26 };

        const r = Math.round(startColor.r + (endColor.r - startColor.r) * progress);
        const g = Math.round(startColor.g + (endColor.g - startColor.g) * progress);
        const b = Math.round(startColor.b + (endColor.b - startColor.b) * progress);

        mainTitle.style.color = `rgb(${r}, ${g}, ${b})`;

        // Also hide the container entirely once faded
        if (progress > 0.35) {
            titleContainer.style.visibility = 'hidden';
        } else {
            titleContainer.style.visibility = 'visible';
        }

        // 4. Top Bar: Fades in with scroll progress
        topBar.style.opacity = progress;
        if (progress > 0.1) {
            topBar.classList.add('visible');
        } else {
            topBar.classList.remove('visible');
        }
    });

    // Trigger once on load to set initial state
    window.dispatchEvent(new Event('scroll'));

    console.log('Project Aegis: Initialized');
});
