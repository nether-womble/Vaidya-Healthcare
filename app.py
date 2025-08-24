import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import json
from googletrans import Translator

# Initialize translator
translator = Translator()

# Load medical data
with open('medical_data.json', 'r') as f:
    medical_data = json.load(f)

# Page configuration
st.set_page_config(
    page_title="Vaidya - Healthcare AI Assistant",
    page_icon="🏥",
    layout="wide"
)

import asyncio

def translate_to_hindi(text):
    """Translate text to Hindi"""
    try:
        # Create event loop if it doesn't exist
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run translation in the event loop
        translation = loop.run_until_complete(translator.translate(text, dest='hi'))
        return translation.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails

def analyze_symptoms(symptoms):
    """Analyze symptoms and return matching diseases with their details"""
    symptoms_lower = symptoms.lower()
    matching_diseases = []
    
    for disease_data in medical_data['symptom_disease_mapping']:
        disease_symptoms = disease_data['symptoms'].lower()
        # Check if any of the input symptoms match with disease symptoms
        if any(symptom.strip() in disease_symptoms for symptom in symptoms_lower.split(',')):
            # Translate all fields to Hindi
            matching_diseases.append({
                'disease': disease_data['disease'],
                'disease_hi': translate_to_hindi(disease_data['disease']),
                'severity': disease_data['severity'],
                'severity_hi': translate_to_hindi(disease_data['severity']),
                'treatment': disease_data['treatment'],
                'treatment_hi': translate_to_hindi(disease_data['treatment']),
                'escalation_criteria': disease_data['escalation_criteria'],
                'escalation_criteria_hi': translate_to_hindi(disease_data['escalation_criteria'])
            })
    
    if not matching_diseases:
        return None, 'Mild', 'Please consult a healthcare professional for proper diagnosis.'
    
    # Determine highest severity among matching diseases
    severity_levels = {'mild': 1, 'moderate': 2, 'severe': 3}
    max_severity = max(matching_diseases, key=lambda x: severity_levels[x['severity'].lower()])
    
    return matching_diseases, max_severity['severity'], max_severity['treatment']

