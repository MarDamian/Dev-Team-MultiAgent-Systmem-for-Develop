export const selectors = {
    chatBox: document.getElementById("chat-box"),
    messageInput: document.getElementById("message-input"),
    fileListDiv: document.getElementById("file-list"),
};

export function addMessage(content, type, options = {}) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", `${type}-message`);

    // Add agent-specific class if provided
    if (options.agent) {
        messageDiv.classList.add(`agent-${options.agent}`);

        // Create and prepend badge
        const badge = document.createElement("span");
        badge.classList.add("agent-badge", `badge-${options.agent}`);
        // Format agent name: "ui_ux" -> "UI UX"
        badge.textContent = options.agent.replace(/_/g, ' ').toUpperCase();
        messageDiv.appendChild(badge);
    }

    if (type === 'agent-status') {
        // For status messages, we might want to keep them simple or use the badge
        // If options.agent is passed, the badge is already added above.
        // We can make the content a bit smaller or italic
        const statusText = document.createElement("div");
        statusText.innerHTML = content;
        messageDiv.appendChild(statusText);

    } else if (options.isCode) {
        const codeContainer = document.createElement("div");
        codeContainer.className = "code-block-container";

        const header = document.createElement("div");
        header.className = "code-block-header";

        const lang = document.createElement("span");
        lang.textContent = options.lang;
        header.appendChild(lang);

        const copyButton = document.createElement("button");
        copyButton.className = "copy-button";
        copyButton.textContent = "Copiar";
        copyButton.addEventListener("click", () => {
            navigator.clipboard.writeText(content).then(() => {
                copyButton.textContent = "¡Copiado!";
                copyButton.classList.add("copied");
                setTimeout(() => {
                    copyButton.textContent = "Copiar";
                    copyButton.classList.remove("copied");
                }, 2000);
            });
        });
        header.appendChild(copyButton);
        codeContainer.appendChild(header);

        const pre = document.createElement("pre");
        const code = document.createElement("code");
        code.className = `language-${options.lang}`;
        code.textContent = content;
        pre.appendChild(code);
        codeContainer.appendChild(pre);
        messageDiv.appendChild(codeContainer);

    } else {
        const p = document.createElement("div");
        p.innerHTML = (type === 'bot') ? marked.parse(content) : content;
        messageDiv.appendChild(p);
    }
    selectors.chatBox.appendChild(messageDiv);
    selectors.chatBox.scrollTop = selectors.chatBox.scrollHeight;

    // Apply Prism syntax highlighting
    if (window.Prism) {
        messageDiv.querySelectorAll('pre code').forEach((block) => {
            window.Prism.highlightElement(block);
        });
    }
}

export function showLoading() {
    const sendButton = document.querySelector("#message-form button[type='submit']");
    if (sendButton) {
        sendButton.dataset.originalContent = sendButton.innerHTML;
        sendButton.innerHTML = '<div class="button-loader"></div>';
        sendButton.disabled = true;
    }
}

export function hideLoading() {
    const sendButton = document.querySelector("#message-form button[type='submit']");
    if (sendButton && sendButton.dataset.originalContent) {
        sendButton.innerHTML = sendButton.dataset.originalContent;
        sendButton.disabled = false;
    }
    // Remove old loading indicator if it exists
    const loadingDiv = document.getElementById("loading-indicator");
    if (loadingDiv) {
        loadingDiv.remove();
    }
}