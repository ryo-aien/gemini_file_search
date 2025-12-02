// API Base URL
const API_BASE = '/api';

// Global state
let stores = [];
let currentStoreId = null;
const defaultFileLabel = 'ファイルが選択されていません';

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

// Upload UI interactions
const fileInputElement = document.getElementById('file-input');
const fileDropZone = document.getElementById('file-drop-zone');
const fileSelectedName = document.getElementById('file-selected-name');

function updateSelectedFileName(file) {
    if (file) {
        fileSelectedName.textContent = file.name;
        fileDropZone.classList.add('has-file');
    } else {
        fileSelectedName.textContent = defaultFileLabel;
        fileDropZone.classList.remove('has-file');
    }
}

if (fileInputElement) {
    fileInputElement.addEventListener('change', (e) => {
        updateSelectedFileName(e.target.files[0]);
    });
}

['dragenter', 'dragover'].forEach(eventName => {
    fileDropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        fileDropZone.classList.add('dragging');
    });
});

['dragleave', 'drop'].forEach(eventName => {
    fileDropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        fileDropZone.classList.remove('dragging');
    });
});

fileDropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (!droppedFile) return;

    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(droppedFile);
    fileInputElement.files = dataTransfer.files;
    updateSelectedFileName(droppedFile);
});

// Load stores
async function loadStores() {
    try {
        const response = await fetch(`${API_BASE}/stores`);
        if (!response.ok) {
            throw new Error(`ストア一覧の取得に失敗しました: ${response.statusText}`);
        }

        const data = await response.json();
        stores = data.fileSearchStores || [];

        renderStoresList();
        updateStoreSelects();

        showToast('成功', `${stores.length} 件のストアを読み込みました`, 'success');
    } catch (error) {
        console.error('ストア取得エラー:', error);
        showToast('エラー', error.message, 'error');
    }
}

// Render stores list
function renderStoresList() {
    const container = document.getElementById('stores-list');

    if (stores.length === 0) {
        container.innerHTML = '<p>ストアがまだありません。まずは作成してください。</p>';
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
                            詳細を見る
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="deleteStore('${storeId}')">
                            削除
                        </button>
                    </div>
                </div>
                <div class="data-item-info">
                    <div><strong>ID:</strong> ${storeId}</div>
                    <div><strong>処理中ドキュメント:</strong> ${store.activeDocumentsCount}</div>
                    <div><strong>保留ドキュメント:</strong> ${store.pendingDocumentsCount}</div>
                    <div><strong>失敗ドキュメント:</strong> ${store.failedDocumentsCount}</div>
                    <div><strong>サイズ:</strong> ${formatBytes(store.sizeBytes)}</div>
                    <div><strong>作成日時:</strong> ${formatDate(store.createTime)}</div>
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

    uploadSelect.innerHTML = '<option value="">-- ストアを選択 --</option>' + options;
    documentsSelect.innerHTML = '<option value="">-- ストアを選択 --</option>' + options;

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
            throw new Error(error.detail || 'ストアの作成に失敗しました');
        }

        const store = await response.json();
        showToast('成功', `ストアを作成しました: ${store.name}`, 'success');

        // Reset form and reload stores
        document.getElementById('store-display-name').value = '';
        await loadStores();

    } catch (error) {
        console.error('ストア作成エラー:', error);
        showToast('エラー', error.message, 'error');
    }
});

// View store details
async function viewStoreDetails(storeId) {
    try {
        const response = await fetch(`${API_BASE}/stores/${storeId}`);
        if (!response.ok) {
            throw new Error('ストア詳細の取得に失敗しました');
        }

        const store = await response.json();
        openStoreModal(store);
    } catch (error) {
        showToast('エラー', error.message, 'error');
    }
}

// Delete store
async function deleteStore(storeId) {
    if (!confirm('このストアを削除しますか？関連ドキュメントも削除されます（force=true）。')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/stores/${storeId}?force=true`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'ストアの削除に失敗しました');
        }

        showToast('成功', 'ストアを削除しました', 'success');
        await loadStores();

    } catch (error) {
        console.error('ストア削除エラー:', error);
        showToast('エラー', error.message, 'error');
    }
}

// Upload file
document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const storeId = document.getElementById('upload-store-select').value;
    if (!storeId) {
        showToast('エラー', 'ストアを選択してください', 'error');
        return;
    }

    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    if (!file) {
        showToast('エラー', 'ファイルを選択してください', 'error');
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
        progressText.textContent = 'アップロード中...';

        const response = await fetch(`${API_BASE}/stores/${storeId}/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'ファイルのアップロードに失敗しました');
        }

        const operation = await response.json();
        progressFill.style.width = '100%';
        progressText.textContent = 'アップロード完了！';

        showToast('成功', `ファイルをアップロードしました。オペレーション: ${operation.name}`, 'success');

        // Reset form
        fileInput.value = '';
        document.getElementById('file-display-name').value = '';
        updateSelectedFileName(null);

        setTimeout(() => {
            progressContainer.style.display = 'none';
            progressFill.style.width = '0%';
        }, 2000);

    } catch (error) {
        console.error('アップロードエラー:', error);
        showToast('エラー', error.message, 'error');
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
        showToast('案内', '先にストアを選択してください', 'info');
    }
});

