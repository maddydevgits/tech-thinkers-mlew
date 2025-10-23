// Enhanced file upload functionality
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('image');
    const uploadArea = document.querySelector('.border-dashed');
    
    if (fileInput && uploadArea) {
        // Handle file selection
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                displayFilePreview(file);
            }
        });
        
        // Handle drag and drop
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('border-green-400', 'bg-green-50');
        });
        
        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('border-green-400', 'bg-green-50');
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('border-green-400', 'bg-green-50');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (isValidImageFile(file)) {
                    fileInput.files = files;
                    displayFilePreview(file);
                } else {
                    showError('Please select a valid image file (PNG, JPG, JPEG, GIF, WebP)');
                }
            }
        });
        
        // Click to upload
        uploadArea.addEventListener('click', function() {
            fileInput.click();
        });
    }
    
    function isValidImageFile(file) {
        const validTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp'];
        return validTypes.includes(file.type);
    }
    
    function displayFilePreview(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.createElement('div');
            preview.className = 'mt-4';
            preview.innerHTML = `
                <div class="flex items-center space-x-3">
                    <img src="${e.target.result}" alt="Preview" class="w-20 h-20 object-cover rounded-lg">
                    <div>
                        <p class="text-sm font-medium text-gray-900">${file.name}</p>
                        <p class="text-xs text-gray-500">${(file.size / 1024 / 1024).toFixed(2)} MB</p>
                        <button type="button" onclick="removeFilePreview()" class="text-red-600 hover:text-red-800 text-xs">
                            <i class="fas fa-times mr-1"></i>Remove
                        </button>
                    </div>
                </div>
            `;
            
            // Remove existing preview
            const existingPreview = uploadArea.querySelector('.mt-4');
            if (existingPreview) {
                existingPreview.remove();
            }
            
            uploadArea.appendChild(preview);
        };
        reader.readAsDataURL(file);
    }
    
    function showError(message) {
        // Create error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'mt-2 text-red-600 text-sm';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle mr-1"></i>${message}`;
        
        // Remove existing error
        const existingError = uploadArea.parentNode.querySelector('.text-red-600');
        if (existingError) {
            existingError.remove();
        }
        
        uploadArea.parentNode.appendChild(errorDiv);
        
        // Remove error after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
    
    // Global function to remove file preview
    window.removeFilePreview = function() {
        const preview = uploadArea.querySelector('.mt-4');
        if (preview) {
            preview.remove();
        }
        fileInput.value = '';
    };
});
