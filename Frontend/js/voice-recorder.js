// Voice Recording Module for SAPCCA Chat Systems
// Usage: Import this in chat.html and classes.html

class VoiceRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.stream = null;
        this.startTime = null;
    }

    async startRecording() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(this.stream);
            this.audioChunks = [];
            this.startTime = Date.now();

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.start();
            return true;
        } catch (error) {
            console.error('Error accessing microphone:', error);
            return false;
        }
    }

    stopRecording() {
        return new Promise((resolve) => {
            if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
                resolve(null);
                return;
            }

            this.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                const duration = Math.floor((Date.now() - this.startTime) / 1000);
                
                // Convert to Base64
                const reader = new FileReader();
                reader.onloadend = () => {
                    const base64data = reader.result;
                    this.cleanup();
                    resolve({ data: base64data, duration });
                };
                reader.readAsDataURL(audioBlob);
            };

            this.mediaRecorder.stop();
        });
    }

    cancelRecording() {
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        this.cleanup();
    }

    cleanup() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        this.audioChunks = [];
    }
}

// Format duration for display
function formatVoiceDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Global voice recorder instance
window.voiceRecorder = new VoiceRecorder();
window.formatVoiceDuration = formatVoiceDuration;
