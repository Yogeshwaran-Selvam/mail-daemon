// dropbox/static/dropbox/js/main.js

// Feature 1: The Interactive Category Filter
function filterCategory(selectedCategory) {
    // 1. Update Button Styles
    const buttons = document.querySelectorAll('.filter-btn');
    buttons.forEach(btn => {
        if (btn.innerText.includes(selectedCategory) || (selectedCategory === 'All' && btn.innerText.includes('All'))) {
            btn.classList.add('bg-brand-600', 'text-white', 'border-brand-500', 'shadow-lg', 'shadow-brand-500/20');
            btn.classList.remove('bg-slate-800', 'text-slate-300', 'hover:bg-slate-700', 'border-slate-700');
        } else {
            btn.classList.remove('bg-brand-600', 'text-white', 'border-brand-500', 'shadow-lg', 'shadow-brand-500/20');
            btn.classList.add('bg-slate-800', 'text-slate-300', 'hover:bg-slate-700', 'border-slate-700');
        }
    });

    // 2. Filter the Cards
    const cards = document.querySelectorAll('.email-item-wrapper');
    let visibleCount = 0;
    
    cards.forEach(card => {
        const cardCategory = card.getAttribute('data-category');
        if (selectedCategory === 'All' || cardCategory === selectedCategory) {
            card.style.display = 'block';
            card.classList.remove('animate-fade-in');
            void card.offsetWidth; // trigger reflow
            card.classList.add('animate-fade-in');
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });

    // 3. Handle Empty Filter States
    const emptyStateDiv = document.getElementById('filter-empty-state');
    const emptyStateText = document.getElementById('filter-empty-text');
    
    if (visibleCount === 0 && cards.length > 0) {
        emptyStateText.innerText = `You have no unarchived emails categorized as "${selectedCategory}".`;
        emptyStateDiv.classList.remove('hidden');
    } else {
        emptyStateDiv.classList.add('hidden');
    }
}

// Feature 2: Background Fetching
function runFetcher() {
    let btn = document.getElementById('fetchBtn');
    let icon = btn.querySelector('i');
    let text = btn.querySelector('span');
    
    btn.classList.add('opacity-75', 'cursor-not-allowed', 'bg-brand-800');
    btn.classList.remove('hover:bg-brand-500', 'bg-brand-600');
    icon.classList.remove('fa-bolt');
    icon.classList.add('fa-spinner', 'fa-spin');
    if (text) text.innerText = 'Initializing...';
    btn.disabled = true;

    fetch('/api/run-fetcher/')
        .then(response => response.json())
        .then(data => {
            if (text) text.innerText = 'Reloading...';
            setTimeout(() => location.reload(), 500); 
        })
        .catch(error => {
            console.error("Error fetching:", error);
            if (text) text.innerText = 'Failed';
            icon.classList.remove('fa-spinner', 'fa-spin');
            icon.classList.add('fa-triangle-exclamation');
            btn.classList.add('bg-red-600');
        });
}