// API Configuration
const API_BASE_URL = resolveApiBaseUrl();
const ML_PER_OZ = 29.5735;

// Global State
let currentUser = null;
let accessToken = null;
let refreshToken = null;
let drinkTypes = [];
let pendingCommunityDrinkId = null;

function resolveApiBaseUrl() {
    const configuredUrl = window.DRUNKVA_CONFIG?.API_BASE_URL;
    if (typeof configuredUrl === 'string' && configuredUrl.trim()) {
        return configuredUrl.trim().replace(/\/+$/, '');
    }

    const metaConfig = document.querySelector('meta[name="drunkva-api-base-url"]')?.content;
    if (typeof metaConfig === 'string' && metaConfig.trim()) {
        return metaConfig.trim().replace(/\/+$/, '');
    }

    // Served over http(s): default to same origin API.
    if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
        return window.location.origin.replace(/\/+$/, '');
    }

    // Local file preview fallback
    return 'http://localhost:8000';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadDrinkTypes();
    checkAuthStatus();
});

// Setup Event Listeners
function setupEventListeners() {
    // Tab Navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tabName = e.target.dataset.tab;
            if (tabName) switchTab(tabName, e.target);
        });
    });

    // Inner Tabs (Register/Login)
    document.querySelectorAll('.inner-tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tabName = e.target.dataset.innerTab;
            switchInnerTab(tabName, e.target);
        });
    });

    // Auth Forms
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    document.getElementById('loginForm').addEventListener('submit', handleLogin);

    // Drink Logging
    document.getElementById('logDrinkForm').addEventListener('submit', handleLogDrink);
    document.getElementById('drinkTypeSelect').addEventListener('change', updateDrinkPreview);
    document.getElementById('drinkTypeSelect').addEventListener('change', syncSearchInputWithDropdown);
    document.getElementById('quantity').addEventListener('input', updateDrinkPreview);
    document.getElementById('drinkSearchInput').addEventListener('input', handleDrinkSearchInput);
    document.getElementById('drinkSearchInput').addEventListener('focus', () => {
        renderDrinkSuggestions(document.getElementById('drinkSearchInput').value);
    });
    document.addEventListener('click', (e) => {
        const searchInput = document.getElementById('drinkSearchInput');
        const suggestionsEl = document.getElementById('drinkSuggestions');
        if (!searchInput.contains(e.target) && !suggestionsEl.contains(e.target)) {
            hideDrinkSuggestions();
        }
    });

    // History & Leaderboard
    document.getElementById('filterHistoryBtn').addEventListener('click', loadHistory);
    document.getElementById('loadLeaderboardBtn').addEventListener('click', loadLeaderboard);
    document.getElementById('loadCommunityBtn').addEventListener('click', loadCommunityFeed);
    document.getElementById('communityPostForm').addEventListener('submit', handleCommunityPostSubmit);
    document.getElementById('skipCommunityPostBtn').addEventListener('click', hideCommunityPrompt);

    // Logout
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);

    // Tab switching for leaderboard
    document.getElementById('leaderboard').addEventListener('click', (e) => {
        if (!currentUser) {
            showMessage('loginMessage', 'Please login first to see your rank', 'error');
        }
    });
}

// Tab Navigation
function switchTab(tabName, clickedButton = null) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.add('active');

    // Add active class to clicked button (if available)
    if (clickedButton) {
        clickedButton.classList.add('active');
    } else {
        const matchingTabButton = document.querySelector(`.tab-btn[data-tab="${tabName}"]`);
        if (matchingTabButton) {
            matchingTabButton.classList.add('active');
        }
    }

    // Load data for specific tabs
    if (tabName === 'history' && currentUser) {
        loadHistory();
    } else if (tabName === 'leaderboard') {
        loadLeaderboard();
    } else if (tabName === 'community') {
        loadCommunityFeed();
    } else if (tabName === 'profile' && currentUser) {
        loadProfile();
    }
}

