import requests
import streamlit as st

st.title("Contract Negotiation Assistant")

uploaded_file = st.file_uploader("Upload Contract", type=["pdf", "docx"])

if uploaded_file is not None:
    files = {"file": uploaded_file}
    response = requests.post("http://localhost:5002/upload", files=files)

    if response.status_code == 200:
        st.write("Contract uploaded successfully. Analyzing...")
        
        # Assuming the response contains the structure you provided
        data = response.json()
        crew_analysis = data.get("crew_analysis", {})
        final_recommendation = crew_analysis.get("final_recommendation", {})
        tasks_output = final_recommendation.get("tasks_output", [])

        for task in tasks_output:
            agent = task.get("agent", "")
            if task.get("pydantic"):
                analysis = task["pydantic"].get("analysis", "")
                recommendation = task["pydantic"].get("recommendation", "")
                
                st.subheader(f"Clause: {agent}")
                st.write("Analysis:")
                st.write(analysis)
                st.write("Recommendation:")
                st.write(recommendation)

                action = st.selectbox(
                    f"Action for {agent}",
                    ["Accept", "Negotiate", "Reject"],
                    key=f"action_{agent}"
                )
                if action == "Negotiate":
                    st.text_area("Enter your negotiation points:", key=f"negotiate_{agent}")
                
                st.markdown("---")  # Add a separator between clauses

if st.button("Finalize Contract"):
    st.success("Contract negotiation completed. Final version ready for review.")
