document.addEventListener('DOMContentLoaded', () => {
    const chatWindow = document.getElementById('chat-window');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const startChatBtn = document.getElementById('start-chat-btn');
    const userNameInput = document.getElementById('user-name');
    const userEmailInput = document.getElementById('user-email');

    let userData = { name: null, email: null };

    startChatBtn.addEventListener('click', () => {
        const name = userNameInput.value.trim();
        const email = userEmailInput.value.trim();

        if (!name || !email) {
            alert("Please enter both Name and Email.");
            return;
        }

        userData = { name, email };

        // Disable form
        userNameInput.disabled = true;
        userEmailInput.disabled = true;
        startChatBtn.disabled = true;
        startChatBtn.textContent = "Connected";
        startChatBtn.style.background = "#10b981";

        // Enable chat
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();

        addMessage(`Welcome, ${name}! Let's get started.`, 'bot');

        // Trigger first interaction
        sendMessage("START_SESSION", true);
    });

    function addMessage(text, sender) {
        const div = document.createElement('div');
        div.classList.add('message', sender === 'user' ? 'user-message' : 'bot-message');
        if (sender === 'bot') {
            div.innerHTML = marked.parse(text);
        } else {
            div.textContent = text;
        }
        chatWindow.appendChild(div);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    async function sendMessage(textOverride = null, hidden = false) {
        const text = textOverride || userInput.value.trim();
        if (!text) return;

        if (!hidden) {
            addMessage(text, 'user');
            userInput.value = '';
        }

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: text,
                    user_data: userData
                })
            });

            const data = await response.json();
            if (data.response) {
                addMessage(data.response, 'bot');
            }
        } catch (error) {
            console.error('Error:', error);
            addMessage("Sorry, I'm having trouble connecting to the server.", 'bot');
        }
    }

    sendBtn.addEventListener('click', () => sendMessage());
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});