async function loadDocuments(storeId) {
    try {
        const response = await fetch(`${API_BASE}/stores/${storeId}/documents`);
        if (!response.ok) {
            throw new Error('ドキュメント一覧の取得に失敗しました');
        }

        const data = await response.json();
        const documents = data.documents || [];

        renderDocumentsList(documents, storeId);
        showToast('成功', `${documents.length} 件のドキュメントを読み込みました`, 'success');

    } catch (error) {
        console.error('ドキュメント取得エラー:', error);
        showToast('エラー', error.message, 'error');
    }
}

// Render documents list
function renderDocumentsList(documents, storeId) {
    const container = document.getElementById('documents-list');

    if (documents.length === 0) {
        container.innerHTML = '<p>このストアにドキュメントはありません。</p>';
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
                            削除
                        </button>
                    </div>
                </div>
                <div class="data-item-info">
                    <div><strong>ID:</strong> ${docId}</div>
                    <div><strong>MIMEタイプ:</strong> ${doc.mimeType || 'N/A'}</div>
                    <div><strong>サイズ:</strong> ${formatBytes(doc.sizeBytes)}</div>
                    <div><strong>作成日時:</strong> ${formatDate(doc.createTime)}</div>
                </div>
            </div>
        `;
    }).join('');
}

// Get state badge
function getStateBadge(state) {
    const badges = {
        'STATE_ACTIVE': '<span class="badge badge-success">完了</span>',
        'STATE_PENDING': '<span class="badge badge-pending">処理中</span>',
        'STATE_FAILED': '<span class="badge badge-failed">失敗</span>',
    };
    return badges[state] || '<span class="badge">不明</span>';
}

// Delete document
async function deleteDocument(storeId, documentId) {
    if (!confirm('このドキュメントを削除しますか？')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/stores/${storeId}/documents/${documentId}?force=true`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'ドキュメントの削除に失敗しました');
        }

        showToast('成功', 'ドキュメントを削除しました', 'success');
        await loadDocuments(storeId);

    } catch (error) {
        console.error('ドキュメント削除エラー:', error);
        showToast('エラー', error.message, 'error');
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

// Store modal helpers
const storeModal = document.getElementById('store-modal');
const storeModalBody = document.getElementById('store-modal-body');
const storeModalClose = document.getElementById('store-modal-close');

function openStoreModal(store) {
    const storeId = extractId(store.name);
    const detailTemplate = `
        <div class="detail-list">
            <div class="detail-row">
                <strong>ID</strong>
                <span>${storeId}</span>
            </div>
            <div class="detail-row">
                <strong>表示名</strong>
                <span>${store.displayName || '-'}</span>
            </div>
            <div class="detail-row">
                <strong>処理中ドキュメント</strong>
                <span>${store.activeDocumentsCount}</span>
            </div>
            <div class="detail-row">
                <strong>保留ドキュメント</strong>
                <span>${store.pendingDocumentsCount}</span>
            </div>
            <div class="detail-row">
                <strong>失敗ドキュメント</strong>
                <span>${store.failedDocumentsCount}</span>
            </div>
            <div class="detail-row">
                <strong>サイズ</strong>
                <span>${formatBytes(store.sizeBytes)}</span>
            </div>
            <div class="detail-row">
                <strong>作成日時</strong>
                <span>${formatDate(store.createTime)}</span>
            </div>
            <div class="detail-row">
                <strong>更新日時</strong>
                <span>${store.updateTime ? formatDate(store.updateTime) : '-'}</span>
            </div>
        </div>
    `;

    storeModalBody.innerHTML = detailTemplate;
    storeModal.style.display = 'flex';
}

function closeStoreModal() {
    storeModal.style.display = 'none';
}

storeModalClose.addEventListener('click', closeStoreModal);
storeModal.addEventListener('click', (e) => {
    if (e.target === storeModal) {
        closeStoreModal();
    }
});

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
            throw new Error('利用可能なモデルがありません');
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
        console.error('モデル読み込みエラー:', error);
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
        showToast('エラー', '検索対象のストアを一つ以上選択してください', 'error');
        return;
    }

    if (!query) {
        showToast('エラー', '検索クエリを入力してください', 'error');
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
            throw new Error(error.detail || '検索に失敗しました');
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
            sourcesDiv.innerHTML = '<p>参照元が見つかりませんでした</p>';
        }

        document.getElementById('search-results').style.display = 'block';
        showToast('成功', '検索が完了しました', 'success');

    } catch (error) {
        console.error('検索エラー:', error);
        showToast('エラー', error.message, 'error');
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
        return `<option value="${storeId}">${displayName} (${store.activeDocumentsCount} 件)</option>`;
    }).join('');

    searchSelect.innerHTML = options;
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    loadStores();
    loadModels();
});