function switchInnerTab(tabName, clickedButton = null) {
    // Hide all form sections
    document.querySelectorAll('.form-section').forEach(section => {
        section.classList.remove('active');
    });

    // Remove active class from all inner tab buttons
    document.querySelectorAll('.inner-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected form
    document.getElementById(tabName === 'register' ? 'registerForm' : 'loginForm').classList.add('active');

    // Add active class to clicked button (if available)
    if (clickedButton) {
        clickedButton.classList.add('active');
    } else {
        const matchingInnerTabButton = document.querySelector(`.inner-tab-btn[data-inner-tab="${tabName}"]`);
        if (matchingInnerTabButton) {
            matchingInnerTabButton.classList.add('active');
        }
    }

    // Clear messages
    document.getElementById('regMessage').innerHTML = '';
    document.getElementById('loginMessage').innerHTML = '';
}

// Authentication Functions
async function handleRegister(e) {
    e.preventDefault();

    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (response.ok) {
            accessToken = data.access_token;
            refreshToken = data.refresh_token;
            localStorage.setItem('accessToken', accessToken);
            await loadCurrentUser();
            showMessage('regMessage', 'Registration successful! Welcome!', 'success');
            setTimeout(() => switchTab('log-drink'), 1500);
        } else {
            showMessage('regMessage', formatApiError(data.detail, 'Registration failed'), 'error');
        }
    } catch (error) {
        showMessage('regMessage', 'Error: ' + error.message, 'error');
    }
}

async function handleLogin(e) {
    e.preventDefault();

    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            accessToken = data.access_token;
            refreshToken = data.refresh_token;
            localStorage.setItem('accessToken', accessToken);
            await loadCurrentUser();
            showMessage('loginMessage', 'Login successful!', 'success');
            setTimeout(() => switchTab('log-drink'), 1500);
        } else {
            showMessage('loginMessage', formatApiError(data.detail, 'Login failed'), 'error');
        }
    } catch (error) {
        showMessage('loginMessage', 'Error: ' + error.message, 'error');
    }
}

function handleLogout() {
    accessToken = null;
    refreshToken = null;
    currentUser = null;
    localStorage.removeItem('accessToken');
    updateUIAfterAuth();
    switchTab('auth');
    showMessage('loginMessage', 'Logged out successfully', 'success');
}

async function loadCurrentUser() {
    try {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });

        if (response.ok) {
            currentUser = await response.json();
            updateUIAfterAuth();
        }
    } catch (error) {
        console.error('Error loading current user:', error);
    }
}

function updateUIAfterAuth() {
    const userStatus = document.getElementById('userStatus');
    const logoutBtn = document.getElementById('logoutBtn');

    if (currentUser && accessToken) {
        userStatus.textContent = `👤 ${currentUser.username} (Rank: #${currentUser.rank})`;
        logoutBtn.style.display = 'block';
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.style.display = 'block';
        });
    } else {
        userStatus.textContent = 'Not logged in';
        logoutBtn.style.display = 'none';
    }
}

// Check Auth Status on Page Load
function checkAuthStatus() {
    const savedToken = localStorage.getItem('accessToken');
    if (savedToken) {
        accessToken = savedToken;
        loadCurrentUser();
    }
}

// Drink Functions
async function loadDrinkTypes() {
    try {
        const response = await fetch(`${API_BASE_URL}/drinks/types`);
        drinkTypes = await response.json();

        // Populate drink select dropdown
        const select = document.getElementById('drinkTypeSelect');
        select.innerHTML = '<option value="">Select a drink...</option>';

        drinkTypes.forEach(drink => {
            const option = document.createElement('option');
            option.value = String(drink.id);
            option.dataset.name = drink.name;
            option.textContent = `${drink.name} (${drink.abv_percent}% ABV)`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading drink types:', error);
    }
}

function updateDrinkPreview() {
    const quantityMl = parseFloat(document.getElementById('quantity').value) || 0;
    const previewEl = document.getElementById('drinkVolumePreview');
    previewEl.textContent = quantityMl > 0 ? formatMl(quantityMl) : '0';
}

function mlToOz(ml) {
    return ml / ML_PER_OZ;
}

function ozToMl(oz) {
    return oz * ML_PER_OZ;
}

function formatMl(value) {
    return value.toFixed(1);
}

async function handleLogDrink(e) {
    e.preventDefault();

    if (!currentUser) {
        showMessage('logDrinkMessage', 'Please login first', 'error');
        return;
    }

    const select = document.getElementById('drinkTypeSelect');
    const quantityMl = parseFloat(document.getElementById('quantity').value);
    const notes = document.getElementById('notes').value;

    if (!select.value) {
        showMessage('logDrinkMessage', 'Please select a drink', 'error');
        return;
    }

    try {
        const drinkTypeId = Number(select.value);

        const response = await fetch(`${API_BASE_URL}/drinks/log`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                drink_type_id: drinkTypeId,
                quantity_oz: mlToOz(quantityMl),
                notes: notes || null
            })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('logDrinkMessage', `Logged 1 drink (${formatMl(quantityMl)} ml).`, 'success');
            document.getElementById('logDrinkForm').reset();
            hideDrinkSuggestions();
            updateDrinkPreview();
            await loadCurrentUser();
            if (data.community_prompt && data.community_prompt.should_prompt) {
                showCommunityPrompt(data.community_prompt.drink_id);
            }
            setTimeout(() => loadHistory(), 1000);
        } else {
            showMessage('logDrinkMessage', data.detail || 'Failed to log drink', 'error');
        }
    } catch (error) {
        showMessage('logDrinkMessage', 'Error: ' + error.message, 'error');
    }
}

