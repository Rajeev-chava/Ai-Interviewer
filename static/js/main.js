/**
 * AI Interviewer - Main JavaScript File
 * Contains common functions used across the application
 */

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg ${
        type === 'success' ? 'bg-green-500' : 
        type === 'error' ? 'bg-red-500' : 
        'bg-blue-500'
    } text-white z-50`;
    notification.innerHTML = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('opacity-0', 'transition-opacity', 'duration-500');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 500);
    }, 3000);
}

// Format time (seconds to MM:SS)
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
    const secs = Math.floor(seconds % 60).toString().padStart(2, '0');
    return `${minutes}:${secs}`;
}

// Check browser compatibility for recording
function checkRecordingCompatibility() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showNotification('Your browser does not support audio recording. Please use a modern browser like Chrome, Firefox, or Edge.', 'error');
        return false;
    }
    return true;
}

// Check if the browser supports the Web Speech API
function checkSpeechRecognitionSupport() {
    return 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window;
}

// Create a blob URL from a blob object
function createBlobURL(blob) {
    return URL.createObjectURL(blob);
}

// Download a blob as a file
function downloadBlob(blob, filename) {
    const url = createBlobURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Truncate text to a specific length
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Debounce function to limit how often a function can be called
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showNotification,
        formatTime,
        checkRecordingCompatibility,
        checkSpeechRecognitionSupport,
        createBlobURL,
        downloadBlob,
        truncateText,
        debounce
    };
}
