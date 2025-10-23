// Translation functionality using Google Translate API
class TranslationManager {
    constructor() {
        this.currentLanguage = 'en';
        this.supportedLanguages = {
            'en': 'English',
            'hi': 'Hindi', 
            'te': 'Telugu',
            'ta': 'Tamil'
        };
        this.originalTexts = new Map();
        this.isTranslating = false;
        this.init();
    }

    init() {
        console.log('Initializing TranslationManager...');
        
        // Load saved language preference
        const savedLang = localStorage.getItem('selectedLanguage');
        if (savedLang && this.supportedLanguages[savedLang]) {
            this.currentLanguage = savedLang;
            console.log('Loaded saved language:', savedLang);
        }
        
        // Set up language selector
        this.setupLanguageSelector();
        
        // Store original texts
        this.storeOriginalTexts();
        
        console.log('Found translatable elements:', this.originalTexts.size);
        
        // Apply saved language on page load
        if (this.currentLanguage !== 'en') {
            setTimeout(() => {
                this.changeLanguage(this.currentLanguage);
            }, 100);
        }
    }

    setupLanguageSelector() {
        // Set up language selector dropdown
        const languageSelector = document.getElementById('language-selector');
        if (languageSelector) {
            console.log('Found language selector, setting up...');
            // Set the current language
            languageSelector.value = this.currentLanguage;
            
            languageSelector.addEventListener('change', (e) => {
                console.log('Language selector changed to:', e.target.value);
                this.changeLanguage(e.target.value);
            });
        } else {
            console.error('Language selector not found! Make sure the element with id="language-selector" exists.');
        }
    }

    storeOriginalTexts() {
        // Store original text content of translatable elements
        const translatableElements = document.querySelectorAll('[data-translate]');
        console.log('Found', translatableElements.length, 'translatable elements');
        
        translatableElements.forEach(element => {
            const key = element.getAttribute('data-translate');
            const text = element.textContent.trim();
            if (text && !this.originalTexts.has(key)) {
                this.originalTexts.set(key, text);
                console.log('Stored text for key:', key, '=', text.substring(0, 50) + '...');
            }
        });
    }

    async changeLanguage(languageCode) {
        if (!this.supportedLanguages[languageCode]) {
            console.error('Unsupported language:', languageCode);
            return;
        }

        if (this.isTranslating) {
            console.log('Translation already in progress...');
            return;
        }

        console.log(`Changing language to: ${languageCode}`);
        this.currentLanguage = languageCode;
        localStorage.setItem('selectedLanguage', languageCode);

        // Show loading indicator
        this.showLoadingIndicator();

        if (languageCode === 'en') {
            // Restore original English text
            this.restoreOriginalTexts();
            this.hideLoadingIndicator();
        } else {
            // Translate to target language
            await this.translatePage(languageCode);
            this.hideLoadingIndicator();
        }
    }

