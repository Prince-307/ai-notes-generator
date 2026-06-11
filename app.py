import streamlit as st
import requests

# Set page layout and Title
st.set_page_config(page_title="AI Notes Summarizer", layout="wide")
st.title("📚 AI Notes Summarizer & Study Guide Generator")
st.write("Upload your lecture PDFs to instantly receive summaries, key takeaways, and flashcard quizzes!")

# Backend API base URL
BACKEND_URL = "http://127.0.0.1:8000"

# Initialize application Session States to store data across user interaction clicks
if "summary_data" not in st.session_state:
    st.session_state.summary_data = None
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None

# Sidebar Upload Controls
st.sidebar.header("Upload Center")
uploaded_file = st.sidebar.file_uploader("Choose a lecture note PDF", type=["pdf"])

if uploaded_file is not None:
    if st.sidebar.button("✨ Generate Study Materials"):
        # Reset any stored quiz selections in session state
        for key in list(st.session_state.keys()):
            if key.startswith("q_"):
                del st.session_state[key]

        with st.spinner("Processing PDF and analyzing core concepts..."):
            # Prepare file payload for backend multipart form request
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            
            # Step 1: Request Summary from FastAPI backend
            response = requests.post(f"{BACKEND_URL}/process-pdf", files=files)
            
            if response.status_code == 200:
                st.session_state.summary_data = response.json()
                
                # Step 2: Request Quiz Generation automatically using the summary data
                quiz_response = requests.post(
                    f"{BACKEND_URL}/generate-quiz", 
                    json=st.session_state.summary_data
                )
                if quiz_response.status_code == 200:
                    st.session_state.quiz_data = quiz_response.json()
                st.sidebar.success("Analysis Complete!")
            else:
                try:
                    error_detail = response.json().get("detail", "Unknown error")
                except Exception:
                    error_detail = response.text
                st.sidebar.error(f"Failed to process the document: {error_detail}")

# Main Dashboard Layout splits screen into two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Notes Summary & Takeaways")
    if st.session_state.summary_data:
        # Display Summary
        st.subheader("Summary")
        st.markdown(st.session_state.summary_data["summary"])
        
        # Display Bullet Pointed Takeaways
        st.subheader("💡 Key Takeaways")
        for takeaway in st.session_state.summary_data["key_takeaways"]:
            st.markdown(f"- {takeaway}")
            
        # Downloadable Study Guide compilation feature
        study_guide_text = f"SUMMARY:\n{st.session_state.summary_data['summary']}\n\nKEY TAKEAWAYS:\n"
        for t in st.session_state.summary_data["key_takeaways"]:
            study_guide_text += f"- {t}\n"
            
        st.download_button(
            label="📥 Download Study Guide (.txt)",
            data=study_guide_text,
            file_name="ai_study_guide.txt",
            mime="text/plain"
        )
    else:
        st.info("Upload a document and press 'Generate' to see summaries.")

with col2:
    st.header("🧠 Interactive Assessment Quiz")
    if st.session_state.quiz_data:
        # Loop through questions parsed from JSON backend response
        for idx, item in enumerate(st.session_state.quiz_data["quiz"]):
            st.markdown(f"**Q{idx+1}: {item['question']}**")
            
            # Interactive Streamlit Radio button for option picking (unselected by default)
            user_choice = st.radio(
                f"Select an answer for Q{idx+1}:", 
                options=item["options"], 
                index=None,
                key=f"q_{idx}"
            )
            
            # Instantly validate user input responses
            if st.button(f"Check Answer for Q{idx+1}", key=f"btn_{idx}"):
                if user_choice is None:
                    st.warning("⚠️ Please select an option first!")
                elif user_choice == item["correct_answer"]:
                    st.success("🎉 Correct!")
                else:
                    st.error(f"❌ Incorrect. The right answer is: {item['correct_answer']}")
            st.write("---")
    else:
        st.info("Your interactive quiz questions will show up here.")