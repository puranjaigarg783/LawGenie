import re
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document as DocxDocument

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_contract(file):
    if file.filename.endswith('.pdf'):
        return extract_pdf_text(file)
    elif file.filename.endswith('.docx'):
        doc = DocxDocument(file)
        return '\n'.join([para.text for para in doc.paragraphs])

def analyze_clause(clause):
    keywords = {
        'payment': ['payment', 'fee', 'cost', 'price'],
        'deadline': ['deadline', 'due date', 'timeline'],
        'confidentiality': ['confidential', 'non-disclosure', 'NDA'],
        'termination': ['termination', 'cancel', 'end of agreement']
    }
    
    issues = []
    for category, words in keywords.items():
        if any(word in clause.lower() for word in words):
            issues.append(f"Found {category} clause. Please review carefully.")
    
    return issues if issues else ["No significant issues found."]

def segment_clauses(text):
    # Simple clause segmentation by paragraphs
    return [clause.strip() for clause in re.split(r'\n\n|\r\n\r\n', text) if clause.strip()]


def generate_recommendation(clause, analysis):
    recommendations = []
    if "payment" in analysis:
        recommendations.append("Ensure payment terms are clearly defined and favorable.")
    if "deadline" in analysis:
        recommendations.append("Review deadlines to ensure they are realistic and include buffer time.")
    if "confidentiality" in analysis:
        recommendations.append("Verify that confidentiality clauses protect your interests adequately.")
    if "termination" in analysis:
        recommendations.append("Check termination conditions and ensure they are fair to both parties.")
    
    return recommendations if recommendations else ["No specific recommendations. The clause appears standard."]



@app.route('/analyze', methods=['POST'])
def analyze_contract():
    data = request.json
    contract_text = data.get('text', '')
    clauses = segment_clauses(contract_text)
    analysis = [{"clause": clause, "analysis": analyze_clause(clause)} for clause in clauses]
    return jsonify({"analysis": analysis})


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        contract_text = parse_contract(file_path)
        return jsonify({"message": "File uploaded successfully", "text": contract_text})
    return jsonify({"error": "File type not allowed"}), 400

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    clause = data.get('clause', '')
    analysis = data.get('analysis', [])
    recommendations = generate_recommendation(clause, ' '.join(analysis))
    return jsonify({"recommendations": recommendations})

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
