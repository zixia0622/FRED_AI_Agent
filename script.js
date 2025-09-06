document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const historyList = document.getElementById('history-list');
    let currentChat = [];

    // 发送消息函数
    const sendMessage = async () => {
        const message = userInput.value.trim();
        if (!message) return;

        // 添加用户消息到界面
        addMessage(message, 'user-message');
        currentChat.push({ role: 'user', content: message });
        userInput.value = '';

        try {
            // 发送请求到本地 Agent 服务
            const response = await fetch('http://localhost:5000/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: message
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            // 添加 AI 回复到界面
            addMessage(data, 'ai-message');
            currentChat.push({ role: 'ai', content: data });
            // 更新历史记录
            updateHistory(message);
        } catch (error) {
            console.error('Error:', error);
            addMessage('请求失败，请稍后重试。', 'ai-message');
        }
    };

    // 更新历史记录
    const updateHistory = (message) => {
        const historyItem = document.createElement('div');
        historyItem.classList.add('history-item');
        historyItem.textContent = message.substring(0, 30) + (message.length > 30 ? '...' : '');
        historyItem.addEventListener('click', () => {
            // 点击历史记录时加载对应聊天
            loadChat(currentChat);
        });
        historyList.appendChild(historyItem);
    };

    // 加载聊天记录
    const loadChat = (chat) => {
        chatMessages.innerHTML = '';
        chat.forEach(item => {
            addMessage(item.content, `${item.role}-message`);
        });
    };

    // 添加消息到聊天界面
    const addMessage = (text, className) => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', className);
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    // 绑定发送按钮点击事件
    sendButton.addEventListener('click', sendMessage);

    // 绑定回车键发送
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});