// History Functions
async function loadHistory() {
    if (!currentUser) {
        showMessage('loginMessage', 'Please login first', 'error');
        return;
    }

    const daysInput = document.getElementById('historyDays').value;
    const url = daysInput
        ? `${API_BASE_URL}/drinks/my-history?days=${daysInput}`
        : `${API_BASE_URL}/drinks/my-history`;

    try {
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });

        if (response.ok) {
            const data = await response.json();
            const historyList = document.getElementById('historyList');

            if (data.drinks.length === 0) {
                historyList.innerHTML = '<p class="loading">No drinks logged yet</p>';
                return;
            }

            historyList.innerHTML = data.drinks.map(drink => `
                <div class="list-item">
                    <div class="list-item-main">
                        <div class="list-item-title">${drink.drink_type?.name || 'Unknown drink'}</div>
                        <div class="list-item-subtitle">
                            ${new Date(drink.timestamp).toLocaleString()} • 
                            ${formatMl(ozToMl(drink.quantity_oz))} ml
                        </div>
                        ${drink.notes ? `<div class="list-item-subtitle">📝 ${drink.notes}</div>` : ''}
                    </div>
                    <div class="list-item-value">1<br><span style="font-size: 0.7em;">drink</span></div>
                </div>
            `).join('');
        }
    } catch (error) {
        document.getElementById('historyList').innerHTML = `<p class="loading error">Error loading history: ${error.message}</p>`;
    }
}

// Leaderboard Functions
async function loadLeaderboard() {
    const limit = document.getElementById('leaderboardLimit').value;

    try {
        const response = await fetch(`${API_BASE_URL}/leaderboard/global?limit=${limit}`);

        if (response.ok) {
            const data = await response.json();
            const leaderboardList = document.getElementById('leaderboardList');

            if (data.entries.length === 0) {
                leaderboardList.innerHTML = '<p class="loading">No entries yet</p>';
                return;
            }

            leaderboardList.innerHTML = data.entries.map((entry, index) => `
                <div class="leaderboard-row">
                    <div class="rank-badge">${index + 1}</div>
                    <div class="leaderboard-info">
                        <div class="leaderboard-name">${entry.username}</div>
                        <div class="leaderboard-stats">${entry.drink_count} drinks • ${formatMl(entry.total_volume_ml)} ml</div>
                    </div>
                    <div class="leaderboard-drinks">${entry.drink_count}<br><span style="font-size: 0.6em;">drinks</span><br><span style="font-size: 0.6em;">${formatMl(entry.total_volume_ml)} ml</span></div>
                </div>
            `).join('');
        }

        // Load user's rank
        if (currentUser && accessToken) {
            await loadUserRank();
        }
    } catch (error) {
        document.getElementById('leaderboardList').innerHTML = `<p class="loading">Error loading leaderboard: ${error.message}</p>`;
    }
}

