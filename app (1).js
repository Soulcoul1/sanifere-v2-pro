// ==================== CONFIGURATION ====================
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : 'https://votre-app.up.railway.app'; // Remplacer par votre URL Railway

// ==================== AUTH STATE ====================
class AuthManager {
    constructor() {
        this.token = localStorage.getItem('sanifere_token');
        this.user = JSON.parse(localStorage.getItem('sanifere_user') || 'null');
    }

    isAuthenticated() {
        return !!this.token;
    }

    getToken() {
        return this.token;
    }

    getUser() {
        return this.user;
    }

    setAuth(token, user) {
        this.token = token;
        this.user = user;
        localStorage.setItem('sanifere_token', token);
        localStorage.setItem('sanifere_user', JSON.stringify(user));
        this.updateUI();
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('sanifere_token');
        localStorage.removeItem('sanifere_user');
        this.updateUI();
        window.location.reload();
    }

    updateUI() {
        const authButtons = document.getElementById('authButtons');
        const userMenu = document.getElementById('userMenu');
        
        if (this.isAuthenticated()) {
            if (authButtons) authButtons.style.display = 'none';
            if (userMenu) {
                userMenu.style.display = 'flex';
                document.getElementById('userName').textContent = this.user.nom;
            }
        } else {
            if (authButtons) authButtons.style.display = 'flex';
            if (userMenu) userMenu.style.display = 'none';
        }
    }
}

const auth = new AuthManager();

