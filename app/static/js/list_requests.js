document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('new-requests-list')) {
        initNewRequestsPage();
    }
});

function initNewRequestsPage() {
    const requestsList = document.getElementById('new-requests-list');

    // Initial load
    fetchNewRequests();

    // Set up periodic refresh every 3 seconds
    setInterval(fetchNewRequests, 3000);

    // Add empty state styling
    requestsList.classList.add('empty');
}

async function fetchNewRequests() {
    const list = document.getElementById('new-requests-list');

    try {
        // Show loading state
        list.innerHTML = '<p class="loading">Загрузка новых обращений...</p>';

        const response = await fetch('/api/requests/new');

        if (!response.ok) {
            throw new Error('Ошибка загрузки данных');
        }

        const requests = await response.json();
        renderRequests(requests);
    } catch (error) {
        console.error('Error:', error);
        showErrorMessage(list, error.message);
    }
}

function renderRequests(requests) {
    const list = document.getElementById('new-requests-list');
    list.classList.remove('empty');

    if (requests.length === 0) {
        list.innerHTML = '<p>Нет новых обращений</p>';
        list.classList.add('empty');
        return;
    }

    list.innerHTML = '';

    requests.forEach(request => {
        const card = document.createElement('div');
        card.className = 'request-card';
        card.innerHTML = `
            <div class="request-info">
                <p><span class="info-label">ФИО:</span> ${request.full_name}</p>
                <p><span class="info-label">Создано:</span> ${new Date(request.created_at).toLocaleString()}</p>
            </div>
            <form method="POST" action="/requests/respond/${request.id}" onsubmit="handleFormSubmit(this)">
                <button type="submit">Откликнуться</button>
            </form>
        `;
        list.appendChild(card);
    });
}

function handleFormSubmit(form) {
    const button = form.querySelector('button');
    if (button) {
        button.disabled = true;
        button.textContent = 'Обработка...';
    }
}

function showErrorMessage(container, message) {
    container.innerHTML = `
        <div class="error-message">
            Произошла ошибка при загрузке обращений: ${message}
        </div>
    `;
}

// Make functions available globally
window.fetchNewRequests = fetchNewRequests;
window.handleFormSubmit = handleFormSubmit;