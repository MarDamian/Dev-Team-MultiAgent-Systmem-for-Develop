export const selectors = {
    chatBox: document.getElementById("chat-box"),
    messageInput: document.getElementById("message-input"),
    fileListDiv: document.getElementById("file-list"),
};

export function addMessage(content, type, options = {}) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", `${type}-message`);

    if (type === 'agent-status') {
        messageDiv.innerHTML = content;
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

        const renderedHtml = marked.parse(pre.outerHTML);
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = renderedHtml;

        codeContainer.replaceChild(tempDiv.firstChild, pre);
        messageDiv.appendChild(codeContainer);

    } else {
        const p = document.createElement("p");
        p.innerHTML = (type === 'bot') ? marked.parse(content) : content;
        messageDiv.appendChild(p);
    }
    selectors.chatBox.appendChild(messageDiv);
    selectors.chatBox.scrollTop = selectors.chatBox.scrollHeight;
}