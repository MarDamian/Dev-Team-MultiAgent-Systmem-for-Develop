export function initVoiceHandler(messageInputId, micButtonId) {
    const messageInput = document.getElementById(messageInputId);
    const micButton = document.getElementById(micButtonId);

    if (!messageInput || !micButton) {
        console.error("VoiceHandler: Elements not found");
        return;
    }

    // Check for browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        console.warn("VoiceHandler: Web Speech API not supported in this browser.");
        micButton.style.display = 'none'; // Hide button if not supported
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false; // Stop after one sentence/phrase
    recognition.lang = 'es-ES'; // Set language to Spanish
    recognition.interimResults = true; // Show results as they are spoken

    let isRecording = false;

    micButton.addEventListener('click', () => {
        if (isRecording) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });

    recognition.onstart = () => {
        isRecording = true;
        micButton.classList.add('recording');
        console.log("VoiceHandler: Recording started");
    };

    recognition.onend = () => {
        isRecording = false;
        micButton.classList.remove('recording');
        console.log("VoiceHandler: Recording ended");
    };

    recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript;
            } else {
                interimTranscript += event.results[i][0].transcript;
            }
        }

        // Append to existing text or replace? 
        // Usually for a chat input, we might want to append if the user paused and started again.
        // But for simplicity, let's just set the value for now, or append if there is already text.

        // Strategy: We will append the final result to the current input value.
        // The interim result can be shown temporarily or we can just wait for final.
        // To avoid duplicating text if the user speaks multiple times, we need to be careful.
        // The simplest approach for "completing automatically" is to update the input value.

        // Let's try to be smart:
        // When 'onresult' fires, we get the *current session's* transcript.
        // If we just append to messageInput.value, we might duplicate if we do it on every 'interim' result.

        // Better approach:
        // Store the text that was in the input *before* this recording session started.
        // Update input = initialText + currentTranscript.

        // However, 'recognition.continuous = false' means it stops after a pause.
        // So we can just append the final result when it's ready.

        if (finalTranscript) {
            // Add a space if there is already text and it doesn't end with a space
            const currentText = messageInput.value;
            const prefix = (currentText && !currentText.endsWith(' ')) ? ' ' : '';
            messageInput.value = currentText + prefix + finalTranscript;
        }

        // Optional: Handle interim results if we want to show them "live" in the input
        // For now, let's stick to final results to be safe and clean.
    };

    recognition.onerror = (event) => {
        console.error("VoiceHandler: Error occurred in recognition: " + event.error);
        isRecording = false;
        micButton.classList.remove('recording');
    };
}
