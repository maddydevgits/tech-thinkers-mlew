// Debug script to test translation functionality
function debugTranslation() {
    console.log('=== Translation Debug Info ===');
    
    if (window.translationManager) {
        console.log('Translation Manager:', window.translationManager);
        console.log('Current Language:', window.translationManager.currentLanguage);
        console.log('Supported Languages:', window.translationManager.supportedLanguages);
        console.log('Original Texts Count:', window.translationManager.originalTexts.size);
        console.log('Is Translating:', window.translationManager.isTranslating);
        
        // List all translatable elements
        const elements = document.querySelectorAll('[data-translate]');
        console.log('Found translatable elements:', elements.length);
        
        elements.forEach((el, index) => {
            const key = el.getAttribute('data-translate');
            const text = el.textContent.trim();
            console.log(`${index + 1}. Key: "${key}", Text: "${text.substring(0, 50)}..."`);
        });
    } else {
        console.error('Translation Manager not found!');
    }
    
    // Test API directly
    console.log('=== Testing Translation API ===');
    fetch('https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=te&dt=t&q=Hello World')
        .then(response => response.json())
        .then(data => {
            console.log('API Test Result:', data);
            if (data && data[0] && data[0][0]) {
                console.log('Translation works! "Hello World" ->', data[0][0][0]);
            }
        })
        .catch(error => {
            console.error('API Test Failed:', error);
        });
}

// Make debug function available globally
window.debugTranslation = debugTranslation;

// Auto-run debug when page loads
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        debugTranslation();
    }, 2000);
});
