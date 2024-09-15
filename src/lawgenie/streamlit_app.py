import requests
import streamlit as st
from together import Together
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Together AI client
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
client = Together(api_key=TOGETHER_API_KEY)

def call_llama_for_response(clauses_data):
    prompt = "As an AI assistant specializing in contract analysis, draft a professional and courteous response to a contract drafter based on the following clause analyses and decisions:\n\n"
    
    for clause in clauses_data:
        prompt += f"Clause: {clause['agent']}\n"
        prompt += f"Analysis: {clause['analysis']}\n"
        prompt += f"Recommendation: {clause['recommendation']}\n"
        prompt += f"Decision: {clause['action']}\n"
        if clause['action'] == 'Negotiate':
            prompt += f"Negotiation points: {clause['negotiation_points']}\n"
        prompt += "\n"
    
    prompt += "Draft a response that addresses each clause, explaining our position on acceptance, rejection, or negotiation. The tone should be professional, courteous, and constructive."

    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        temperature=0.3,
        top_p=0.8,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>", "<|eom_id|>"],
        stream=False
    )
    return response.choices[0].message.content

st.title("Contract Negotiation Assistant")

# Use session state to store the uploaded file and analysis results
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# File uploader
uploaded_file = st.file_uploader("Upload Contract", type=["pdf", "docx"])

# If a new file is uploaded, update the session state and clear previous results
if uploaded_file is not None and uploaded_file != st.session_state.uploaded_file:
    st.session_state.uploaded_file = uploaded_file
    st.session_state.analysis_results = None

# If we have an uploaded file, process it
if st.session_state.uploaded_file is not None:
    # Only call the API if we don't have analysis results yet
    if st.session_state.analysis_results is None:
        files = {"file": st.session_state.uploaded_file}
        response = requests.post("http://localhost:5002/upload", files=files)
        if response.status_code == 200:
            st.write("Contract uploaded successfully. Analyzing...")
            st.session_state.analysis_results = response.json()
        else:
            st.error("Failed to analyze the contract. Please try again.")

    # If we have analysis results, display them and allow user interaction
    if st.session_state.analysis_results is not None:
        data = st.session_state.analysis_results
        segmented_contract = data.get("segmented_contract", {})
        crew_analysis = data.get("crew_analysis", {})

        # Extract the tasks_output from the nested structure
        tasks_output = crew_analysis.get("final_recommendation", {}).get("tasks_output", [])

        clauses_data = []
        for task in tasks_output:
            agent = task.get("agent", "")
            if task.get("pydantic"):
                clause_analysis = task["pydantic"].get("analysis", "")
                recommendation = task["pydantic"].get("recommendation", "")
                
                st.subheader(f"Clause: {agent}")
                st.write("Analysis:")
                st.write(clause_analysis)
                st.write("Recommendation:")
                st.write(recommendation)

                action = st.selectbox(
                    f"Action for {agent}",
                    ["Accept", "Negotiate", "Reject"],
                    key=f"action_{agent}"
                )
                negotiation_points = ""
                if action == "Negotiate":
                    negotiation_points = st.text_area("Enter your negotiation points:", key=f"negotiate_{agent}")
                
                clauses_data.append({
                    "agent": agent,
                    "analysis": clause_analysis,
                    "recommendation": recommendation,
                    "action": action,
                    "negotiation_points": negotiation_points
                })
                
                st.markdown("---")  # Add a separator between clauses

        # Finalize Contract button
        if st.button("Finalize Contract"):
            with st.spinner("Generating response..."):
                response_to_drafter = call_llama_for_response(clauses_data)
            st.subheader("Response to Contract Drafter:")
            st.text_area("", response_to_drafter, height=400)
            st.success("Contract negotiation completed. Response generated for review.")

else:
    st.write("Please upload a contract to begin the analysis.")
