document.addEventListener('DOMContentLoaded', () => {
    // View switching
    const sitesViewBtn = document.getElementById('sites-view-btn');
    const historyViewBtn = document.getElementById('history-view-btn');
    const sitesView = document.getElementById('sites-view');
    const historyView = document.getElementById('history-view');
    const historyTitle = document.getElementById('history-title');
    const backToSitesBtn = document.getElementById('back-to-sites-btn');

    // Modals
    const siteModal = document.getElementById('site-modal');
    const diffModal = document.getElementById('diff-modal');
    const closeButtons = document.querySelectorAll('.close-btn');

    // Forms and lists
    const siteForm = document.getElementById('site-form');
    const sitesList = document.getElementById('sites-list');
    const historyList = document.getElementById('history-list');

    // Buttons
    const addSiteBtn = document.getElementById('add-site-btn');

    const API_BASE_URL = '/api';
    let sitesCache = []; // Cache for sites data

    // --- View Switching ---
    sitesViewBtn.addEventListener('click', () => {
        sitesView.classList.remove('hidden');
        historyView.classList.add('hidden');
        sitesViewBtn.classList.add('active');
        historyViewBtn.classList.remove('active');
        loadSites();
    });

    historyViewBtn.addEventListener('click', () => {
        showHistoryView();
    });

    backToSitesBtn.addEventListener('click', () => {
        sitesView.classList.remove('hidden');
        historyView.classList.add('hidden');
        sitesViewBtn.classList.add('active');
        historyViewBtn.classList.remove('active');
    });

    // --- Modal Handling ---
    const showModal = (modal) => modal.classList.remove('hidden');
    const hideModal = (modal) => modal.classList.add('hidden');

    addSiteBtn.addEventListener('click', () => {
        siteForm.reset();
        document.getElementById('modal-title').textContent = 'Add New Site';
        document.getElementById('site-id').value = '';
        showModal(siteModal);
    });

    closeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            hideModal(siteModal);
            hideModal(diffModal);
        });
    });

    // --- API Calls ---
    const fetchAPI = async (endpoint, options = {}) => {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.description || 'API request failed');
        }
        return response.status === 204 ? null : response.json();
    };

    // --- Site Management ---
    const loadSites = async () => {
        try {
            const sites = await fetchAPI('/sites');
            sitesCache = sites; // Store sites in cache
            sitesList.innerHTML = sites.map(site => `
                <div class="card" data-id="${site.id}">
                    <h3>${site.name}</h3>
                    <p><strong>URL:</strong> <a href="${site.url}" target="_blank">${site.url}</a></p>
                    <p><strong>Selector:</strong> ${site.selector || 'N/A'}</p>
                    <p><strong>Receivers:</strong> ${site.receivers.join(', ') || 'N/A'}</p>
                    <p><strong>Playwright:</strong> ${site.use_playwright ? 'Yes' : 'No'}</p>
                    <div class="card-actions">
                        <button class="edit-btn">Edit</button>
                        <button class="delete-btn">Delete</button>
                        <button class="history-btn">History</button>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            sitesList.innerHTML = `<p class="error">${error.message}</p>`;
        }
    };

    siteForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const siteId = document.getElementById('site-id').value;
        const siteData = {
            name: document.getElementById('name').value,
            url: document.getElementById('url').value,
            selector: document.getElementById('selector').value,
            receivers: document.getElementById('receivers').value.split(',').map(r => r.trim()).filter(r => r),
            use_playwright: document.getElementById('use_playwright').checked,
        };

        try {
            if (siteId) {
                await fetchAPI(`/sites/${siteId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(siteData),
                });
            } else {
                await fetchAPI('/sites', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(siteData),
                });
            }
            hideModal(siteModal);
            loadSites();
        } catch (error) {
            alert(`Error saving site: ${error.message}`);
        }
    });

    sitesList.addEventListener('click', async (e) => {
        const card = e.target.closest('.card');
        if (!card) return;

        const siteId = card.dataset.id;

        if (e.target.classList.contains('edit-btn')) {
            const site = sitesCache.find(s => s.id === siteId);
            if (site) {
                document.getElementById('modal-title').textContent = 'Edit Site';
                document.getElementById('site-id').value = site.id;
                document.getElementById('name').value = site.name;
                document.getElementById('url').value = site.url;
                document.getElementById('selector').value = site.selector;
                document.getElementById('receivers').value = site.receivers.join(', ');
                document.getElementById('use_playwright').checked = site.use_playwright;
                showModal(siteModal);
            }
        }

        if (e.target.classList.contains('delete-btn')) {
            if (confirm('Are you sure you want to delete this site?')) {
                try {
                    await fetchAPI(`/sites/${siteId}`, { method: 'DELETE' });
                    loadSites();
                } catch (error) {
                    alert(`Error deleting site: ${error.message}`);
                }
            }
        }

        if (e.target.classList.contains('history-btn')) {
            const site = sitesCache.find(s => s.id === siteId);
            if (site) {
                showHistoryView(site);
            }
        }
    });

    // --- History Management ---
    const showHistoryView = (site = null) => {
        historyView.classList.remove('hidden');
        sitesView.classList.add('hidden');
        historyViewBtn.classList.add('active');
        sitesViewBtn.classList.remove('active');

        if (site) {
            historyTitle.textContent = `History for ${site.name}`;
            backToSitesBtn.classList.remove('hidden');
            loadHistory(site.url);
        } else {
            historyTitle.textContent = 'History';
            backToSitesBtn.classList.add('hidden');
            loadHistory();
        }
    };

    const loadHistory = async (url = null) => {
        try {
            const endpoint = url ? `/history?url=${encodeURIComponent(url)}` : '/history';
            const history = await fetchAPI(endpoint);
            historyList.innerHTML = history.length ? history.map(entry => {
                // Render the split diff for each entry
                const diffHtml = renderSplitDiffHtml(entry.diff_lines);
                return `
                    <div class="card">
                        <h3>${entry.url}</h3>
                        <p><strong>Timestamp:</strong> ${new Date(entry.timestamp).toLocaleString()}</p>
                        <p><strong>Selector:</strong> ${entry.selector || 'N/A'}</p>
                        <div class="split-diff-history">${diffHtml}</div>
                    </div>
                `;
            }).join('') : '<p>No history yet.</p>';
        } catch (error) {
            historyList.innerHTML = `<p class="error">${error.message}</p>`;
        }
    };

    // --- Split Diff Rendering for History List ---
    function renderSplitDiffHtml(diffLines) {
        // Parse the diff into old and new lines
        let oldLines = [];
        let newLines = [];
        let i = 0;
        while (i < diffLines.length) {
            const line = diffLines[i];
            if (line.startsWith('@@')) {
                i++;
                continue;
            }
            if (line.startsWith('-')) {
                oldLines.push({ text: line.slice(1), type: 'del' });
                i++;
            } else if (line.startsWith('+')) {
                newLines.push({ text: line.slice(1), type: 'add' });
                i++;
            } else if (line.startsWith(' ')) {
                oldLines.push({ text: line.slice(1), type: 'unchanged' });
                newLines.push({ text: line.slice(1), type: 'unchanged' });
                i++;
            } else {
                i++;
            }
        }
        let maxLen = Math.max(oldLines.length, newLines.length);
        while (oldLines.length < maxLen) oldLines.push({ text: '', type: 'empty' });
        while (newLines.length < maxLen) newLines.push({ text: '', type: 'empty' });
        // Build HTML for split diff
        let html = '<div class="split-diff-container" style="display:flex;gap:1rem;">';
        html += '<div class="diff-column"><div class="diff-header">Old</div>';
        for (let j = 0; j < maxLen; j++) {
            html += `<div class="diff-line diff-${oldLines[j].type || 'empty'}">${escapeHtml(oldLines[j].text)}</div>`;
        }
        html += '</div>';
        html += '<div class="diff-column"><div class="diff-header">New</div>';
        for (let j = 0; j < maxLen; j++) {
            html += `<div class="diff-line diff-${newLines[j].type || 'empty'}">${escapeHtml(newLines[j].text)}</div>`;
        }
        html += '</div></div>';
        return html;
    }
    function escapeHtml(text) {
        return text.replace(/[&<>"']/g, function (c) {
            return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
        });
    }

    // Initial load
    loadSites();
}); 