async function loadUserRank() {
    try {
        const response = await fetch(`${API_BASE_URL}/leaderboard/my-rank`, {
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });

        if (response.ok) {
            const data = await response.json();
            const myRank = document.getElementById('myRank');

            let nearbyHTML = `
                <div class="rank-display">
                    🏆 Your Rank: <strong>#${data.rank}</strong>
                </div>
                <div class="info-box">
                    Drinks logged: ${data.drink_count} • Total volume: ${formatMl(data.total_volume_ml)} ml
                </div>
                <div style="margin-top: 20px;">
                    <h4>Nearby Rankings:</h4>
            `;

            data.nearby_users.forEach((user, index) => {
                const offset = index - Math.floor(data.nearby_users.length / 2);
                const isCurrent = offset === 0;
                nearbyHTML += `
                    <div class="leaderboard-row" style="background-color: ${isCurrent ? '#fff3cd' : '#f9f9f9'}">
                        <div class="rank-badge">${user.rank}</div>
                        <div class="leaderboard-info">
                            <div class="leaderboard-name">${user.username}${isCurrent ? ' ⭐' : ''}</div>
                            <div class="leaderboard-stats">${user.drink_count} drinks • ${formatMl(user.total_volume_ml)} ml</div>
                        </div>
                        <div class="leaderboard-drinks">${user.drink_count}<br><span style="font-size: 0.6em;">drinks</span><br><span style="font-size: 0.6em;">${formatMl(user.total_volume_ml)} ml</span></div>
                    </div>
                `;
            });

            nearbyHTML += '</div>';
            myRank.innerHTML = nearbyHTML;
        }
    } catch (error) {
        document.getElementById('myRank').innerHTML = `<p class="loading">Error loading rank: ${error.message}</p>`;
    }
}

// Profile Functions
async function loadProfile() {
    if (!currentUser) return;

    try {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });

        if (response.ok) {
            const user = await response.json();
            const profileInfo = document.getElementById('profileInfo');

            profileInfo.innerHTML = `
                <div class="stat-card">
                    <div class="stat-card-value">${formatMl(user.total_volume_ml)}</div>
                    <div class="stat-card-label">Total Volume (ml)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-value">${user.drink_count}</div>
                    <div class="stat-card-label">Drinks Logged</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-value">#${user.rank}</div>
                    <div class="stat-card-label">Leaderboard Rank</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-value">${user.username}</div>
                    <div class="stat-card-label">Username</div>
                </div>
            `;
        }
    } catch (error) {
        document.getElementById('profileInfo').innerHTML = `<p class="loading">Error loading profile: ${error.message}</p>`;
    }
}

// Community Functions
function showCommunityPrompt(drinkId) {
    pendingCommunityDrinkId = drinkId;
    document.getElementById('communityPromptCard').style.display = 'block';
    document.getElementById('communityPostText').value = '';
    document.getElementById('communityPostImage').value = '';
    document.getElementById('communityPostMessage').className = 'message';
    document.getElementById('communityPostMessage').textContent = '';
}

function hideCommunityPrompt() {
    pendingCommunityDrinkId = null;
    document.getElementById('communityPromptCard').style.display = 'none';
}

