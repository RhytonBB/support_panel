let currentRequestIds = new Set();

async function fetchNewRequests() {
    const list = document.getElementById('new-requests-list');

    try {
        const response = await fetch('/api/requests/new');
        if (!response.ok) throw new Error('Ошибка загрузки данных');

        const requests = await response.json();
        updateRequestList(requests);
    } catch (error) {
        console.error('Error:', error);
        showErrorMessage(list, error.message);
    }
}

function updateRequestList(requests) {
    const list = document.getElementById('new-requests-list');
    list.classList.remove('empty');

    const incomingIds = new Set(requests.map(req => req.id));

    // Удаляем карточки, которых больше нет
    list.querySelectorAll('.request-card').forEach(card => {
        const id = parseInt(card.dataset.id);
        if (!incomingIds.has(id)) {
            card.remove();
            currentRequestIds.delete(id);
        }
    });

    if (requests.length === 0) {
        if (list.children.length === 0) {
            list.innerHTML = '<p>Нет новых обращений</p>';
            list.classList.add('empty');
        }
        return;
    }

    // Добавляем новые карточки
    requests.forEach(request => {
        if (!currentRequestIds.has(request.id)) {
            const card = document.createElement('div');
            card.className = 'request-card';
            card.dataset.id = request.id;

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
            currentRequestIds.add(request.id);
        }
    });
}
