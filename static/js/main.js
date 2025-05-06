// Define translations object
const translations = {
    'en': {
        'title': 'AI Healthcare Assistant',
        'symptoms': 'Enter your symptoms',
        'upload': 'Upload Image',
        'analyze': 'Analyze',
        'language': 'Language',
        'emergency': 'Emergency',
        'urgent': 'Urgent',
        'warning': 'Please consult a healthcare professional',
        'loading': 'Analyzing...',
        'error': 'An error occurred while analyzing symptoms'
    },
    'bn': {
        'title': 'এআই স্বাস্থ্য সহায়ক',
        'symptoms': 'আপনার লক্ষণগুলি লিখুন',
        'upload': 'ছবি আপলোড করুন',
        'analyze': 'বিশ্লেষণ করুন',
        'language': 'ভাষা',
        'language': 'ভাষা'
    }
};

let currentLanguage = 'en';

function changeLanguage(lang) {
    currentLanguage = lang;
    // Update UI elements with new language
    document.getElementById('title').textContent = translations[lang].title;
    document.getElementById('symptoms-title').textContent = translations[lang].symptoms;
    document.getElementById('analyze-btn').textContent = translations[lang].analyze;
    document.getElementById('symptoms-input').placeholder = translations[lang].symptoms;
}

async function analyzeSymptoms() {
    const symptoms = document.getElementById('symptoms-input').value;
    if (!symptoms.trim()) {
        alert('Please enter symptoms');
        return;
    }

    // Show loading state
    const analyzeBtn = document.getElementById('analyze-btn');
    const originalBtnText = analyzeBtn.textContent;
    analyzeBtn.textContent = translations[currentLanguage].loading;
    analyzeBtn.disabled = true;

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                symptoms: symptoms,
                language: currentLanguage
            })
        });

        const data = await response.json();
        displayResults(data);
    } catch (error) {
        console.error('Error:', error);
        alert(translations[currentLanguage].error);
    } finally {
        // Reset button state
        analyzeBtn.textContent = originalBtnText;
        analyzeBtn.disabled = false;
    }
}

async function analyzeImage() {
    const imageInput = document.getElementById('image-input');
    const file = imageInput.files[0];
    
    if (!file) {
        alert('Please select an image');
        return;
    }

    const formData = new FormData();
    formData.append('image', file);
    formData.append('language', currentLanguage);

    try {
        const response = await fetch('/analyze_image', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        displayResults(data);
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while analyzing the image');
    }
}

function displayResults(data) {
    const resultsSection = document.getElementById('results');
    const diagnosisResult = document.getElementById('diagnosis-result');
    const confidenceMeter = document.getElementById('confidence-meter');
    const recommendations = document.getElementById('recommendations');

    // Display diagnosis with urgency level
    let urgencyClass = '';
    let urgencyMessage = '';
    
    if (data.urgency === 'emergency') {
        urgencyClass = 'emergency';
        urgencyMessage = translations[currentLanguage].emergency;
    } else if (data.urgency === 'urgent') {
        urgencyClass = 'urgent';
        urgencyMessage = translations[currentLanguage].urgent;
    }

    diagnosisResult.innerHTML = `
        <div class="urgency-message ${urgencyClass}">${urgencyMessage}</div>
        <h3>${data.diagnosis}</h3>
    `;

    // Display confidence meter
    const confidencePercentage = Math.round(data.confidence * 100);
    confidenceMeter.innerHTML = `
        <div style="width: ${confidencePercentage}%"></div>
        <p>Confidence: ${confidencePercentage}%</p>
    `;

    // Display recommendations and medicine information
    let recommendationsHtml = `
        <h3>Recommendations:</h3>
        <ul>
            ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
        </ul>
    `;

    // Add medicine recommendations if available
    if (data.medicine_recommendations && data.medicine_recommendations.length > 0) {
        recommendationsHtml += `
            <div class="medicine-recommendations">
                <h3>Medicine Recommendations:</h3>
                ${data.medicine_recommendations.map(rec => `
                    <div class="medicine-card">
                        <h4>${rec.condition}</h4>
                        <div class="medicines">
                            ${rec.medicines.map(med => `
                                <div class="medicine">
                                    <strong>${med.name}</strong>
                                    <p>Dosage: ${med.dosage}</p>
                                    <p>Maximum daily: ${med.max_daily}</p>
                                </div>
                            `).join('')}
                        </div>
                        <div class="medicine-warning">${rec.warning}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    recommendationsHtml += `<div class="warning-message">${translations[currentLanguage].warning}</div>`;
    recommendations.innerHTML = recommendationsHtml;

    resultsSection.style.display = 'block';
}

// Handle drag and drop for image upload
const dropZone = document.getElementById('drop-zone');
const imageInput = document.getElementById('image-input');

dropZone.addEventListener('click', () => imageInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '#3498db';
});

dropZone.addEventListener('dragleave', () => {
    dropZone.style.borderColor = '#ddd';
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '#ddd';
    
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        imageInput.files = e.dataTransfer.files;
    } else {
        alert('Please drop an image file');
    }
});

imageInput.addEventListener('change', () => {
    if (imageInput.files.length > 0) {
        const fileName = imageInput.files[0].name;
        document.querySelector('.upload-prompt p').textContent = fileName;
    }
}); 