async function handleCommunityPostSubmit(e) {
    e.preventDefault();

    if (!currentUser) {
        showMessage('communityPostMessage', 'Please login first', 'error');
        return;
    }

    const text = document.getElementById('communityPostText').value.trim();
    const imageInput = document.getElementById('communityPostImage');
    const imageFile = imageInput.files[0];

    if (!text) {
        showMessage('communityPostMessage', 'Please add text for your post', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('text', text);
    if (pendingCommunityDrinkId) {
        formData.append('drink_id', String(pendingCommunityDrinkId));
    }
    if (imageFile) {
        formData.append('image', imageFile);
    }

    try {
        const response = await fetch(`${API_BASE_URL}/community/posts`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${accessToken}` },
            body: formData
        });

        const data = await response.json();
        if (response.ok) {
            showMessage('communityPostMessage', 'Posted to community!', 'success');
            hideCommunityPrompt();
            if (document.getElementById('community').classList.contains('active')) {
                await loadCommunityFeed();
            }
        } else {
            showMessage('communityPostMessage', formatApiError(data.detail, 'Failed to post to community'), 'error');
        }
    } catch (error) {
        showMessage('communityPostMessage', `Error: ${error.message}`, 'error');
    }
}

async function loadCommunityFeed() {
    const feedEl = document.getElementById('communityFeedList');
    feedEl.innerHTML = '<p class="loading">Loading community feed...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/community/feed?limit=25`);
        if (!response.ok) {
            feedEl.innerHTML = '<p class="loading error">Failed to load community feed</p>';
            return;
        }

        const data = await response.json();
        if (!data.posts || data.posts.length === 0) {
            feedEl.innerHTML = '<p class="loading">No community posts yet</p>';
            return;
        }

        feedEl.innerHTML = data.posts.map(post => `
            <div class="list-item" style="display:block;">
                <div class="list-item-title">${escapeHtml(post.username)}</div>
                <div class="list-item-subtitle">${new Date(post.created_at).toLocaleString()}</div>
                <div class="list-item-subtitle" style="color:#333; margin-top:8px;">${escapeHtml(post.text)}</div>
                ${post.drink_type_name ? `<div class="list-item-subtitle">🍺 ${escapeHtml(post.drink_type_name)} • ${formatMl(post.drink_volume_ml || 0)} ml</div>` : ''}
                ${post.image_url ? `<img class="community-post-image" src="${API_BASE_URL}${post.image_url}" alt="Community post image">` : ''}
            </div>
        `).join('');
    } catch (error) {
        feedEl.innerHTML = `<p class="loading error">Error loading feed: ${error.message}</p>`;
    }
}

// Utility Functions
function showMessage(elementId, message, type) {
    const messageEl = document.getElementById(elementId);
    messageEl.textContent = message;
    messageEl.className = `message show ${type}`;

    if (type !== 'error') {
        setTimeout(() => {
            messageEl.classList.remove('show');
        }, 5000);
    }
}

function formatApiError(detail, fallbackMessage) {
    if (!detail) return fallbackMessage;
    if (typeof detail === 'string') return detail;

    if (Array.isArray(detail)) {
        const messages = detail.map(item => {
            if (typeof item === 'string') return item;
            if (item && typeof item === 'object' && item.msg) return item.msg;
            return JSON.stringify(item);
        });
        return messages.filter(Boolean).join(' | ') || fallbackMessage;
    }

    if (typeof detail === 'object') {
        if (detail.msg) return detail.msg;
        return JSON.stringify(detail);
    }

    return fallbackMessage;
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function handleDrinkSearchInput(e) {
    const query = e.target.value.trim();
    renderDrinkSuggestions(query);
}

function renderDrinkSuggestions(query) {
    const suggestionsEl = document.getElementById('drinkSuggestions');
    const select = document.getElementById('drinkTypeSelect');
    const normalizedQuery = query.toLowerCase();

    if (!normalizedQuery) {
        suggestionsEl.innerHTML = '';
        hideDrinkSuggestions();
        return;
    }

    const matches = drinkTypes.filter(drink => drink.name.toLowerCase().includes(normalizedQuery)).slice(0, 8);

    if (matches.length === 0) {
        suggestionsEl.innerHTML = '';
        hideDrinkSuggestions();
        return;
    }

    suggestionsEl.innerHTML = matches.map(drink => `
        <button type="button" class="suggestion-item" data-drink-id="${drink.id}">
            ${drink.name} (${drink.abv_percent}% ABV)
        </button>
    `).join('');

    suggestionsEl.querySelectorAll('.suggestion-item').forEach(item => {
        item.addEventListener('click', () => {
            const drinkId = item.dataset.drinkId;
            select.value = drinkId;
            syncSearchInputWithDropdown();
            hideDrinkSuggestions();
        });
    });

    suggestionsEl.classList.add('active');
}

function hideDrinkSuggestions() {
    const suggestionsEl = document.getElementById('drinkSuggestions');
    suggestionsEl.classList.remove('active');
}

function syncSearchInputWithDropdown() {
    const select = document.getElementById('drinkTypeSelect');
    const searchInput = document.getElementById('drinkSearchInput');
    const selectedOption = select.options[select.selectedIndex];

    if (selectedOption && selectedOption.value) {
        searchInput.value = selectedOption.dataset.name || selectedOption.textContent;
    }
}