def save_consultation(symptoms, diagnosis, risk_level, recommendation):
    """Save consultation details to SQLite database"""
    conn = sqlite3.connect('consultations.db')
    c = conn.cursor()
    
    # Create table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS consultations
        (timestamp TEXT, symptoms TEXT, diagnosis TEXT, risk_level TEXT, recommendation TEXT)
    ''')
    
    # Insert consultation record
    c.execute('''
        INSERT INTO consultations VALUES (?, ?, ?, ?, ?)
    ''', (datetime.now().isoformat(), symptoms, str(diagnosis), risk_level, recommendation))
    
    conn.commit()
    conn.close()

def main():
    language = st.radio('Select Language / भाषा चुनें', ['English', 'हिंदी'], horizontal=True)
    
    # Title and headers with translation
    if language == 'English':
        st.title('🏥 Vaidya - Healthcare AI Assistant')
        st.subheader('Supporting Rural Healthcare Workers')
        symptom_text = 'Patient Symptoms'
        symptom_input = 'Enter patient symptoms (in English or Hindi):'
        analyze_button = 'Analyze Symptoms'
    else:
        st.title('🏥 वैद्य - स्वास्थ्य सहायक')
        st.subheader('ग्रामीण स्वास्थ्य कार्यकर्ताओं का समर्थन')
        symptom_text = 'रोगी के लक्षण'
        symptom_input = 'रोगी के लक्षण दर्ज करें (अंग्रेजी या हिंदी में):'
        analyze_button = 'लक्षणों का विश्लेषण करें'
    
    # Symptom Input
    st.write(f'### {symptom_text}')
    symptoms = st.text_area(symptom_input, height=100)
    
    if st.button(analyze_button):
        if symptoms:
            with st.spinner('Analyzing symptoms...'):
                # Get disease matches and risk assessment
                matching_diseases, risk_level, recommendation = analyze_symptoms(symptoms)
                
                # Display results with translation
                if language == 'English':
                    st.write('### Analysis Result:')
                    risk_text = 'Risk Level'
                else:
                    st.write('### विश्लेषण परिणाम:')
                    risk_text = 'जोखिम स्तर'
                
                # Display risk level with color coding
                risk_color = {
                    'mild': 'green',
                    'moderate': 'orange',
                    'severe': 'red'
                }[risk_level.lower()]
                
                if language == 'English':
                    st.markdown(f"**{risk_text}:** ::{risk_color}[{risk_level}]")
                else:
                    # Translate risk level and ensure consistent translation
                    risk_level_hi = translate_to_hindi(risk_level)
                    st.markdown(f"**{risk_text}:** ::{risk_color}[{risk_level_hi}]")
                
                if matching_diseases:
                    if language == 'English':
                        st.write('#### Health Assessment:')
                    else:
                        st.write('#### स्वास्थ्य मूल्यांकन:')

                    for disease in matching_diseases:
                        if language == 'English':
                            st.markdown(f"**Disease:** {disease['disease']}")
                            st.markdown(f"**Severity:** {disease['severity']}")
                            st.markdown(f"**Treatment:** {disease['treatment']}")
                            st.markdown(f"**When to Escalate:** {disease['escalation_criteria']}")
                        else:
                            # Display all text in Hindi
                            try:
                                # Use pre-translated text or translate in real-time
                                disease_name = disease.get('disease_hi', translate_to_hindi(disease['disease']))
                                severity = disease.get('severity_hi', translate_to_hindi(disease['severity']))
                                treatment = disease.get('treatment_hi', translate_to_hindi(disease['treatment']))
                                escalation = disease.get('escalation_criteria_hi', translate_to_hindi(disease['escalation_criteria']))
                                
                                st.markdown(f"**रोग:** {disease_name}")
                                st.markdown(f"**गंभीरता:** {severity}")
                                st.markdown(f"**उपचार:** {treatment}")
                                st.markdown(f"**कब डॉक्टर को दिखाएं:** {escalation}")
                            except Exception as e:
                                st.error("Translation error occurred. Showing original text.")
                                st.markdown(f"**रोग:** {disease['disease']}")
                                st.markdown(f"**गंभीरता:** {disease['severity']}")
                                st.markdown(f"**उपचार:** {disease['treatment']}")
                                st.markdown(f"**कब डॉक्टर को दिखाएं:** {disease['escalation_criteria']}")
                        st.markdown("---")
                else:
                    if language == 'English':
                        st.warning('No specific disease matches found. Please consult a healthcare professional.')
                    else:
                        st.warning('कोई विशिष्ट रोग नहीं मिला। कृपया चिकित्सक से परामर्श करें।')
                
                if language == 'English':
                    st.markdown(f"**General Recommendation:** {recommendation}")
                    save_msg = 'Consultation saved successfully!'
                else:
                    translated_recommendation = translate_to_hindi(recommendation)
                    st.markdown(f"**सामान्य सिफारिश:** {translated_recommendation}")
                    save_msg = 'परामर्श सफलतापूर्वक सहेजा गया!'
                
                # Save consultation
                save_consultation(symptoms, matching_diseases, risk_level, recommendation)
                st.success(save_msg)
    
    # Show consultation history with translation
    if language == 'English':
        show_history = st.checkbox('Show Consultation History')
    else:
        show_history = st.checkbox('परामर्श इतिहास दिखाएं')
    
    if show_history:
        conn = sqlite3.connect('consultations.db')
        history = pd.read_sql_query('SELECT * FROM consultations', conn)
        conn.close()
        
        if language == 'हिंदी':
            # Translate column names to Hindi
            history.columns = ['समय', 'लक्षण', 'निदान', 'जोखिम स्तर', 'सिफारिश']
        
        st.write(history)

if __name__ == '__main__':
    main()