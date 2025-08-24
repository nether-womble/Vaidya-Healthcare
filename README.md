# Vaidya - AI Doctor's Assistant for Rural Healthcare Workers

Vaidya is an AI-powered medical assistance application designed to support healthcare workers in rural areas. It helps in preliminary diagnosis based on symptoms and provides guidance on whether local treatment is sufficient or hospital referral is necessary.

## Features

- Symptom-based disease prediction using BioBERT
- Risk assessment and treatment recommendations
- Consultation history tracking
- Supports both English and Hindi inputs
- Offline-first design for areas with limited internet connectivity

## Technical Stack

- Frontend: Streamlit
- ML Model: PubMedBERT (from HuggingFace)
- Database: SQLite for consultation history
- Additional Libraries: PyTorch, scikit-learn, FAISS

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage Guide

1. Enter patient symptoms in the text area (English or Hindi)
2. Click 'Analyze Symptoms' to get:
   - Possible diagnoses
   - Risk level assessment
   - Treatment recommendations
   - Referral guidance
3. View consultation history using the checkbox below

## Data Privacy

- All consultations are stored locally
- No patient data is transmitted to external servers
- Compliant with basic medical data privacy practices

## Offline Usage

The application works offline after initial setup. The BioBERT model is downloaded during the first run and cached locally for subsequent use.

## Support

For issues and suggestions, please create an issue in the repository.

## License

MIT License