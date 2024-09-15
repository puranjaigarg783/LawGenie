import json
import os
import re
import base64
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from openai import OpenAI
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

load_dotenv()


solar_llm = OpenAI(
    api_key=os.getenv("UPSTAGE_API_KEY"), base_url="https://api.upstage.ai/v1/solar"
)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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
                print(json.dumps(result, indent=2))
                # Extract the full text from the response
                contract_text = ""
                for page in result.get("pages", []):
                    for element in page.get("elements", []):
                        if element.get("category") == "text":
                            contract_text += element.get("text", "") + "\n"
                return contract_text
            else:
                raise Exception(f"Error in Document Parse API: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise


def parse_contract_old(file_path):
    # Debug the API key
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        raise Exception("API key is missing")
    print(f"API Key: {api_key}")

    url = "https://api.upstage.ai/v1/document-ai/ocr"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        with open(file_path, "rb") as file:
            files = {"document": file}
            print("Sending request to OCR API...")
            response = requests.post(url, headers=headers, files=files)

            # Debug the response status code and content
            #            print(f"API Response Status Code: {response.status_code}")
            #            print(f"API Response Content: {response.text}")

            if response.status_code == 200:
                result = response.json()
                # Extract the full text from the response
                contract_text = result.get("text", "")
                return contract_text
            else:
                raise Exception(
                    f"Error in OCR API: {response.status_code}, {response.text}"
                )
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def segment_contract(contract_text):
    """
    Segments an NDA (Non-Disclosure Agreement) into predefined sections.

    Args:
        contract_text (str): The full text of the NDA to be segmented.

    Returns:
        dict: A dictionary containing the segmented sections with their
              summaries and full text. If an error occurs during the process, 
              an error message and raw response are returned.
    """

    # Define the prompt to analyze and segment the NDA text
    prompt = f"""
    Analyze the following Non-Disclosure Agreement (NDA) and segment it into key sections. 
    Focus on identifying these common NDA sections:

    1. Parties: Identify the parties entering into the agreement.
    2. Definition of Confidential Information: How confidential information is defined in this agreement.
    3. Obligations of Receiving Party: The duties of the party receiving confidential information.
    4. Exclusions from Confidential Information: What is not considered confidential under this agreement.
    5. Term and Termination: The duration of the agreement and how it can be terminated.
    6. Return of Confidential Information: Provisions for returning or destroying confidential information.
    7. Remedies: The consequences for breaching the agreement.

    For each identified section, provide:
    1. The section name
    2. A brief summary of what the section covers (1-2 sentences)
    3. The full text of the section. Do not skip any text within each section. Bring whole sentences.

    If a section is not present in the agreement, note its absence in the summary.
    If you find additional important sections not listed above, include them as well.

    Return the result as a JSON object where keys are section names and values are objects containing 'summary' and 'full_text'.

    NDA text:
    {contract_text}
    """

    try:
        print("Sending request to Solar LLM...")

        # Invoke the Solar LLM API and stream the result
        stream = solar_llm.chat.completions.create(
            model="solar-pro",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True
        )

        response_content = ""

        # Collecting the streamed response into a full text
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response_content += chunk.choices[0].delta.content

        print(f"Received response: {response_content}")

        # Attempt to parse the response as JSON
        try:
            segmented_contract = json.loads(response_content)
            return segmented_contract
        except json.JSONDecodeError:
            print("Failed to decode JSON response.")
            return {"error": "Failed to parse JSON", "raw_response": response_content}

    except Exception as e:
        print(f"An error occurred during the API request: {e}")
        return {"error": str(e)}
                                 




def segment_clauses(text):
    # Simple clause segmentation by paragraphs
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
    analyze_clause = ()  # TODO: fix
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
        try:
            contract_text = parse_contract(file_path)
            segmented_contract = segment_contract(contract_text)
            return jsonify(
                {
                    "message": "File uploaded and processed successfully",
                    "segmented_contract": segmented_contract,
                    # 		"output": contract_text
                }
            )
        except Exception as e:
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
    app.run(debug=True)
