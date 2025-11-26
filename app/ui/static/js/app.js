// API Base URL
const API_BASE = '/api';

// Global state
let stores = [];
let currentStoreId = null;

// Utility: Show toast notification
function showToast(title, message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-title">${title}</div>
        <div class="toast-message">${message}</div>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Utility: Format date
function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
}

// Utility: Extract ID from resource name
function extractId(resourceName) {
    const parts = resourceName.split('/');
    return parts[parts.length - 1];
}

// Tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.dataset.tab;

        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        // Load data for the tab
        if (tabName === 'stores') {
            loadStores();
        } else if (tabName === 'upload' || tabName === 'documents') {
            updateStoreSelects();
        } else if (tabName === 'search') {
            updateStoreSelects();
            updateSearchStoreSelect();
        }
    });
});

// Load stores
async function loadStores() {
    try {
        const response = await fetch(`${API_BASE}/stores`);
        if (!response.ok) {
            throw new Error(`Failed to load stores: ${response.statusText}`);
        }

        const data = await response.json();
        stores = data.fileSearchStores || [];

        renderStoresList();
        updateStoreSelects();

        showToast('Success', `Loaded ${stores.length} store(s)`, 'success');
    } catch (error) {
        console.error('Error loading stores:', error);
        showToast('Error', error.message, 'error');
    }
}

// Render stores list
function renderStoresList() {
    const container = document.getElementById('stores-list');

    if (stores.length === 0) {
        container.innerHTML = '<p>No stores found. Create one to get started.</p>';
        return;
    }

    container.innerHTML = stores.map(store => {
        const storeId = extractId(store.name);
        return `
            <div class="data-item">
                <div class="data-item-header">
                    <div class="data-item-title">
                        ${store.displayName || store.name}
                    </div>
                    <div class="data-item-actions">
                        <button class="btn btn-secondary btn-sm" onclick="viewStoreDetails('${storeId}')">
                            View Details
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="deleteStore('${storeId}')">
                            Delete
                        </button>
                    </div>
                </div>
                <div class="data-item-info">
                    <div><strong>ID:</strong> ${storeId}</div>
                    <div><strong>Active Documents:</strong> ${store.activeDocumentsCount}</div>
                    <div><strong>Pending Documents:</strong> ${store.pendingDocumentsCount}</div>
                    <div><strong>Failed Documents:</strong> ${store.failedDocumentsCount}</div>
                    <div><strong>Size:</strong> ${formatBytes(store.sizeBytes)}</div>
                    <div><strong>Created:</strong> ${formatDate(store.createTime)}</div>
                </div>
            </div>
        `;
    }).join('');
}

// Update store select dropdowns
function updateStoreSelects() {
    const uploadSelect = document.getElementById('upload-store-select');
    const documentsSelect = document.getElementById('documents-store-select');

    const options = stores.map(store => {
        const storeId = extractId(store.name);
        return `<option value="${storeId}">${store.displayName || store.name}</option>`;
    }).join('');

    uploadSelect.innerHTML = '<option value="">-- Select a Store --</option>' + options;
    documentsSelect.innerHTML = '<option value="">-- Select a Store --</option>' + options;

    // Also update search store select
    updateSearchStoreSelect();
}

// Create store
document.getElementById('create-store-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const displayName = document.getElementById('store-display-name').value;

    try {
        const response = await fetch(`${API_BASE}/stores`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ displayName: displayName || undefined }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create store');
        }

        const store = await response.json();
        showToast('Success', `Store created: ${store.name}`, 'success');

        // Reset form and reload stores
        document.getElementById('store-display-name').value = '';
        await loadStores();

    } catch (error) {
        console.error('Error creating store:', error);
        showToast('Error', error.message, 'error');
    }
});

// View store details
async function viewStoreDetails(storeId) {
    try {
        const response = await fetch(`${API_BASE}/stores/${storeId}`);
        if (!response.ok) {
            throw new Error('Failed to load store details');
        }

        const store = await response.json();
        alert(JSON.stringify(store, null, 2));
    } catch (error) {
        showToast('Error', error.message, 'error');
    }
}