    showLoadingIndicator() {
        // Create or show loading indicator
        let indicator = document.getElementById('translation-loading');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'translation-loading';
            indicator.innerHTML = `
                <div style="position: fixed; top: 20px; right: 20px; background: #10b981; color: white; padding: 10px 20px; border-radius: 5px; z-index: 9999; font-size: 14px;">
                    <i class="fas fa-spinner fa-spin mr-2"></i>Translating...
                </div>
            `;
            document.body.appendChild(indicator);
        } else {
            indicator.style.display = 'block';
        }
    }

    hideLoadingIndicator() {
        const indicator = document.getElementById('translation-loading');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }

    restoreOriginalTexts() {
        // Restore original English text
        const translatableElements = document.querySelectorAll('[data-translate]');
        translatableElements.forEach(element => {
            const key = element.getAttribute('data-translate');
            const originalText = this.originalTexts.get(key);
            if (originalText) {
                element.textContent = originalText;
            }
        });
    }

    async translatePage(targetLanguage) {
        this.isTranslating = true;
        console.log(`Translating page to ${targetLanguage}...`);
        
        // First, store all current texts (including dynamic content)
        this.storeOriginalTexts();
        
        const translatableElements = document.querySelectorAll('[data-translate]');
        const totalElements = translatableElements.length;
        let translatedCount = 0;
        
        console.log(`Found ${totalElements} elements to translate`);
        
        // Process elements in batches to avoid overwhelming the API
        const batchSize = 3; // Reduced batch size for better reliability
        for (let i = 0; i < translatableElements.length; i += batchSize) {
            const batch = Array.from(translatableElements).slice(i, i + batchSize);
            
            const promises = batch.map(async (element) => {
                const key = element.getAttribute('data-translate');
                let textToTranslate = element.textContent.trim();
                
                // For dynamic content, use the current text if not in originalTexts
                if (!this.originalTexts.has(key) && textToTranslate) {
                    this.originalTexts.set(key, textToTranslate);
                } else if (this.originalTexts.has(key)) {
                    textToTranslate = this.originalTexts.get(key);
                }
                
                if (textToTranslate && textToTranslate.trim()) {
                    try {
                        const translatedText = await this.translateText(textToTranslate, targetLanguage);
                        element.textContent = translatedText;
                        translatedCount++;
                        console.log(`Translated ${translatedCount}/${totalElements}: ${textToTranslate.substring(0, 30)}...`);
                    } catch (error) {
                        console.error('Translation error for:', textToTranslate, error);
                    }
                }
            });
            
            await Promise.all(promises);
            
            // Small delay between batches to be respectful to the API
            if (i + batchSize < translatableElements.length) {
                await new Promise(resolve => setTimeout(resolve, 200));
            }
        }
        
        this.isTranslating = false;
        console.log(`Translation complete! Translated ${translatedCount}/${totalElements} elements.`);
    }

    async translateText(text, targetLanguage) {
        try {
            // Use Google Translate API with proper error handling
            const response = await fetch(`https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=${targetLanguage}&dt=t&q=${encodeURIComponent(text)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data && data[0] && data[0][0] && data[0][0][0]) {
                return data[0][0][0];
            }
            
            return text; // Return original text if translation fails
        } catch (error) {
            console.error('Translation API error:', error);
            return text; // Return original text on error
        }
    }

    // Method to add new translatable content dynamically
    addTranslatableElement(element, key, text) {
        element.setAttribute('data-translate', key);
        element.textContent = text;
        this.originalTexts.set(key, text);
        
        // Translate if not in English
        if (this.currentLanguage !== 'en') {
            this.translateText(text, this.currentLanguage).then(translated => {
                element.textContent = translated;
            });
        }
    }

    // Method to re-translate all content (useful for dynamic pages)
    async retranslateAll() {
        if (this.currentLanguage !== 'en') {
            await this.translatePage(this.currentLanguage);
        }
    }

    // Method to handle dynamic content updates
    handleDynamicContent() {
        // Re-store texts for any new elements
        this.storeOriginalTexts();
        
        // Re-translate if needed
        if (this.currentLanguage !== 'en') {
            setTimeout(() => {
                this.retranslateAll();
            }, 100);
        }
    }
}

// Initialize translation manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.translationManager = new TranslationManager();
});

// Utility function to translate specific text
function translateText(text, targetLanguage = null) {
    if (!targetLanguage) {
        targetLanguage = window.translationManager?.currentLanguage || 'en';
    }
    
    if (targetLanguage === 'en') {
        return Promise.resolve(text);
    }
    
    return window.translationManager?.translateText(text, targetLanguage) || Promise.resolve(text);
}

// Utility function to add translatable content
function addTranslatableContent(element, key, text) {
    window.translationManager?.addTranslatableElement(element, key, text);
}

// Utility function to handle dynamic content updates
function handleDynamicContentUpdate() {
    window.translationManager?.handleDynamicContent();
}

// Watch for dynamic content changes
if (window.MutationObserver) {
    const observer = new MutationObserver((mutations) => {
        let shouldRetranslate = false;
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.querySelector && node.querySelector('[data-translate]')) {
                        shouldRetranslate = true;
                    }
                });
            }
        });
        
        if (shouldRetranslate) {
            setTimeout(() => {
                handleDynamicContentUpdate();
            }, 500);
        }
    });
    
    // Start observing when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
}
