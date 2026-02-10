document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('movieInput');
    const searchBtn = document.getElementById('searchBtn');
    const resultsSection = document.getElementById('resultsSection');
    const recommendationsGrid = document.getElementById('recommendationsGrid');
    const loading = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const suggestionsList = document.getElementById('suggestions');

    let debounceTimer;
    let isSearching = false;

    const handleSearch = async (query = null) => {
        clearTimeout(debounceTimer);
        isSearching = true; // Signal that a search is in progress
        console.log("Search initiated with query:", query);

        const title = query || input.value.trim();

        if (!title) {
            console.log("Empty title, aborting search");
            isSearching = false;
            return;
        }

        // Hide suggestions and update input
        suggestionsList.classList.add('hidden');
        input.value = title;

        // Reset UI
        resultsSection.classList.add('hidden');
        errorDiv.classList.add('hidden');
        loading.classList.remove('hidden');
        recommendationsGrid.innerHTML = '';

        console.log("Fetching recommendations for:", title);

        try {
            const res = await fetch(`/api/recommend?title=${encodeURIComponent(title)}`);
            const data = await res.json();

            if (!res.ok) throw new Error(data.error || "Failed to fetch recommendations");

            // Update header to show we are in search mode
            document.querySelector('#resultsSection h2').innerHTML = `Top Picks for <span style="color:var(--primary)">${data.movie}</span>`;

            renderCards(data.recommendations);
        } catch (err) {
            console.error("Search error:", err);
            errorDiv.textContent = err.message;
            errorDiv.classList.remove('hidden');
        } finally {
            loading.classList.add('hidden');
            suggestionsList.classList.add('hidden');
            // We do NOT reset isSearching here to prevent any race-condition suggestions from showing up.
            // isSearching will be reset when the user actively types again.
        }
    };

    const renderCards = (movies) => {
        if (!movies || movies.length === 0) {
            errorDiv.textContent = "No recommendations found.";
            errorDiv.classList.remove('hidden');
            return;
        }

        movies.forEach((movie, index) => {
            const card = document.createElement('div');
            card.className = 'card';
            card.style.animation = `fadeIn 0.5s ease-out ${index * 0.1}s forwards`;
            card.style.opacity = '0';

            // Handle potential variations in API response structure
            const title = movie.title || movie;
            const poster = movie.poster || '/static/no-poster.png';

            // Only show match badge if score exists (it won't for random movies)
            const matchBadge = movie.match ? `<div class="match-badge">${movie.match}% Match</div>` : '';

            card.innerHTML = `
                ${matchBadge}
                ${movie.poster ? `<img src="${poster}" class="movie-poster" loading="lazy" alt="${title}" style="cursor: pointer;">` : ''}
                <div class="card-content">
                    <h3>${title}</h3>
                    <div style="margin-top:5px; color:var(--text-secondary); font-size: 0.9em;">
                         Recommended
                    </div>
                </div>
            `;

            // Add click event for modal if ID exists
            if (movie.id) {
                const img = card.querySelector('.movie-poster');
                if (img) {
                    img.addEventListener('click', () => openMovieModal(movie.id));
                }
            }

            recommendationsGrid.appendChild(card);
        });

        resultsSection.classList.remove('hidden');
    };

    const openMovieModal = async (movieId) => {
        const modal = document.getElementById("movieModal");
        const body = document.getElementById("modalBody");

        modal.classList.remove("hidden");
        // Prevent background scrolling
        document.body.style.overflow = 'hidden';

        body.innerHTML = '<div style="text-align:center; padding:2rem;"><div class="spinner"></div><p>Loading details...</p></div>';

        try {
            const res = await fetch(`/api/movie/${movieId}`);
            const m = await res.json();

            if (m.error) throw new Error(m.error);

            body.innerHTML = `
                <div class="modal-header">
                    <img src="${m.poster || '/static/no-poster.png'}" class="modal-poster" alt="${m.title}">
                    <div class="modal-info">
                        <h2>${m.title}</h2>
                        <div class="modal-meta">
                            <span>⭐ ${m.rating ? m.rating.toFixed(1) : 'N/A'}</span> • 
                            <span>📅 ${m.release_date ? m.release_date.split('-')[0] : 'N/A'}</span> • 
                            <span>⏱ ${m.runtime || '?'} min</span>
                        </div>
                        <div class="modal-genres">
                            ${m.genres.map(g => `<span class="genre-tag">${g}</span>`).join('')}
                        </div>
                        <p class="modal-overview">${m.overview || 'No overview available.'}</p>
                        ${m.trailer ? `<a href="${m.trailer}" target="_blank" class="trailer-btn"><i class="fab fa-youtube"></i> Watch Trailer</a>` : ''}
                    </div>
                </div>
             `;
        } catch (err) {
            body.innerHTML = `<p style="color:red; text-align:center;">Failed to load details: ${err.message}</p>`;
        }
    };

    const closeModal = () => {
        document.getElementById("movieModal").classList.add("hidden");
        document.body.style.overflow = ''; // Restore scrolling
    };

    // Close modal on close button click
    document.querySelector('.close-btn').addEventListener('click', closeModal);

    // Close modal on click outside
    window.addEventListener('click', (e) => {
        const modal = document.getElementById("movieModal");
        if (e.target === modal) {
            closeModal();
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !document.getElementById("movieModal").classList.contains('hidden')) {
            closeModal();
        }
    });

    const fetchSuggestions = async (query) => {
        // 1. If a search has been committed, ignore.
        if (isSearching) return;

        // 2. If the input value has changed (e.g. selection), ignore.
        if (input.value.trim() !== query) return;

        if (!query || query.length < 2) {
            suggestionsList.classList.add('hidden');
            return;
        }

        try {
            const res = await fetch(`/api/suggestions?q=${encodeURIComponent(query)}`);
            const suggestions = await res.json();

            // 3. Final check: if state changed during fetch, ignore.
            if (isSearching || input.value.trim() !== query) return;

            suggestionsList.innerHTML = '';
            suggestions.forEach(title => {
                const div = document.createElement('div');
                div.className = 'suggestion-item';
                div.textContent = title;
                div.onclick = () => handleSearch(title);
                suggestionsList.appendChild(div);
            });

            if (suggestions.length > 0) {
                suggestionsList.classList.remove('hidden');
            } else {
                suggestionsList.classList.add('hidden');
            }
        } catch (err) {
            console.error("Suggestion error:", err);
        }
    };

    // Event Listeners
    searchBtn.addEventListener('click', () => {
        console.log("Button clicked");
        handleSearch();
    });

    input.addEventListener('keypress', e => {
        if (e.key === 'Enter') {
            handleSearch();
            suggestionsList.classList.add('hidden');
        }
    });

    input.addEventListener('input', e => {
        isSearching = false; // User is active again
        const query = e.target.value.trim();
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => fetchSuggestions(query), 300);
    });

    // ... (existing event listeners)

    document.addEventListener('click', e => {
        if (!e.target.closest('.search-box')) {
            suggestionsList.classList.add('hidden');
        }
    });

    // Load random movies on startup
    const loadRandomMovies = async () => {
        try {
            loading.classList.remove('hidden');
            const res = await fetch('/api/random');
            const data = await res.json();

            // If the user started searching while we were fetching random movies, abort!
            if (isSearching || input.value.trim().length > 0) return;

            if (data.length > 0) {
                document.querySelector('#resultsSection h2').textContent = "Movies You Might Like";
                renderCards(data);
            }
        } catch (err) {
            console.error("Error loading random movies:", err);
        } finally {
            // Only hide loading if we actually showed something or if we are not searching
            if (!isSearching) {
                loading.classList.add('hidden');
            }
        }
    };

    loadRandomMovies();
});
