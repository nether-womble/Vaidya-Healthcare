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

def translate_to_hindi(text):
    """Translate text to Hindi"""
    try:
        return translator.translate(text, dest='hi').text
    except:
        return text  # Return original text if translation fails

def analyze_symptoms(symptoms):
    """Analyze symptoms and return matching diseases with their details"""
    symptoms_lower = symptoms.lower()
    matching_diseases = []
    
    for disease_data in medical_data['symptom_disease_mapping']:
        disease_symptoms = disease_data['symptoms'].lower()
        # Check if any of the input symptoms match with disease symptoms
        if any(symptom.strip() in disease_symptoms for symptom in symptoms_lower.split(',')):
            matching_diseases.append({
                'disease': disease_data['disease'],
                'disease_hi': translate_to_hindi(disease_data['disease']),
                'severity': disease_data['severity'],
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
    st.title('🏥 Vaidya - Healthcare AI Assistant')
    st.subheader('Supporting Rural Healthcare Workers')
    
    # Language selection
    language = st.radio('Select Language / भाषा चुनें', ['English', 'हिंदी'], horizontal=True)
    
    # Symptom Input
    st.write('### Patient Symptoms')
    symptoms = st.text_area('Enter patient symptoms (in English or Hindi):', height=100)
    
    if st.button('Analyze Symptoms'):
        if symptoms:
            with st.spinner('Analyzing symptoms...'):
                # Get disease matches and risk assessment
                matching_diseases, risk_level, recommendation = analyze_symptoms(symptoms)
                
                # Display results
                st.write('### Analysis Result:')
                
                # Display risk level with color coding
                risk_color = {
                    'mild': 'green',
                    'moderate': 'orange',
                    'severe': 'red'
                }[risk_level.lower()]
                
                st.markdown(f"**Risk Level:** ::{risk_color}[{risk_level}]")
                
                if matching_diseases:
                    st.write('#### Health Assessment / स्वास्थ्य मूल्यांकन:')
                    for disease in matching_diseases:
                        if language == 'English':
                            st.markdown(f"**Disease:** {disease['disease']}")
                            st.markdown(f"**Severity:** {disease['severity']}")
                            st.markdown(f"**Treatment:** {disease['treatment']}")
                            st.markdown(f"**When to Escalate:** {disease['escalation_criteria']}")
                        else:
                            st.markdown(f"**रोग:** {disease['disease_hi']}")
                            st.markdown(f"**गंभीरता:** {translate_to_hindi(disease['severity'])}")
                            st.markdown(f"**उपचार:** {disease['treatment_hi']}")
                            st.markdown(f"**कब डॉक्टर को दिखाएं:** {disease['escalation_criteria_hi']}")
                        st.markdown("---")
                else:
                    st.warning('No specific disease matches found. Please consult a healthcare professional.')
                
                st.markdown(f"**General Recommendation:** {recommendation}")
                
                # Save consultation
                save_consultation(symptoms, matching_diseases, risk_level, recommendation)
                st.success('Consultation saved successfully!')
    
    # Show consultation history
    show_history = st.checkbox('Show Consultation History')
    if show_history:
        conn = sqlite3.connect('consultations.db')
        history = pd.read_sql_query('SELECT * FROM consultations', conn)
        conn.close()
        st.write(history)

if __name__ == '__main__':
    main()