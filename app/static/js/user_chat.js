const requestId = "{{ request_id }}";
const chatEl = document.getElementById("chat");

function renderMessages(messages) {
    chatEl.innerHTML = "";
    messages.forEach(msg => {
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${msg.sender === 'user' ? 'user' : 'admin'}`;

        if (msg.text) {
            const textElement = document.createElement("div");
            textElement.innerText = msg.text;
            messageDiv.appendChild(textElement);
        }

        if (msg.media && msg.media.length > 0) {
            const mediaContainer = document.createElement("div");
            mediaContainer.className = "media";
            msg.media.forEach(m => {
                if (m.endsWith('.mp4') || m.endsWith('.webm')) {
                    const video = document.createElement("video");
                    video.src = m;
                    video.controls = true;
                    mediaContainer.appendChild(video);
                } else {
                    const img = document.createElement("img");
                    img.src = m;
                    mediaContainer.appendChild(img);
                }
            });
            messageDiv.appendChild(mediaContainer);
        }

        const metaElement = document.createElement("div");
        metaElement.className = "message-meta";
        metaElement.innerText = msg.created_at;
        messageDiv.appendChild(metaElement);

        chatEl.appendChild(messageDiv);
    });

    // Прокрутка вниз к новым сообщениям
    chatEl.scrollTop = chatEl.scrollHeight;
}

async function fetchMessages() {
    try {
        const res = await fetch(`/api/messages/${requestId}`);
        if (!res.ok) throw new Error('Ошибка загрузки сообщений');
        const messages = await res.json();
        renderMessages(messages);
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

// Загружаем сообщения сразу и каждые 5 секунд
fetchMessages();
setInterval(fetchMessages, 5000);

// Обработчик отправки формы (если нужно добавить AJAX)
document.querySelector('.message-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
        const response = await fetch(e.target.action, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            e.target.reset();
            fetchMessages();
        }
    } catch (error) {
        console.error('Ошибка отправки:', error);
    }
});