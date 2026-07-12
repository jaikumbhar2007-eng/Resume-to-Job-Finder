console.log("JavaScript is loaded and ready!");

// This is for Showing a loading state on the button when the form is submitted
document.getElementById('match-form').addEventListener('submit', function() {
    const btn = document.getElementById('submit-btn');
    btn.innerText = "Processing";
    btn.classList.add('loading');
    btn.disabled = true;
});

// Update the file upload label to show the selected file name
function updateFileName(input) {
    if (input.files.length > 0) {
        const fileName = input.files[0].name;
        document.getElementById('file-name').innerText = fileName;
    }
}

// This section is for Revealing job cards with a fade/slide-up animation as they scroll into view
function initScrollReveal() {
    const cards = document.querySelectorAll('.card-preview');
    if (!cards.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });

    cards.forEach(card => observer.observe(card));
}

document.addEventListener('DOMContentLoaded', initScrollReveal);