// Delete store
async function deleteStore(storeId) {
    if (!confirm('Are you sure you want to delete this store? This will also delete all documents (force=true).')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/stores/${storeId}?force=true`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete store');
        }

        showToast('Success', 'Store deleted successfully', 'success');
        await loadStores();

    } catch (error) {
        console.error('Error deleting store:', error);
        showToast('Error', error.message, 'error');
    }
}

// Upload file
document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const storeId = document.getElementById('upload-store-select').value;
    if (!storeId) {
        showToast('Error', 'Please select a store', 'error');
        return;
    }

    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    if (!file) {
        showToast('Error', 'Please select a file', 'error');
        return;
    }

    const displayName = document.getElementById('file-display-name').value;
    const maxTokensPerChunk = document.getElementById('max-tokens-per-chunk').value;
    const maxOverlapTokens = document.getElementById('max-overlap-tokens').value;

    const formData = new FormData();
    formData.append('file', file);
    if (displayName) {
        formData.append('display_name', displayName);
    }
    formData.append('max_tokens_per_chunk', maxTokensPerChunk);
    formData.append('max_overlap_tokens', maxOverlapTokens);

    const progressContainer = document.getElementById('upload-progress');
    const progressFill = progressContainer.querySelector('.progress-fill');
    const progressText = progressContainer.querySelector('.progress-text');

    try {
        progressContainer.style.display = 'block';
        progressFill.style.width = '50%';
        progressText.textContent = 'Uploading...';

        const response = await fetch(`${API_BASE}/stores/${storeId}/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to upload file');
        }

        const operation = await response.json();
        progressFill.style.width = '100%';
        progressText.textContent = 'Upload complete!';

        showToast('Success', `File uploaded. Operation: ${operation.name}`, 'success');

        // Reset form
        fileInput.value = '';
        document.getElementById('file-display-name').value = '';

        setTimeout(() => {
            progressContainer.style.display = 'none';
            progressFill.style.width = '0%';
        }, 2000);

    } catch (error) {
        console.error('Error uploading file:', error);
        showToast('Error', error.message, 'error');
        progressContainer.style.display = 'none';
        progressFill.style.width = '0%';
    }
});

// Load documents
document.getElementById('documents-store-select').addEventListener('change', (e) => {
    currentStoreId = e.target.value;
    if (currentStoreId) {
        loadDocuments(currentStoreId);
    }
});

document.getElementById('refresh-documents').addEventListener('click', () => {
    if (currentStoreId) {
        loadDocuments(currentStoreId);
    } else {
        showToast('Info', 'Please select a store first', 'info');
    }
});

async function loadDocuments(storeId) {
    try {
        const response = await fetch(`${API_BASE}/stores/${storeId}/documents`);
        if (!response.ok) {
            throw new Error('Failed to load documents');
        }

        const data = await response.json();
        const documents = data.documents || [];

        renderDocumentsList(documents, storeId);
        showToast('Success', `Loaded ${documents.length} document(s)`, 'success');

    } catch (error) {
        console.error('Error loading documents:', error);
        showToast('Error', error.message, 'error');
    }
}

// Render documents list
function renderDocumentsList(documents, storeId) {
    const container = document.getElementById('documents-list');

    if (documents.length === 0) {
        container.innerHTML = '<p>No documents found in this store.</p>';
        return;
    }

    container.innerHTML = documents.map(doc => {
        const docId = extractId(doc.name);
        const stateBadge = getStateBadge(doc.state);

        return `
            <div class="data-item">
                <div class="data-item-header">
                    <div class="data-item-title">
                        ${doc.displayName || doc.name}
                        ${stateBadge}
                    </div>
                    <div class="data-item-actions">
                        <button class="btn btn-danger btn-sm" onclick="deleteDocument('${storeId}', '${docId}')">
                            Delete
                        </button>
                    </div>
                </div>
                <div class="data-item-info">
                    <div><strong>ID:</strong> ${docId}</div>
                    <div><strong>MIME Type:</strong> ${doc.mimeType || 'N/A'}</div>
                    <div><strong>Size:</strong> ${formatBytes(doc.sizeBytes)}</div>
                    <div><strong>Created:</strong> ${formatDate(doc.createTime)}</div>
                </div>
            </div>
        `;
    }).join('');
}

