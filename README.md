# AI Healthcare Assistant for Bangladesh

An intelligent healthcare web application designed specifically for Bangladesh, providing symptom analysis, medical information, and medicine recommendations in both English and Bengali.

## Features

### 1. Bilingual Interface
- Full support for English and Bengali languages
- Culturally relevant healthcare advice
- Easy language switching

### 2. Intelligent Symptom Analysis
- Real-time symptom analysis using web scraping
- Information gathered from reliable medical sources (WebMD, Mayo Clinic)
- Urgency level detection (Emergency, Urgent, Normal)
- Confidence scoring for diagnoses

### 3. Medicine Recommendations
- Comprehensive medicine database
- Detailed dosage information
- Maximum daily limits
- Warning messages
- Support for common conditions:
  - Fever
  - Headache
  - Cough
  - Allergies
  - General pain

### 4. User-Friendly Interface
- Clean, modern design
- Responsive layout for all devices
- Easy-to-read medicine cards
- Clear warning messages
- Confidence meter visualization

### 5. Performance Optimizations
- Caching system for faster responses
- Lightweight design for low-bandwidth networks
- Efficient web scraping with proper error handling

## Technical Stack

- **Frontend:**
  - HTML5
  - CSS3 (with responsive design)
  - JavaScript (ES6+)
  - Noto Sans Bengali font for Bengali text

- **Backend:**
  - Python 3.x
  - Flask web framework
  - BeautifulSoup4 for web scraping
  - Requests for HTTP calls

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/healthcare-assistant.git
cd healthcare-assistant
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

1. Select your preferred language (English or Bengali)
2. Enter your symptoms in detail
3. Click "Analyze Symptoms"
4. Review the results:
   - Diagnosis
   - Confidence level
   - Urgency level
   - Medicine recommendations (if applicable)
   - General recommendations
   - Source links for more information

## Important Notes

- This application is not a substitute for professional medical advice
- Always consult healthcare professionals for proper diagnosis and treatment
- Medicine recommendations are for informational purposes only
- Follow the provided warnings and dosage instructions carefully

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- WebMD and Mayo Clinic for medical information
- Noto Sans Bengali font by Google
- All contributors and supporters of the project 