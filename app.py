import streamlit as st
from weasyprint import HTML
import base64
import tempfile
import os

# Set initial_sidebar_state to collapsed for maximum mobile screen space
st.set_page_config(page_title="AHA PDF Generator", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1, h2, h3, label { color: #00ffff !important; }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea { 
        background-color: #0a0a0a; 
        color: #00ffff; 
        border: 1px solid #8a2be2; 
        caret-color: #00ffff;
    }
    
    /* Standard Generate Button */
    .stButton > button { 
        background-color: #32cd32; 
        color: #000000; 
        font-weight: bold; 
        border: none; 
        width: 100%;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .stButton > button:hover { background-color: #00ffff; color: #000000; box-shadow: 0 0 10px #00ffff; }
    
    /* Fix for Download Button */
    .stDownloadButton > button {
        background-color: #00ffff;
        color: #000000;
        font-weight: bold;
        border: none;
        width: 100%;
        text-transform: uppercase;
        margin-top: 10px;
    }
    .stDownloadButton > button:hover {
        background-color: #8a2be2;
        color: #ffffff;
        box-shadow: 0 0 10px #8a2be2;
    }
    
    /* Custom styling for the Add button */
    div[data-testid="stVerticalBlock"] div:has(> button.step-up) button {
        background-color: #8a2be2;
        color: #ffffff;
    }
    div[data-testid="stVerticalBlock"] div:has(> button.step-up) button:hover {
        background-color: #00ffff;
        color: #000000;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ AHA Workout Generator")

client_title = st.text_input("Client Name & Date / Session (e.g., AR - SESSION 71)")
custom_filename = st.text_input("Custom PDF File Name (Optional - leave blank to use Client Name)")

st.markdown("### Workout Sections")
st.caption("Leave title or content blank to skip a section.")

# Initialize dynamic sections in session state
if 'num_sections' not in st.session_state:
    st.session_state.num_sections = 6

defaults = [
    "WARM-UP", 
    "MOBILITY & ACTIVATION (10 REPS x 1 SET)", 
    "DYNAMIC WARM UP", 
    "STRENGTH CIRCUIT ONE", 
    "STRENGTH CIRCUIT TWO",
    "FINISHER / CONDITIONING"
]

sections_data = []

# Mobile-Friendly Vertical Layout
for i in range(st.session_state.num_sections):
    st.markdown(f"<div style='color: #8a2be2; font-weight: bold; margin-top: 15px; font-size: 14px;'>SECTION {i+1}</div>", unsafe_allow_html=True)
    
    default_title = defaults[i] if i < len(defaults) else ""
    
    # Hidden labels with placeholders to save vertical screen space on mobile
    sec_title = st.text_input(f"Title {i+1}", value=default_title, key=f"title_{i}", placeholder=f"Section {i+1} Title (e.g., WARM-UP)", label_visibility="collapsed")
    sec_content = st.text_area(f"Content {i+1}", key=f"content_{i}", height=80, placeholder="Paste exercises here...", label_visibility="collapsed")
    
    sections_data.append((sec_title, sec_content))

# Add Section Button
st.markdown('<div class="step-up">', unsafe_allow_html=True)
if st.button("➕ ADD ANOTHER SECTION", key="add_section_btn"):
    st.session_state.num_sections += 1
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr style='border-color: #8a2be2;'>", unsafe_allow_html=True)

def format_list(text_block):
    if not text_block.strip(): return ""
    items = [line.strip().lstrip('•').strip() for line in text_block.replace(',', '\n').split('\n') if line.strip()]
    return "".join([f'<div class="list-item">&bull; {item}</div>' for item in items])

# Generate PDF Logic
if st.button("🚀 GENERATE PDF"):
    if not client_title:
        st.error("Please enter a Client Name/Session.")
    else:
        with st.spinner("Compiling document..."):
            
            # Look for static logo in the project folder
            img_tag = '<div style="color:red; text-align:center;">Logo missing. Please add logo.png to project folder.</div>'
            logo_paths = ["logo.png", "logo.jpg", "logo.jpeg"]
            for path in logo_paths:
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        encoded_string = base64.b64encode(f.read()).decode()
                    mime = "image/png" if path.endswith('.png') else "image/jpeg"
                    img_tag = f'<img src="data:{mime};base64,{encoded_string}" style="height: 200px; width: auto; display: block; margin: 0 auto;">'
                    break

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            <style>
                @page {{ size: A4; margin: 20mm 25mm; background-color: #ffffff; }}
                body {{
                    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                    font-size: 10pt; color: #000000; line-height: 1.4; margin: 0; padding: 0;
                    text-transform: uppercase;
                }}
                .logo-container {{ text-align: center; margin-bottom: 25px; }}
                .main-title {{
                    text-align: center; color: #1f4e79; font-size: 14pt; font-weight: bold;
                    margin-bottom: 30px; letter-spacing: 0.5px;
                }}
                .section-title {{
                    color: #1f4e79; font-weight: bold; font-size: 11pt; margin-top: 25px; margin-bottom: 8px; 
                }}
                .list-item {{ margin-bottom: 3px; font-size: 10pt; color: #000000; }}
            </style>
            </head>
            <body>
                <div class="logo-container">{img_tag}</div>
                <div class="main-title">{client_title}</div>
            """
            
            # Only append sections that have both a title and content
            for sec_title, sec_content in sections_data:
                if sec_title.strip() and sec_content.strip():
                    html_content += f'<div class="section-title">{sec_title}</div>\n'
                    html_content += format_list(sec_content)

            html_content += "</body></html>"

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                HTML(string=html_content).write_pdf(tmp_pdf.name)
                with open(tmp_pdf.name, "rb") as f:
                    pdf_bytes = f.read()
            
            # Determine the download filename
            if custom_filename.strip():
                download_name = custom_filename.strip()
                if not download_name.lower().endswith('.pdf'):
                    download_name += ".pdf"
            else:
                download_name = f"{client_title.replace(' ', '_')}.pdf"

            st.success("PDF Generated Successfully!")
            st.download_button(label="⬇️ DOWNLOAD PDF", data=pdf_bytes, file_name=download_name, mime="application/pdf")
            os.remove(tmp_pdf.name)