// Get state badge
function getStateBadge(state) {
    const badges = {
        'STATE_ACTIVE': '<span class="badge badge-success">Active</span>',
        'STATE_PENDING': '<span class="badge badge-pending">Pending</span>',
        'STATE_FAILED': '<span class="badge badge-failed">Failed</span>',
    };
    return badges[state] || '<span class="badge">Unknown</span>';
}

// Delete document
async function deleteDocument(storeId, documentId) {
    if (!confirm('Are you sure you want to delete this document?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/stores/${storeId}/documents/${documentId}?force=true`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete document');
        }

        showToast('Success', 'Document deleted successfully', 'success');
        await loadDocuments(storeId);

    } catch (error) {
        console.error('Error deleting document:', error);
        showToast('Error', error.message, 'error');
    }
}

// Format bytes
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Refresh stores button
document.getElementById('refresh-stores').addEventListener('click', loadStores);

// Load available models
async function loadModels() {
    const modelSelect = document.getElementById('search-model');

    try {
        const response = await fetch(`${API_BASE}/models`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const models = await response.json();

        if (!models || models.length === 0) {
            throw new Error('No models available');
        }

        // Clear existing options
        modelSelect.innerHTML = '';

        // Add models as options
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model.name;
            option.textContent = model.displayName || model.name;
            if (model.description) {
                option.title = model.description;
            }
            modelSelect.appendChild(option);
        });

        // Set default to first model, preferring 2.5 models that support file_search
        const defaultModel = models.find(m => m.name.includes('gemini-2.5-flash')) ||
                           models.find(m => m.name.includes('gemini-2.5-pro')) ||
                           models.find(m => m.name.includes('gemini-1.5-flash')) ||
                           models[0];
        if (defaultModel) {
            modelSelect.value = defaultModel.name;
        }

    } catch (error) {
        console.error('Error loading models:', error);
        // Fallback to hardcoded models if API fails (only file_search supported models)
        modelSelect.innerHTML = `
            <option value="gemini-2.5-flash">Gemini 2.5 Flash (Recommended)</option>
            <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
            <option value="gemini-1.5-flash-002">Gemini 1.5 Flash 002</option>
            <option value="gemini-1.5-pro-002">Gemini 1.5 Pro 002</option>
        `;
    }
}

// Search functionality
document.getElementById('search-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const searchStoreSelect = document.getElementById('search-store-select');
    const query = document.getElementById('search-query').value.trim();
    const model = document.getElementById('search-model').value;

    // Get selected store IDs
    const selectedOptions = Array.from(searchStoreSelect.selectedOptions);
    const storeIds = selectedOptions.map(opt => opt.value);

    if (storeIds.length === 0) {
        showToast('Error', 'Please select at least one store', 'error');
        return;
    }

    if (!query) {
        showToast('Error', 'Please enter a search query', 'error');
        return;
    }

    // Show loading
    document.getElementById('search-loading').style.display = 'flex';
    document.getElementById('search-results').style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                storeIds: storeIds,
                model: model
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Search failed');
        }

        const result = await response.json();
        console.log(result)
        // Display results
        document.getElementById('search-answer').textContent = result.answer;

        const sourcesDiv = document.getElementById('search-sources');
        if (result.sources && result.sources.length > 0) {
            sourcesDiv.innerHTML = '<ul>' +
                result.sources.map(source => `<li>${source}</li>`).join('') +
                '</ul>';
        } else {
            sourcesDiv.innerHTML = '<p>No sources found</p>';
        }

        document.getElementById('search-results').style.display = 'block';
        showToast('Success', 'Search completed', 'success');

    } catch (error) {
        console.error('Search error:', error);
        showToast('Error', error.message, 'error');
    } finally {
        document.getElementById('search-loading').style.display = 'none';
    }
});

// Update search store select when switching to search tab
function updateSearchStoreSelect() {
    const searchSelect = document.getElementById('search-store-select');

    const options = stores.map(store => {
        const storeId = extractId(store.name);
        const displayName = store.displayName || store.name;
        return `<option value="${storeId}">${displayName} (${store.activeDocumentsCount} docs)</option>`;
    }).join('');

    searchSelect.innerHTML = options;
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    loadStores();
    loadModels();
});
