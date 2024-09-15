import regex
import json
import os
import re
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
from together import Together
from crew import get_agent_output

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

load_dotenv()


client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def inspect_and_serialize(obj):
    """
    Inspect the object and return a JSON-serializable version of it.
    """
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, list):
        return [inspect_and_serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: inspect_and_serialize(value) for key, value in obj.items()}
    elif hasattr(obj, '__dict__'):
        return inspect_and_serialize(obj.__dict__)
    else:
        return str(obj)

def debug_crew_output(crew_output):
    print("Type of crew_output:", type(crew_output))
    print("Content of crew_output:")
    print(json.dumps(inspect_and_serialize(crew_output), indent=2))

def parse_combined_output(combined_output):
    sections = {}
    current_section = None
    current_summary = ""
    current_full_text = ""
    lines = combined_output.splitlines()

    for line in lines:
        line = line.strip()
        if line.startswith("Section Name:"):
            if current_section:
                
                sections[current_section] = {
                    "summary": current_summary.strip(),
                    "full_text": current_full_text.strip()
                }
            
            current_section = line[len("Section Name:"):].strip()
            current_summary = ""
            current_full_text = ""
        elif line.startswith("Summary:"):
            current_summary = line[len("Summary:"):].strip()
        elif line.startswith("Full Text:"):
            current_full_text = line[len("Full Text:"):].strip()
        elif current_section:
            
            current_full_text += line + " "

    
    if current_section:
        sections[current_section] = {
            "summary": current_summary.strip(),
            "full_text": current_full_text.strip()
        }

    return sections


def extract_json(text):
    
    match = regex.search(r'\{(?:[^{}]|(?R))*\}', text, regex.DOTALL)
    if match:
        return match.group(0)
    else:
        raise ValueError("No JSON object found in the response.")


def call_llama_via_together_ai(prompt):
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        temperature=0.0,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>", "<|eom_id|>"],
        stream=False
    )
    return response.choices[0].message.content

def segment_contract(contract_text):
    print("In segment")
    print(f"Contract text length: {len(contract_text)}")

    chunk_size = 16000  
    chunks = [contract_text[i:i+chunk_size] for i in range(0, len(contract_text), chunk_size)]
    print(f"Number of chunks: {len(chunks)}")
    combined_output = ""

    for idx, chunk in enumerate(chunks):
        prompt = f"""
        Analyze the following part {idx+1}/{len(chunks)} of a Non-Disclosure Agreement (NDA) and segment it into key sections.
        
        Focus on identifying these common NDA sections:
        
        1. Parties
        2. Definition of Confidential Information
        3. Obligations of Receiving Party
        4. Exclusions from Confidential Information
        5. Term and Termination
        6. Return of Confidential Information
        7. Remedies
        
        For each identified section, provide:
        
        - Section Name: [Name of the section]
        - Summary: [A brief summary of what the section covers (1-2 sentences)]
        - Full Text: [The full text of the section. Do not skip any text within each section.]
        
        If a section is not present in this part, ignore it.
        
        If you find additional important sections not listed above, include them as well.
        
        Output Format:
        
        For each section, output in the following format:
        
        Section Name: [Name] Summary: [Summary] Full Text: [Full text]
        
        Do not include any additional text outside this format.
        
        NDA text part {idx+1}/{len(chunks)}:
        {chunk}
        """
        try:
            print(f"Processing chunk {idx+1}/{len(chunks)}")
            response_content = call_llama_via_together_ai(prompt)
            print(f"Received response for chunk {idx+1}")
            combined_output += response_content + "\n"
        except Exception as e:
            print(f"An error occurred while processing chunk {idx+1}: {e}")
            continue

    print("Segmentation complete.")
    return combined_output


def parse_contract(file_path):
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        raise Exception("API key is missing")
    print(f"API Key: {api_key}")

    url = "https://api.upstage.ai/v1/document-ai/document-parse"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        with open(file_path, "rb") as file:
            files = {"document": file}
            data = {
                "ocr": "auto",
                "coordinates": "false",
                "output_formats": "['text']"
            }
            print("Sending request to Document Parse API...")
            response = requests.post(url, headers=headers, files=files, data=data)

            if response.status_code == 200:
                result = response.json()
                print(f"API Response: {json.dumps(result, indent=2)}")
                
                
                contract_text = ""
                if "content" in result and "text" in result["content"]:
                    contract_text = result["content"]["text"]
                else:
                    print("Warning: 'content' or 'text' not found in API response")
                    for page in result.get("pages", []):
                        for element in page.get("elements", []):
                            if element.get("category") == "text":
                                contract_text += element.get("text", "") + "\n"
                
                print(f"Extracted text length: {len(contract_text)}")
                print(f"First 500 characters of extracted text: {contract_text[:500]}")
                
                if len(contract_text) == 0:
                    print("Warning: No text extracted from the document")
                    print("API Response structure:")
                    print(json.dumps(result, indent=2))
                
                return contract_text
            else:
                raise Exception(f"Error in Document Parse API: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def segment_clauses(text):
    
    return [
        clause.strip() for clause in re.split(r"\n\n|\r\n\r\n", text) if clause.strip()
    ]

def generate_recommendation(clause, analysis):
    recommendations = []
    if "payment" in analysis:
        recommendations.append(
            "Ensure payment terms are clearly defined and favorable."
        )
    if "deadline" in analysis:
        recommendations.append(
            "Review deadlines to ensure they are realistic and include buffer time."
        )
    if "confidentiality" in analysis:
        recommendations.append(
            "Verify that confidentiality clauses protect your interests adequately."
        )
    if "termination" in analysis:
        recommendations.append(
            "Check termination conditions and ensure they are fair to both parties."
        )

    return (
        recommendations
        if recommendations
        else ["No specific recommendations. The clause appears standard."]
    )

@app.route("/analyze", methods=["POST"])
def analyze_contract():
    data = request.json
    contract_text = data.get("text", "")
    clauses = segment_clauses(contract_text)
    
    analysis = [
        {"clause": clause, "analysis": analyze_clause(clause)} for clause in clauses
    ]
    return jsonify({"analysis": analysis})


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        print(f"File saved: {file_path}")
        print(f"File size: {os.path.getsize(file_path)} bytes")
        try:
            print("Parsing contract...")
            contract_text = parse_contract(file_path)
            print(f"Parsed contract text length: {len(contract_text)}")
            print("Contract parsed. Starting segmentation...")
            combined_output = segment_contract(contract_text)
            print("Parsing combined output...")
            segmented_contract = parse_combined_output(combined_output)
            print("Segmentation complete.")


            crew_output = get_agent_output(segmented_contract)
            debug_crew_output(crew_output) 


            response_data = {
                "message": "File uploaded and processed successfully",
                "segmented_contract": segmented_contract,
                "crew_analysis": inspect_and_serialize(crew_output)
            }
            print("Response Data:", response_data)  

            
            return jsonify(response_data)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "File type not allowed"}), 400



@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    clause = data.get("clause", "")
    analysis = data.get("analysis", [])
    recommendations = generate_recommendation(clause, " ".join(analysis))
    return jsonify({"recommendations": recommendations})

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', debug=True, port=5002)