// ==================== API HELPER ====================
async function apiCall(endpoint, options = {}) {
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };

    // Ajouter le token si authentifié
    if (auth.isAuthenticated()) {
        config.headers['Authorization'] = `Bearer ${auth.getToken()}`;
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Une erreur est survenue');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ==================== AUTH FUNCTIONS ====================
async function handleSignup() {
    const nom = document.getElementById('signupName').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const telephone = document.getElementById('signupPhone').value.trim();
    const mot_de_passe = document.getElementById('signupPassword').value;
    const code_parrainage = document.getElementById('signupReferral')?.value.trim();

    // Validation
    if (!nom || !email || !telephone || !mot_de_passe) {
        showNotification('Veuillez remplir tous les champs', 'error');
        return;
    }

    if (mot_de_passe.length < 6) {
        showNotification('Le mot de passe doit contenir au moins 6 caractères', 'error');
        return;
    }

    try {
        showLoading(true);
        
        const data = await apiCall('/api/auth/inscription', {
            method: 'POST',
            body: JSON.stringify({
                nom,
                email,
                telephone,
                mot_de_passe,
                code_parrainage: code_parrainage || null
            })
        });

        auth.setAuth(data.token, data.utilisateur);
        showNotification('Inscription réussie ! Bienvenue sur SANI-FÉRÉ 🎉', 'success');
        closeAuthModal();
        
        // Afficher le code de parrainage
        if (data.utilisateur.code_parrainage) {
            setTimeout(() => {
                showNotification(`Votre code de parrainage : ${data.utilisateur.code_parrainage}`, 'info');
            }, 2000);
        }

    } catch (error) {
        showNotification(error.message || 'Erreur lors de l\'inscription', 'error');
    } finally {
        showLoading(false);
    }
}

async function handleLogin() {
    const email = document.getElementById('loginEmail').value.trim();
    const mot_de_passe = document.getElementById('loginPassword').value;

    if (!email || !mot_de_passe) {
        showNotification('Veuillez remplir tous les champs', 'error');
        return;
    }

    try {
        showLoading(true);

        const data = await apiCall('/api/auth/connexion', {
            method: 'POST',
            body: JSON.stringify({ email, mot_de_passe })
        });

        auth.setAuth(data.token, data.utilisateur);
        showNotification(`Bon retour ${data.utilisateur.nom} ! 👋`, 'success');
        closeAuthModal();

    } catch (error) {
        showNotification(error.message || 'Email ou mot de passe incorrect', 'error');
    } finally {
        showLoading(false);
    }
}

// ==================== PRODUCTS FUNCTIONS ====================
async function loadProducts(filters = {}) {
    try {
        showLoading(true);

        const queryParams = new URLSearchParams({
            page: filters.page || 1,
            limite: filters.limite || 20,
            ...(filters.categorie && { categorie: filters.categorie }),
            ...(filters.ville && { ville: filters.ville }),
            ...(filters.prix_min && { prix_min: filters.prix_min }),
            ...(filters.prix_max && { prix_max: filters.prix_max }),
            ...(filters.recherche && { recherche: filters.recherche })
        });

        const data = await apiCall(`/api/produits?${queryParams}`);
        
        displayProducts(data.produits);
        updatePagination(data.page, data.pages_total);

    } catch (error) {
        showNotification('Erreur lors du chargement des produits', 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

function displayProducts(products) {
    const grid = document.getElementById('productsGrid');
    
    if (products.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 4rem;">
                <p style="font-size: 1.2rem; color: #666;">
                    Aucun produit trouvé 😔
                </p>
            </div>
        `;
        return;
    }

    grid.innerHTML = products.map(product => `
        <div class="product-card" onclick="viewProduct('${product.id}')">
            <div class="product-image">
                ${product.images && product.images.length > 0 
                    ? `<img src="${product.images[0]}" alt="${product.titre}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'400\\' height=\\'400\\'%3E%3Crect fill=\\'%23E8DCC4\\' width=\\'400\\' height=\\'400\\'/%3E%3Ctext x=\\'50%25\\' y=\\'50%25\\' text-anchor=\\'middle\\' dy=\\'.3em\\' fill=\\'%233D2817\\' font-size=\\'20\\'%3ESani-Féré%3C/text%3E%3C/svg%3E'">` 
                    : `<img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Crect fill='%23E8DCC4' width='400' height='400'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' dy='.3em' fill='%233D2817' font-size='20'%3E${product.titre}%3C/text%3E%3C/svg%3E">`
                }
                ${product.statut === 'vendu' ? '<div class="product-badge sold-badge">Vendu</div>' : ''}
                ${product.statut === 'réservé' ? '<div class="product-badge reserved-badge">Réservé</div>' : ''}
                ${product.negociable ? '<div class="product-badge negotiable-badge">Négociable</div>' : ''}
            </div>
            <div class="product-info">
                <div class="product-category">${product.categorie}</div>
                <h3 class="product-title">${product.titre}</h3>
                <p class="product-description">${truncateText(product.description, 100)}</p>
                <div class="product-meta">
                    <span>📍 ${product.ville}${product.quartier ? ', ' + product.quartier : ''}</span>
                    <span>👁️ ${product.vues || 0} vues</span>
                </div>
                <div class="product-footer">
                    <div class="product-price">
                        ${formatPrice(product.prix)} 
                        <span class="product-currency">FCFA</span>
                    </div>
                    <button class="favorite-btn" onclick="event.stopPropagation(); toggleFavorite('${product.id}')">
                        ${isFavorite(product.id) ? '❤️' : '♡'}
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

async function viewProduct(productId) {
    try {
        const product = await apiCall(`/api/produits/${productId}`);
        showProductModal(product);
    } catch (error) {
        showNotification('Erreur lors du chargement du produit', 'error');
    }
}

function showProductModal(product) {
    // TODO: Créer un modal de détail produit
    console.log('Product details:', product);
}

// ==================== CHATBOT FUNCTIONS ====================
let currentConversationId = null;

async function sendChatMessage(message) {
    if (!auth.isAuthenticated()) {
        showNotification('Connectez-vous pour utiliser le chatbot', 'info');
        openAuthModal('login');
        return;
    }

    try {
        const chatInput = document.getElementById('chatInput');
        const chatMessages = document.getElementById('chatMessages');

        // Afficher le message utilisateur
        appendChatMessage('user', message);
        chatInput.value = '';

        // Afficher indicateur de saisie
        const typingIndicator = appendChatMessage('assistant', '...');

        const data = await apiCall('/api/chatbot', {
            method: 'POST',
            body: JSON.stringify({
                message,
                conversation_id: currentConversationId
            })
        });

        // Retirer l'indicateur et afficher la réponse
        typingIndicator.remove();
        appendChatMessage('assistant', data.reponse);
        currentConversationId = data.conversation_id;

    } catch (error) {
        showNotification('Erreur chatbot', 'error');
        console.error(error);
    }
}

function appendChatMessage(role, content) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message chat-message-${role}`;
    messageDiv.innerHTML = `
        <div class="message-avatar">${role === 'user' ? '👤' : '🤖'}</div>
        <div class="message-content">${content}</div>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return messageDiv;
}

// ==================== FAVORITES ====================
function getFavorites() {
    return JSON.parse(localStorage.getItem('sanifere_favorites') || '[]');
}

function isFavorite(productId) {
    return getFavorites().includes(productId);
}

function toggleFavorite(productId) {
    let favorites = getFavorites();
    
    if (favorites.includes(productId)) {
        favorites = favorites.filter(id => id !== productId);
        showNotification('Retiré des favoris', 'info');
    } else {
        favorites.push(productId);
        showNotification('Ajouté aux favoris ❤️', 'success');
    }
    
    localStorage.setItem('sanifere_favorites', JSON.stringify(favorites));
    
    // Rafraîchir l'affichage si on est sur la page produits
    const productCard = event.target.closest('.product-card');
    if (productCard) {
        event.target.textContent = isFavorite(productId) ? '❤️' : '♡';
    }
}

// ==================== SEARCH & FILTERS ====================
let currentFilters = {};

function applyFilters() {
    const recherche = document.getElementById('searchInput')?.value;
    const categorie = document.getElementById('categoryFilter')?.value;
    const ville = document.getElementById('cityFilter')?.value;
    const prix_min = document.getElementById('priceMinFilter')?.value;
    const prix_max = document.getElementById('priceMaxFilter')?.value;

    currentFilters = {
        ...(recherche && { recherche }),
        ...(categorie && categorie !== 'all' && { categorie }),
        ...(ville && ville !== 'all' && { ville }),
        ...(prix_min && { prix_min: parseInt(prix_min) }),
        ...(prix_max && { prix_max: parseInt(prix_max) }),
        page: 1
    };

    loadProducts(currentFilters);
}

function filterByCategory(category) {
    currentFilters = { categorie: category, page: 1 };
    loadProducts(currentFilters);
    scrollToSection('featured');
}

// ==================== PAGINATION ====================
function updatePagination(currentPage, totalPages) {
    const paginationContainer = document.getElementById('pagination');
    if (!paginationContainer || totalPages <= 1) {
        if (paginationContainer) paginationContainer.innerHTML = '';
        return;
    }

    let html = '<div class="pagination-buttons">';

    // Previous
    if (currentPage > 1) {
        html += `<button class="btn-page" onclick="changePage(${currentPage - 1})">← Précédent</button>`;
    }

    // Pages
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            html += `<button class="btn-page ${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">${i}</button>`;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            html += '<span class="pagination-dots">...</span>';
        }
    }

    // Next
    if (currentPage < totalPages) {
        html += `<button class="btn-page" onclick="changePage(${currentPage + 1})">Suivant →</button>`;
    }

    html += '</div>';
    paginationContainer.innerHTML = html;
}

function changePage(page) {
    currentFilters.page = page;
    loadProducts(currentFilters);
    scrollToSection('featured');
}

// ==================== UTILITIES ====================
function formatPrice(price) {
    return new Intl.NumberFormat('fr-FR').format(price);
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function showNotification(message, type = 'info') {
    // Créer la notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">
                ${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}
            </span>
            <span class="notification-message">${message}</span>
        </div>
    `;

    // Ajouter au DOM
    document.body.appendChild(notification);

    // Animation d'entrée
    setTimeout(() => notification.classList.add('show'), 10);

    // Retirer après 4 secondes
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

function showLoading(show) {
    let loader = document.getElementById('globalLoader');
    
    if (show) {
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'globalLoader';
            loader.className = 'global-loader';
            loader.innerHTML = '<div class="loader-spinner"></div>';
            document.body.appendChild(loader);
        }
        loader.style.display = 'flex';
    } else {
        if (loader) {
            loader.style.display = 'none';
        }
    }
}

function scrollToSection(id) {
    const element = document.getElementById(id);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// ==================== STATS ====================
async function loadStats() {
    try {
        const data = await apiCall('/api/stats');
        updateStatsDisplay(data);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function updateStatsDisplay(stats) {
    const statsElements = {
        'stat-users': stats.utilisateurs,
        'stat-products': stats.produits_actifs,
        'stat-sold': stats.produits_vendus
    };

    Object.entries(statsElements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            animateNumber(element, 0, value, 2000);
        }
    });
}

function animateNumber(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= end) {
            element.textContent = Math.floor(end).toLocaleString('fr-FR');
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current).toLocaleString('fr-FR');
        }
    }, 16);
}

// ==================== INIT ====================
document.addEventListener('DOMContentLoaded', () => {
    // Charger les produits
    loadProducts();
    
    // Charger les stats
    loadStats();
    
    // Mettre à jour l'UI auth
    auth.updateUI();
    
    // Event listeners pour la recherche
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                applyFilters();
            }
        });
    }

    // Event listener pour le chatbot
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const message = chatInput.value.trim();
                if (message) {
                    sendChatMessage(message);
                }
            }
        });
    }
});

// ==================== EXPORT ====================
window.sanifere = {
    auth,
    apiCall,
    handleLogin,
    handleSignup,
    loadProducts,
    viewProduct,
    toggleFavorite,
    filterByCategory,
    applyFilters,
    sendChatMessage,
    showNotification
};
