import os
import streamlit as st
from fpdf import FPDF

# Set initial_sidebar_state to collapsed for maximum mobile screen space
st.set_page_config(
    page_title="AHA PDF Generator",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

st.title("⚡ AHA Workout Generator")

client_title = st.text_input(
    "Client Name & Date / Session (e.g., AR - SESSION 71)"
)
custom_filename = st.text_input(
    "Custom PDF File Name (Optional - leave blank to use Client Name)"
)

st.markdown("### Workout Sections")
st.caption("Leave title or content blank to skip a section.")

# Initialize dynamic sections in session state
if "num_sections" not in st.session_state:
    st.session_state.num_sections = 6

defaults = [
    "WARM-UP",
    "MOBILITY & ACTIVATION (10 REPS x 1 SET)",
    "DYNAMIC WARM UP",
    "STRENGTH CIRCUIT ONE",
    "STRENGTH CIRCUIT TWO",
    "FINISHER / CONDITIONING",
]

sections_data = []

# Mobile-Friendly Vertical Layout
for i in range(st.session_state.num_sections):
    st.markdown(
        f"<div style='color: #8a2be2; font-weight: bold; margin-top: 15px; font-size: 14px;'>SECTION {i+1}</div>",
        unsafe_allow_html=True,
    )

    default_title = defaults[i] if i < len(defaults) else ""

    sec_title = st.text_input(
        f"Title {i+1}",
        value=default_title,
        key=f"title_{i}",
        placeholder=f"Section {i+1} Title (e.g., WARM-UP)",
        label_visibility="collapsed",
    )
    sec_content = st.text_area(
        f"Content {i+1}",
        key=f"content_{i}",
        height=80,
        placeholder="Paste exercises here...",
        label_visibility="collapsed",
    )

    sections_data.append((sec_title, sec_content))

# Add Section Button
st.markdown('<div class="step-up">', unsafe_allow_html=True)
if st.button("➕ ADD ANOTHER SECTION", key="add_section_btn"):
    st.session_state.num_sections += 1
    st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr style='border-color: #8a2be2;'>", unsafe_allow_html=True)


# Pure Python PDF Builder using FPDF2
class WorkoutPDF(FPDF):

    def __init__(self, logo_path=None):
        super().__init__(format="A4", unit="mm")
        self.logo_path = logo_path
        self.set_margins(25, 20, 25)
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.logo_path and os.path.exists(self.logo_path):
            logo_w = 45  # Width in mm
            x_pos = (210 - logo_w) / 2  # Center on A4 page
            self.image(self.logo_path, x=x_pos, y=15, w=logo_w)
            self.ln(35)
        else:
            self.ln(10)


if st.button("🚀 GENERATE PDF"):
    if not client_title:
        st.error("Please enter a Client Name/Session.")
    else:
        with st.spinner("Compiling document..."):
            # Check for logo
            found_logo = None
            for path in ["logo.png", "logo.jpg", "logo.jpeg"]:
                if os.path.exists(path):
                    found_logo = path
                    break

            pdf = WorkoutPDF(logo_path=found_logo)
            pdf.add_page()

            # Main Header Title
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(31, 78, 121)  # #1f4e79
            pdf.cell(
                0,
                10,
                txt=client_title.upper(),
                border=False,
                align="C",
                new_x="LMARGIN",
                new_y="NEXT",
            )
            pdf.ln(6)

            # Render Sections
            for sec_title, sec_content in sections_data:
                if sec_title.strip() and sec_content.strip():
                    # Section Title
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.set_text_color(31, 78, 121)
                    pdf.cell(
                        0,
                        8,
                        txt=sec_title.strip().upper(),
                        border=False,
                        new_x="LMARGIN",
                        new_y="NEXT",
                    )

                    # List Items
                    pdf.set_font("Helvetica", "", 10)
                    pdf.set_text_color(0, 0, 0)

                    items = [
                        line.strip().lstrip("•").strip()
                        for line in sec_content.replace(",", "\n").split("\n")
                        if line.strip()
                    ]
                    for item in items:
                        pdf.multi_cell(
                            0,
                            5,
                            txt=f"- {item.upper()}",
                            new_x="LMARGIN",
                            new_y="NEXT",
                        )

                    pdf.ln(4)

            # Output PDF bytes
            pdf_bytes = bytes(pdf.output())

            # Determine Download Filename
            if custom_filename.strip():
                download_name = custom_filename.strip()
                if not download_name.lower().endswith(".pdf"):
                    download_name += ".pdf"
            else:
                download_name = f"{client_title.replace(' ', '_')}.pdf"

            st.success("PDF Generated Successfully!")
            st.download_button(
                label="⬇️ DOWNLOAD PDF",
                data=pdf_bytes,
                file_name=download_name,
                mime="application/pdf",
            )
