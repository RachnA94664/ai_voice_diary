// diary/static/js/voice_record.js

let mediaRecorder;
let audioChunks = [];

document.addEventListener('DOMContentLoaded', function () {
    const recordBtn = document.getElementById('recordBtn');
    if (recordBtn) {
        recordBtn.addEventListener('click', function () {
            if (!mediaRecorder || mediaRecorder.state === "inactive") {
                navigator.mediaDevices.getUserMedia({ audio: true })
                    .then(stream => {
                        mediaRecorder = new MediaRecorder(stream);
                        audioChunks = [];
                        mediaRecorder.ondataavailable = e => { audioChunks.push(e.data); };
                        mediaRecorder.onstop = () => {
                            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                            const formData = new FormData();
                            formData.append('audio_file', audioBlob, 'recording.wav');
                            fetch('/api/diary/upload/', {
                                method: 'POST',
                                body: formData,
                                headers: {'X-CSRFToken': window.csrfToken}
                            })
                            .then(response => {
                                if (response.ok) {
                                    alert('Audio submitted successfully!');
                                } else {
                                    alert('Failed to submit. Try again.');
                                }
                            });
                        };
                        mediaRecorder.start();
                        setTimeout(() => mediaRecorder.stop(), 6000); // Record 6 sec
                    });
            }
        });
    }
});
