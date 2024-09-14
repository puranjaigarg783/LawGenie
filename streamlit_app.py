import streamlit as st
import requests

st.title('Contract Negotiation Assistant')

uploaded_file = st.file_uploader("Upload Contract", type=["pdf", "docx"])

if uploaded_file is not None:
    files = {'file': uploaded_file}
    response = requests.post("http://localhost:5000/upload", files=files)
    
    if response.status_code == 200:
        contract_text = response.json()['text']
        st.write("Contract uploaded successfully. Analyzing...")
        
        analysis_response = requests.post("http://localhost:5000/analyze", json={"text": contract_text})
        if analysis_response.status_code == 200:
            analysis = analysis_response.json()['analysis']
            
            for i, clause_analysis in enumerate(analysis):
                st.subheader(f"Clause {i+1}")
                st.write(clause_analysis['clause'])
                st.write("Analysis:")
                for issue in clause_analysis['analysis']:
                    st.write(f"- {issue}")
                
                recommend_response = requests.post("http://localhost:5000/recommend", json={"clause": clause_analysis['clause'], "analysis": clause_analysis['analysis']})
                if recommend_response.status_code == 200:
                    recommendations = recommend_response.json()['recommendations']
                    st.write("Recommendations:")
                    for rec in recommendations:
                        st.write(f"- {rec}")
                
                action = st.selectbox(f"Action for Clause {i+1}", ["Accept", "Negotiate", "Reject"], key=f"action_{i}")
                if action == "Negotiate":
                    st.text_area("Enter your negotiation points:", key=f"negotiate_{i}")
        else:
            st.error("Error analyzing the contract.")
    else:
        st.error("Error uploading the contract.")

if st.button("Finalize Contract"):
    st.success("Contract negotiation completed. Final version ready for review.")
