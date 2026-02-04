import streamlit as st
import json
import os
import logging
from dotenv import load_dotenv
from PIL import Image
import tempfile
import io

# Import Agents
from agents.ocr_agent import extract_text
from agents.matcher_agent import match_answer_to_question
from agents.grading_agent import grade_answer
from agents.report_agent import generate_report

# Import Utils
from utils.pdf_utils import pdf_to_images, extract_pdf_text

# Load env vars
load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="MCP Answer Sheet Evaluator", layout="wide")

st.title("📝 MCP Answer Sheet Evaluator")
st.markdown("Use this interface to debug and visualize the multi-agent specific evaluation pipeline.")

# Sidebar for Config / Instructions
st.sidebar.header("Configuration")
if not os.getenv("HF_TOKEN"):
    st.sidebar.error("HF_TOKEN is missing! Please set it in .env or environment variables.")
else:
    st.sidebar.success("HF_TOKEN is set.")

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Workflow:**
1. **Upload** Answer Sheet (PDF/Image)
2. **Upload/Paste** Question Paper (PDF/Text)
3. **Upload/Paste** Solution Key (PDF/Text/JSON)
4. **Evaluate**
""")

# --- Input Section ---
col1, col2 = st.columns([1, 1])

# Helper to save uploaded file to temp
def save_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return None
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        return tmp.name

with col1:
    st.subheader("1. Answer Sheet")
    uploaded_answer_sheet = st.file_uploader("Upload Answer Sheet (PDF/Image)", type=["jpg", "png", "jpeg", "pdf"])
    
    answer_sheet_images = []
    
    if uploaded_answer_sheet:
        file_path = save_uploaded_file(uploaded_answer_sheet)
        if file_path.endswith(".pdf"):
            with st.spinner("Converting PDF to images..."):
                answer_sheet_images = pdf_to_images(file_path)
            st.success(f"Loaded {len(answer_sheet_images)} pages.")
        else:
            image = Image.open(file_path)
            answer_sheet_images = [image]
            
        # Display first page preview
        if answer_sheet_images:
            st.image(answer_sheet_images[0], caption="Preview (Page 1)", use_column_width=True)

with col2:
    st.subheader("2. Question Paper & Key")
    
    # QP
    qp_tab1, qp_tab2 = st.tabs(["Upload PDF", "Paste Text"])
    question_paper_text = ""
    with qp_tab1:
        uploaded_qp = st.file_uploader("Upload Question Paper (PDF)", type=["pdf"])
        if uploaded_qp:
            qp_path = save_uploaded_file(uploaded_qp)
            question_paper_text = extract_pdf_text(qp_path)
            st.info(f"Extracted {len(question_paper_text)} characters.")
    with qp_tab2:
        qp_text_input = st.text_area("Question Paper Text", height=150, placeholder="Q1. Define Force...")
        if not question_paper_text:
            question_paper_text = qp_text_input

    # Key
    key_tab1, key_tab2 = st.tabs(["Upload PDF", "Paste Text/JSON"])
    solution_key_text = ""
    with key_tab1:
        uploaded_key = st.file_uploader("Upload Solution Key (PDF)", type=["pdf"])
        if uploaded_key:
            key_path = save_uploaded_file(uploaded_key)
            solution_key_text = extract_pdf_text(key_path)
            st.info(f"Extracted {len(solution_key_text)} characters.")
    with key_tab2:
        key_text_input = st.text_area("Solution Key", height=150, placeholder='{"1": {"text": "...", "marks": 5}}')
        if not solution_key_text:
            solution_key_text = key_text_input

# --- Evaluation Section ---
if st.button("🚀 Run Evaluation", type="primary"):
    if not answer_sheet_images:
        st.error("Please upload an answer sheet.")
    elif not question_paper_text.strip():
        st.error("Please provide the Question Paper text.")
    else:
        st.markdown("---")
        st.header("🔍 Evaluation Progress")
        
        # 1. OCR Step
        st.subheader("Step 1: OCR (Vision Agent)")
        full_student_text = ""
        
        progress_bar = st.progress(0)
        
        for idx, img in enumerate(answer_sheet_images):
            st.write(f"Processing Page {idx + 1}/{len(answer_sheet_images)}...")
            try:
                # Save current image frame to temp for OCR agent
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
                    img.save(tmp_img.name)
                    tmp_img_path = tmp_img.name
                
                page_text = extract_text(tmp_img_path)
                
                if page_text != "ILLEGIBLE":
                    full_student_text += f"\n--- Page {idx+1} ---\n{page_text}"
                else:
                    st.warning(f"Page {idx+1} was illegible.")
                    
            except Exception as e:
                st.error(f"Error on Page {idx+1}: {e}")
            
            progress_bar.progress((idx + 1) / len(answer_sheet_images))
            
        with st.expander("View Full OCR Output", expanded=True):
            st.code(full_student_text, language="text")

        # 2. Matching Step
        st.subheader("Step 2: Matching (Reasoning Agent)")
        # Note: In a real system, we might split the full text by "Q" or numbered list before matching.
        # For V1, we pass the full text and ask Matcher to identify the *primary* question(s) or we could prompt it to list all.
        # Since our Matcher currently returns a single JSON object (one question), this V1 Logic assumes 
        # the answer sheet corresponds to ONE identifiable question or we just match the first one found.
        # To improve, we should ask the Matcher to return a LIST of matches.
        
        # Let's simple-loop it: We can try to match the whole text. 
        # If the student answered multiple questions, the current matcher prompt might get confused or just return one.
        # For this demo, let's assume it finds the best match.
        
        with st.spinner("Matching answer to question..."):
            try:
                match_result = match_answer_to_question(full_student_text, question_paper_text)
                
                col_m1, col_m2 = st.columns(2)
                col_m1.info(f"**Matched Question ID:** {match_result.get('question_number')}")
                col_m2.text(f"Matched Text: {match_result.get('question_text', '')}")
                
            except Exception as e:
                st.error(f"Matching Error: {e}")
                st.stop()
                
        # 3. Grading Step
        st.subheader("Step 3: Grading (Reasoning Agent)")
        if match_result.get("question_number") != "UNIDENTIFIED":
            with st.spinner("Grading answer..."):
                try:
                    # Parse solution key for specific Q
                    q_id = match_result.get("question_number")
                    max_marks = 10 # Default
                    sol_text_q = solution_key_text
                    
                    # Try simple JSON parsing
                    try:
                        sol_json = json.loads(solution_key_text)
                        if str(q_id) in sol_json: # Handle string/int key diffs
                            sol_text_q = sol_json[str(q_id)].get("text", solution_key_text)
                            max_marks = sol_json[str(q_id)].get("marks", 10)
                        elif q_id in sol_json:
                             sol_text_q = sol_json[q_id].get("text", solution_key_text)
                             max_marks = sol_json[q_id].get("marks", 10)
                    except:
                        pass # Treat as plain text
                    
                    grading_result = grade_answer(full_student_text, sol_text_q, max_marks)
                    
                    st.markdown(f"**Score:** `{grading_result.get('marks_awarded')} / {max_marks}`")
                    st.info(f"**Feedback:** {grading_result.get('feedback')}")
                    
                except Exception as e:
                    st.error(f"Grading Error: {e}")
        else:
            st.write("Skipping grading for unidentified question.")

        # 4. Report Step
        st.subheader("Step 4: Final Report")
        
        # Construct report item
        marks = grading_result.get("marks_awarded", 0) if 'grading_result' in locals() else 0
        fdback = grading_result.get("feedback", "") if 'grading_result' in locals() else "N/A"
        maxim = max_marks if 'max_marks' in locals() else 0
        
        graded_items = [{
            "question_number": match_result.get("question_number"),
            "question_text": match_result.get("question_text"),
            "student_answer": full_student_text[:500] + "..." if len(full_student_text) > 500 else full_student_text,
            "marks_awarded": marks,
            "max_marks": maxim,
            "feedback": fdback
        }]
        
        report = generate_report(graded_items)
        st.json(report)
