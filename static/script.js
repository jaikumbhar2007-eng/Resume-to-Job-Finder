// Seamless Video Loop Fix
document.addEventListener("DOMContentLoaded", function() {
    const video = document.getElementById("bg-video");

    if (video) {
        let loopCutoff = null;

        // Figure out the real loop point once we know the video's actual length,
        // instead of a hardcoded number that breaks if the video file changes.
        video.addEventListener("loadedmetadata", function() {
            loopCutoff = Math.max(this.duration - 1.5, 1);
        });

        video.addEventListener("timeupdate", function() {
            if (loopCutoff && this.currentTime >= loopCutoff) {
                this.currentTime = 0;
                this.play();
            }
        });
    }
});

console.log("JavaScript is loaded and ready!");
// This is for Showing a loading state on the button when the form is submitted,
// plus a full-page overlay since SerpApi calls can take a few seconds.
const matchForm = document.getElementById('match-form');

if (matchForm) {
    matchForm.addEventListener('submit', function() {
        const btn = document.getElementById('submit-btn');
        btn.innerText = "Processing";
        btn.classList.add('loading');
        btn.disabled = true;

        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.classList.add('active');
    });
}

// Update the file upload label to show the selected file name
function updateFileName(input) {
    if (input.files.length > 0) {
        const fileName = input.files[0].name;
        document.getElementById('file-name').innerText = fileName;
    }
}

// Reveal job cards and other marked sections with a fade/slide-up animation
// as they scroll into view
function initScrollReveal() {
    const elements = document.querySelectorAll('.card-preview, .reveal');
    if (!elements.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });

    elements.forEach(el => observer.observe(el));
}

// Animate score badges counting up from 0 to their real value instead of
// just appearing instantly
function animateScoreCounts() {
    const badges = document.querySelectorAll('.count-up-score[data-target]');
    if (!badges.length) return;

    badges.forEach(badge => {
        const target = parseInt(badge.dataset.target, 10) || 0;
        const duration = 900;
        const steps = 40;
        const increment = target / steps;
        const stepTime = duration / steps;
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            badge.textContent = `${Math.round(current)}% Match`;
        }, stepTime);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initScrollReveal();
    animateScoreCounts();
});