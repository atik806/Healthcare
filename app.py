from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Cache configuration
CACHE_FILE = 'medical_cache.json'
CACHE_DURATION = timedelta(hours=24)

# Medicine database
MEDICINE_DATABASE = {
    'en': {
        'fever': {
            'common_medicines': [
                {'name': 'Paracetamol', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                {'name': 'Ibuprofen', 'dosage': '200-400mg every 4-6 hours', 'max_daily': '1200mg'}
            ],
            'warning': 'Consult doctor if fever persists for more than 3 days'
        },
        'headache': {
            'common_medicines': [
                {'name': 'Paracetamol', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                {'name': 'Aspirin', 'dosage': '325-650mg every 4-6 hours', 'max_daily': '4000mg'}
            ],
            'warning': 'Seek medical attention for severe or persistent headaches'
        },
        'cough': {
            'common_medicines': [
                {'name': 'Dextromethorphan', 'dosage': '10-20mg every 4-6 hours', 'max_daily': '120mg'},
                {'name': 'Guaifenesin', 'dosage': '200-400mg every 4 hours', 'max_daily': '2400mg'}
            ],
            'warning': 'Consult doctor if cough persists for more than 2 weeks'
        },
        'allergy': {
            'common_medicines': [
                {'name': 'Cetirizine', 'dosage': '10mg once daily', 'max_daily': '10mg'},
                {'name': 'Loratadine', 'dosage': '10mg once daily', 'max_daily': '10mg'}
            ],
            'warning': 'Avoid known allergens and consult doctor if symptoms worsen'
        },
        'pain': {
            'common_medicines': [
                {'name': 'Paracetamol', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                {'name': 'Ibuprofen', 'dosage': '200-400mg every 4-6 hours', 'max_daily': '1200mg'}
            ],
            'warning': 'Seek medical attention for severe or persistent pain'
        }
    },
    'bn': {
        'fever': {
            'common_medicines': [
                {'name': 'প্যারাসিটামল', 'dosage': '৫০০-১০০০ মিলিগ্রাম প্রতি ৪-৬ ঘন্টায়', 'max_daily': '৪০০০ মিলিগ্রাম'},
                {'name': 'আইবুপ্রোফেন', 'dosage': '২০০-৪০০ মিলিগ্রাম প্রতি ৪-৬ ঘন্টায়', 'max_daily': '১২০০ মিলিগ্রাম'}
            ],
            'warning': '৩ দিনের বেশি জ্বর থাকলে ডাক্তারের সাথে পরামর্শ করুন'
        },
        'headache': {
            'common_medicines': [
                {'name': 'প্যারাসিটামল', 'dosage': '৫০০-১০০০ মিলিগ্রাম প্রতি ৪-৬ ঘন্টায়', 'max_daily': '৪০০০ মিলিগ্রাম'},
                {'name': 'অ্যাসপিরিন', 'dosage': '৩২৫-৬৫০ মিলিগ্রাম প্রতি ৪-৬ ঘন্টায়', 'max_daily': '৪০০০ মিলিগ্রাম'}
            ],
            'warning': 'তীব্র বা দীর্ঘস্থায়ী মাথাব্যথার জন্য চিকিৎসকের পরামর্শ নিন'
        },
        'cough': {
            'common_medicines': [
                {'name': 'ডেক্সট্রোমেথরফ্যান', 'dosage': '১০-২০ মিলিগ্রাম প্রতি ৪-৬ ঘন্টায়', 'max_daily': '১২০ মিলিগ্রাম'},
                {'name': 'গুয়াইফেনেসিন', 'dosage': '২০০-৪০০ মিলিগ্রাম প্রতি ৪ ঘন্টায়', 'max_daily': '২৪০০ মিলিগ্রাম'}
            ],
            'warning': '২ সপ্তাহের বেশি কাশি থাকলে ডাক্তারের সাথে পরামর্শ করুন'
        },
        'allergy': {
            'common_medicines': [
                {'name': 'সেটিরিজিন', 'dosage': '১০ মিলিগ্রাম দিনে একবার', 'max_daily': '১০ মিলিগ্রাম'},
                {'name': 'লোরাটাডিন', 'dosage': '১০ মিলিগ্রাম দিনে একবার', 'max_daily': '১০ মিলিগ্রাম'}
            ],
            'warning': 'জানা অ্যালার্জেন এড়িয়ে চলুন এবং লক্ষণ বাড়লে ডাক্তারের সাথে পরামর্শ করুন'
        },
        'pain': {
            'common_medicines': [
                {'name': 'প্যারাসিটামল', 'dosage': '৫০০-১০০০ মিলিগ্রাম প্রতি ৪-৬ ঘন্টায়', 'max_daily': '৪০০০ মিলিগ্রাম'},
                {'name': 'আইবুপ্রোফেন', 'dosage': '২০০-৪০০ মিলিগ্রাম প্রতি ৪-৬ ঘন্টায়', 'max_daily': '১২০০ মিলিগ্রাম'}
            ],
            'warning': 'তীব্র বা দীর্ঘস্থায়ী ব্যথার জন্য চিকিৎসকের পরামর্শ নিন'
        }
    }
}

# Language dictionary for translations
TRANSLATIONS = {
    'en': {
        'title': 'AI Healthcare Assistant',
        'symptoms': 'Enter your symptoms in detail (e.g., "I have a severe headache and fever for 2 days")',
        'analyze': 'Analyze Symptoms',
        'language': 'Language',
        'emergency': 'EMERGENCY: Please seek immediate medical attention!',
        'urgent': 'URGENT: Please visit a doctor as soon as possible.',
        'warning': 'Warning: This is not a substitute for professional medical advice.',
        'loading': 'Analyzing symptoms...',
        'error': 'An error occurred. Please try again.'
    },
    'bn': {
        'title': 'এআই স্বাস্থ্য সহায়ক',
        'symptoms': 'বিস্তারিতভাবে আপনার লক্ষণগুলি লিখুন (যেমন: "আমার ২ দিন ধরে তীব্র মাথাব্যথা এবং জ্বর আছে")',
        'analyze': 'লক্ষণ বিশ্লেষণ করুন',
        'language': 'ভাষা',
        'emergency': 'জরুরি: দয়া করে অবিলম্বে চিকিৎসা সহায়তা নিন!',
        'urgent': 'জরুরি: দয়া করে যত তাড়াতাড়ি সম্ভব ডাক্তারের কাছে যান।',
        'warning': 'সতর্কতা: এটি পেশাদার চিকিৎসা পরামর্শের বিকল্প নয়।',
        'loading': 'লক্ষণগুলি বিশ্লেষণ করা হচ্ছে...',
        'error': 'একটি ত্রুটি ঘটেছে। অনুগ্রহ করে আবার চেষ্টা করুন।'
    }
}

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
            current_time = datetime.now()
            return {k: v for k, v in cache_data.items() 
                   if datetime.fromisoformat(v['timestamp']) + CACHE_DURATION > current_time}
    return {}

def save_cache(cache_data):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

def get_medicine_recommendations(symptoms, language):
    """Get medicine recommendations based on symptoms"""
    symptoms = symptoms.lower()
    recommendations = []
    
    # Check each condition in the medicine database
    for condition, data in MEDICINE_DATABASE[language].items():
        if condition in symptoms:
            recommendations.append({
                'condition': condition,
                'medicines': data['common_medicines'],
                'warning': data['warning']
            })
    
    return recommendations

def scrape_webmd(symptoms):
    """Scrape WebMD for symptom information"""
    try:
        search_query = '+'.join(symptoms.split())
        url = f'https://www.webmd.com/search/search_results/default.aspx?query={search_query}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for article in soup.find_all('div', class_='search-results-item'):
            title = article.find('h3')
            if title:
                results.append({
                    'title': title.text.strip(),
                    'url': article.find('a')['href'] if article.find('a') else None
                })
        
        return results
    except Exception as e:
        print(f"Error scraping WebMD: {str(e)}")
        return []

def scrape_mayoclinic(symptoms):
    """Scrape Mayo Clinic for symptom information"""
    try:
        search_query = '+'.join(symptoms.split())
        url = f'https://www.mayoclinic.org/search/search-results?q={search_query}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for article in soup.find_all('div', class_='search-result'):
            title = article.find('h3')
            if title:
                results.append({
                    'title': title.text.strip(),
                    'url': article.find('a')['href'] if article.find('a') else None
                })
        
        return results
    except Exception as e:
        print(f"Error scraping Mayo Clinic: {str(e)}")
        return []

def get_medical_info(symptoms, language):
    """Get medical information from multiple sources"""
    cache = load_cache()
    cache_key = f"{symptoms}_{language}"
    
    # Check cache first
    if cache_key in cache:
        return cache[cache_key]['data']
    
    # Scrape information from multiple sources
    webmd_results = scrape_webmd(symptoms)
    mayoclinic_results = scrape_mayoclinic(symptoms)
    
    # Combine and process results
    all_results = webmd_results + mayoclinic_results
    
    # Determine urgency based on keywords
    urgency_keywords = {
        'emergency': ['emergency', 'severe', 'acute', 'critical', 'immediate', 'urgent'],
        'urgent': ['serious', 'concerning', 'worrying', 'significant']
    }
    
    urgency = 'normal'
    for result in all_results:
        title_lower = result['title'].lower()
        for level, keywords in urgency_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                urgency = level
                break
    
    # Get medicine recommendations
    medicine_recommendations = get_medicine_recommendations(symptoms, language)
    
    # Generate recommendations based on results
    recommendations = []
    if all_results:
        for result in all_results[:3]:  # Take top 3 results
            recommendations.append(f"Read more about: {result['title']}")
    
    # Add standard recommendations
    if urgency == 'emergency':
        recommendations.insert(0, 'Seek immediate medical attention')
    elif urgency == 'urgent':
        recommendations.insert(0, 'Schedule a doctor\'s appointment as soon as possible')
    
    recommendations.extend([
        'Monitor your symptoms',
        'Keep track of any changes',
        'Consult a healthcare professional for proper diagnosis'
    ])
    
    # Prepare response
    response = {
        'diagnosis': all_results[0]['title'] if all_results else 'Unable to determine specific condition',
        'confidence': 0.8 if all_results else 0.5,
        'recommendations': recommendations,
        'urgency': urgency,
        'sources': [result['url'] for result in all_results if result['url']],
        'medicine_recommendations': medicine_recommendations
    }
    
    # Cache the results
    cache[cache_key] = {
        'data': response,
        'timestamp': datetime.now().isoformat()
    }
    save_cache(cache)
    
    return response

@app.route('/')
def index():
    return render_template('index.html', translations=TRANSLATIONS, language='en')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    symptoms = data.get('symptoms', '')
    language = data.get('language', 'en')
    
    result = get_medical_info(symptoms, language)
    return jsonify(result)

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image = request.files['image']
    language = request.form.get('language', 'en')
    
    # TODO: Implement image analysis with AI model
    # This is a placeholder response
    response = {
        'diagnosis': 'Skin rash' if language == 'en' else 'ত্বকের ফুসকুড়ি',
        'confidence': 0.92,
        'recommendations': [
            'Apply prescribed cream' if language == 'en' else 'নির্ধারিত ক্রিম ব্যবহার করুন',
            'Avoid scratching' if language == 'en' else 'চুলকানো এড়িয়ে চলুন'
        ],
        'urgency': 'normal'
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True) 