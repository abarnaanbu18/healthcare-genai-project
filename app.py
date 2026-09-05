import streamlit as st

from data import load_patients
from utils import get_diagnosis, ask_followup
from drug_safety import check_prescription_safety
from save_record import save_confirmed_record
from stats_view import show_stats_dashboard
from treatment_recommender import (
    recommend_treatment,
    simulate_outcome_feedback
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="GenAI Doctor View",
    page_icon="🩺",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #f0f8ff;
}


/* ==========================================================
   SIDEBAR
   ========================================================== */

section[data-testid="stSidebar"] {
    background-color: #262936 !important;
}

section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: #ffffff !important;
}


/* ==========================================================
   MAIN HEADINGS
   ========================================================== */

h1 {
    color: #0077b6;
    font-weight: 700;
}

h2,
h3 {
    color: #023e8a;
}


/* ==========================================================
   MAIN TEXT
   ========================================================== */

p,
span,
label,
.stMarkdown {
    color: #1a1a1a;
}


/* ==========================================================
   METRICS
   ========================================================== */

div[data-testid="stMetric"] {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 15px;
    border-left: 4px solid #0077b6;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}


/* ==========================================================
   BUTTONS
   ========================================================== */

.stButton > button {
    background-color: #0077b6;
    color: white !important;
    border-radius: 8px;
    border: none;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #005f8c;
    color: white !important;
}


/* ==========================================================
   TEXT INPUTS
   ========================================================== */

div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {
    background-color: #ffffff;
    color: #1a1a1a;
    border: 1px solid #b3d9ff;
}


/* ==========================================================
   FILE UPLOADER
   ========================================================== */

div[data-testid="stFileUploader"] {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 10px;
}


/* ==========================================================
   CHECKBOX
   ========================================================== */

div[data-testid="stCheckbox"] label {
    color: #1a1a1a !important;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "view" not in st.session_state:
    st.session_state.view = "login"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "selected_patient_id" not in st.session_state:
    st.session_state.selected_patient_id = None

if "diagnosis_result" not in st.session_state:
    st.session_state.diagnosis_result = None


# ============================================================
# LOAD PATIENT DATA
# ============================================================

patients_df = load_patients()


# ============================================================
# LOGIN VIEW
# ============================================================

if st.session_state.view == "login":

    st.markdown(
        """
        <h1>
            🩺 GenAI
            <span style="color:#023e8a; font-weight:400;">
                Doctor Login
            </span>
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.subheader("Clinician Sign In")

    with st.form("login_form"):

        username = st.text_input("Doctor ID")

        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button("Sign In")

        if submitted:

            if (
                username == "doctor"
                and password == "medintel123"
            ):

                st.session_state.authenticated = True
                st.session_state.view = "list"

                st.rerun()

            else:

                st.error(
                    "❌ Invalid credentials. Please try again."
                )

    st.caption(
        "Demo credentials — Doctor ID: doctor | "
        "Password: medintel123"
    )


# ============================================================
# LIST VIEW
# ============================================================

elif st.session_state.view == "list":

    if not st.session_state.authenticated:
        st.session_state.view = "login"
        st.rerun()

    st.markdown(
        """
        <h1>
            🩺 GenAI
            <span style="color:#023e8a; font-weight:400;">
                Doctor View
            </span>
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.subheader("Select a Patient")

    cols = st.columns(4)

    for idx, row in patients_df.iterrows():

        with cols[idx % 4]:

            if st.button(
                f"👤 {row['name']}",
                key=f"patient_{row['patient_id']}"
            ):

                st.session_state.selected_patient_id = (
                    row["patient_id"]
                )

                st.session_state.view = "detail"

                # Clear old diagnosis
                st.session_state.diagnosis_result = None

                st.rerun()


# ============================================================
# DETAIL VIEW
# ============================================================

elif st.session_state.view == "detail":

    # ========================================================
    # BACK BUTTON
    # ========================================================

    if st.button("← Back to Patient List"):

        st.session_state.view = "list"

        st.session_state.selected_patient_id = None

        st.session_state.diagnosis_result = None

        st.rerun()


    # ========================================================
    # SELECTED PATIENT
    # ========================================================

    selected = patients_df[
        patients_df["patient_id"]
        == st.session_state.selected_patient_id
    ].iloc[0]


    # ========================================================
    # SIDEBAR
    # ========================================================

    with st.sidebar:

        st.header("Patient")

        st.markdown(
            f"""
            <h3 style="color:white !important;">
                👤 {selected['name']}
            </h3>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <p style="color:white !important;">
                Age: {selected['age']}
                |
                Gender: {selected['gender']}
            </p>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # VITALS
        # ----------------------------------------------------

        st.subheader("Vitals")

        st.markdown(
            f"""
            <p style="color:white !important;">
                BP: {selected['blood_pressure']}
            </p>

            <p style="color:white !important;">
                Heart Rate: {selected['heart_rate']} bpm
            </p>

            <p style="color:white !important;">
                Temperature: {selected['temperature_f']}°F
            </p>

            <p style="color:white !important;">
                O2 Saturation:
                {selected['oxygen_saturation']}%
            </p>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # ALLERGIES
        # ----------------------------------------------------

        st.subheader("Allergies")

        if selected["allergies"] != "None":

            st.error(
                selected["allergies"]
            )

        else:

            st.success(
                "No known allergies"
            )


        # ----------------------------------------------------
        # CURRENT MEDICATIONS
        # ----------------------------------------------------

        st.subheader("Current Medications")

        st.markdown(
            f"""
            <p style="color:white !important;">
                {selected['current_medications']}
            </p>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # PATIENT TITLE
    # ========================================================

    st.markdown(
        f"""
        <h1>
            🩺 {selected['name']}
        </h1>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # MAIN COLUMNS
    # ========================================================

    col1, col2 = st.columns([2, 1])


    # ========================================================
    # LEFT COLUMN - DIAGNOSIS
    # ========================================================

    with col1:

        st.header("Diagnosis")


        # ----------------------------------------------------
        # CHIEF COMPLAINT
        # ----------------------------------------------------

        complaint = st.text_area(
            "Chief Complaint",
            value=selected[
                "chief_complaint_history"
            ]
        )


        # ----------------------------------------------------
        # X-RAY UPLOAD
        # ----------------------------------------------------

        st.subheader("🩻 X-Ray Image")

        xray_image = st.file_uploader(
            "Upload X-Ray Image",
            type=[
                "png",
                "jpg",
                "jpeg"
            ],
            key=f"xray_{selected['patient_id']}",
            help="Upload an X-ray image for AI-assisted analysis."
        )


        # ----------------------------------------------------
        # X-RAY PREVIEW
        # ----------------------------------------------------

        if xray_image is not None:

            st.success(
                f"X-Ray uploaded: {xray_image.name}"
            )

            st.image(
                xray_image,
                caption="Uploaded X-Ray",
                width="stretch"
            )


        # ----------------------------------------------------
        # CONSENT
        # ----------------------------------------------------

        consent = st.checkbox(
            "Patient consent obtained for AI-assisted diagnosis "
            "(GDPR/HIPAA compliance)"
        )


        # ----------------------------------------------------
        # GET AI SUGGESTION
        # ----------------------------------------------------

        if st.button(
            "Get AI Suggestion",
            disabled=not consent
        ):

            # Remove previous result first
            st.session_state.diagnosis_result = None

            with st.spinner(
                "Analyzing symptoms and cross-referencing "
                "clinical data..."
            ):

                result = get_diagnosis(
                    selected.to_dict(),
                    complaint,
                    xray_image
                )


            # =================================================
            # CHECK AI ERROR
            # =================================================

            if result.get("error"):

                error_type = result.get(
                    "error_type",
                    "OTHER"
                )


                # ------------------------------------------------
                # 503 ERROR
                # ------------------------------------------------

                if error_type == "503":

                    st.warning(
                        "⚠️ Gemini AI is temporarily unavailable. "
                        "The model is currently experiencing high "
                        "demand. Please try again later."
                    )


                # ------------------------------------------------
                # 429 ERROR
                # ------------------------------------------------

                elif error_type == "429":

                    st.error(
                        "🚫 Gemini API quota exceeded. "
                        "Please try again after the quota resets."
                    )


                # ------------------------------------------------
                # OTHER ERROR
                # ------------------------------------------------

                else:

                    st.error(
                        "❌ Gemini AI service is currently "
                        "unavailable. Please try again later."
                    )


            # =================================================
            # SUCCESSFUL AI RESULT
            # =================================================

            else:

                st.session_state.diagnosis_result = result


        # ====================================================
        # DISPLAY DIAGNOSIS RESULT
        # ====================================================

        if st.session_state.diagnosis_result is not None:

            result = st.session_state.diagnosis_result


            # =================================================
            # SAFETY CHECK
            # =================================================

            if not result.get("error"):

                primary = result.get(
                    "primary_diagnosis",
                    {}
                )

                score = primary.get(
                    "confidence_score",
                    0
                )


                # =================================================
                # TABS
                # =================================================

                tab1, tab2, tab3 = st.tabs(
                    [
                        "🩺 Diagnosis",
                        "💊 Treatment",
                        "📋 Safety Notes"
                    ]
                )


                # =================================================
                # TAB 1 - DIAGNOSIS
                # =================================================

                with tab1:

                    # ---------------------------------------------
                    # DEBUG - RAW RESULT
                    # ---------------------------------------------

                    with st.expander(
                        "DEBUG: Raw Result"
                    ):

                        st.json(
                            result
                        )


                    st.subheader(
                        "Primary Diagnosis"
                    )


                    # ---------------------------------------------
                    # CONDITION
                    # ---------------------------------------------

                    st.metric(
                        label=primary.get(
                            "condition",
                            "Unknown"
                        ),
                        value=(
                            f"{score * 100:.0f}% confidence"
                        )
                    )


                    # ---------------------------------------------
                    # PROGRESS
                    # ---------------------------------------------

                    st.progress(
                        min(
                            max(score, 0),
                            1
                        )
                    )


                    # ---------------------------------------------
                    # ICD CODE
                    # ---------------------------------------------

                    st.caption(
                        f"ICD-10: "
                        f"{primary.get('icd_10_code', 'N/A')}"
                    )


                    # ---------------------------------------------
                    # REASONING
                    # ---------------------------------------------

                    st.write(
                        primary.get(
                            "reasoning",
                            ""
                        )
                    )


                    # =================================================
                    # DIFFERENTIAL DIAGNOSES
                    # =================================================

                    with st.expander(
                        "Differential Diagnoses"
                    ):

                        differential = result.get(
                            "differential_diagnoses",
                            []
                        )

                        if differential:

                            for d in differential:

                                dscore = d.get(
                                    "confidence_score",
                                    d.get("confidence")
                                )

                                label = (
                                    f"**{d.get('condition', 'Unknown')}** "
                                    f"({d.get('icd_10_code', 'N/A')})"
                                )

                                if dscore is not None:

                                    label += (
                                        f" — "
                                        f"{dscore * 100:.0f}%"
                                    )

                                st.write(label)

                                if d.get("reasoning"):

                                    st.caption(
                                        d["reasoning"]
                                    )

                        else:

                            st.caption(
                                "No differential diagnoses available."
                            )


                    # =================================================
                    # FOLLOW-UP TESTS
                    # =================================================

                    with st.expander(
                        "Recommended Follow-up Tests"
                    ):

                        tests = result.get(
                            "follow_up_tests",
                            []
                        )

                        if tests:

                            for test in tests:

                                st.write(
                                    f"- {test}"
                                )

                        else:

                            st.caption(
                                "No follow-up tests suggested."
                            )


                # =================================================
                # TAB 2 - TREATMENT
                # =================================================

                with tab2:

                    treatment = recommend_treatment(
                        selected.get(
                            "department",
                            "General Medicine"
                        ),
                        selected.get(
                            "age_group",
                            "31-45"
                        )
                    )


                    if treatment:

                        st.info(
                            f"**Recommended:** "
                            f"{treatment['recommended_treatment']}"
                        )


                        st.caption(
                            f"Based on "
                            f"{treatment['based_on_cases']} "
                            f"similar cases — "
                            f"Avg recovery score: "
                            f"{treatment['avg_recovery_score']}, "
                            f"Avg readmission risk: "
                            f"{treatment['avg_readmission_risk']}"
                        )


                        # -----------------------------------------
                        # ALL TREATMENT OPTIONS
                        # -----------------------------------------

                        with st.expander(
                            "All Treatment Options Compared"
                        ):

                            for opt in treatment[
                                "all_options"
                            ]:

                                st.write(
                                    f"- "
                                    f"**{opt['treatment_type']}**: "
                                    f"recovery "
                                    f"{opt['avg_recovery_score']:.1f}, "
                                    f"readmission risk "
                                    f"{opt['avg_readmission_risk']:.2f} "
                                    f"({opt['case_count']} cases)"
                                )


                        st.markdown("---")


                        # -----------------------------------------
                        # OUTCOME FEEDBACK
                        # -----------------------------------------

                        st.subheader(
                            "Simulated Outcome Feedback"
                        )


                        outcome = simulate_outcome_feedback(
                            selected.get(
                                "department",
                                "General Medicine"
                            ),
                            selected.get(
                                "age_group",
                                "31-45"
                            ),
                            treatment[
                                "recommended_treatment"
                            ]
                        )


                        if outcome:

                            st.metric(
                                "Predicted Recovery Score",
                                f"{outcome['predicted_recovery']}/100"
                            )

                            st.caption(
                                outcome[
                                    "confidence_note"
                                ]
                            )

                        else:

                            st.caption(
                                "Insufficient data for outcome "
                                "prediction."
                            )


                    else:

                        st.caption(
                            "No historical treatment data "
                            "available for this department/"
                            "age group."
                        )


                # =================================================
                # TAB 3 - SAFETY NOTES
                # =================================================

                with tab3:

                    clinical_notes = result.get(
                        "clinical_notes",
                        []
                    )


                    if clinical_notes:

                        for note in clinical_notes:

                            st.warning(
                                note
                            )

                    else:

                        st.caption(
                            "No safety notes flagged."
                        )


    # ========================================================
    # RIGHT COLUMN - PRESCRIPTION
    # ========================================================

    with col2:

        st.header("Prescription")


        # ----------------------------------------------------
        # MEDICATION INPUT
        # ----------------------------------------------------

        prescription = st.text_input(
            "Prescribe medication"
        )


        # ----------------------------------------------------
        # CHECK SAFETY
        # ----------------------------------------------------

        if st.button(
            "Check Safety"
        ):

            warnings = check_prescription_safety(
                prescription,
                selected.to_dict()
            )


            if warnings:

                for w in warnings:

                    severity = w.get(
                        "severity",
                        "info"
                    )


                    if severity == "critical":

                        st.error(
                            f"🔴 CRITICAL: "
                            f"{w['message']}"
                        )


                    elif severity == "warning":

                        st.warning(
                            f"🟡 WARNING: "
                            f"{w['message']}"
                        )


                    else:

                        st.info(
                            f"🔵 INFO: "
                            f"{w['message']}"
                        )


            else:

                st.success(
                    "✅ No conflicts detected"
                )


        # ----------------------------------------------------
        # CONFIRM & SAVE
        # ----------------------------------------------------

        if st.button(
            "Confirm & Save"
        ):

            diagnosis_summary = None


            if st.session_state.diagnosis_result:

                diagnosis_summary = (
                    st.session_state
                    .diagnosis_result
                    .get(
                        "primary_diagnosis"
                    )
                )


            saved = save_confirmed_record(
                patient_id=selected[
                    "patient_id"
                ],

                patient_name=selected[
                    "name"
                ],

                diagnosis=diagnosis_summary,

                prescription=prescription
            )


            st.success(
                f"Saved record for "
                f"{selected['name']} "
                f"at {saved['timestamp']}"
            )


        # ----------------------------------------------------
        # AI ASSISTANT (goes to dedicated page)
        # ----------------------------------------------------

        st.markdown("---")

        if "prescription_chat" not in st.session_state:
            st.session_state.prescription_chat = []

        if st.button(
            "🤖 Ask AI Assistant",
            use_container_width=True
        ):
            st.session_state.view = "chat"
            st.rerun()


    # ========================================================
    # SYSTEM STATISTICS
    # ========================================================

    st.markdown("---")

    st.header(
        "📊 System Statistics"
    )

    show_stats_dashboard()


# ============================================================
# CHAT VIEW (AI ASSISTANT FULL PAGE)
# ============================================================

elif st.session_state.view == "chat":

    # ========================================================
    # BACK BUTTON
    # ========================================================

    if st.button("← Back to Patient"):

        st.session_state.view = "detail"

        st.rerun()


    # ========================================================
    # SELECTED PATIENT
    # ========================================================

    selected = patients_df[
        patients_df["patient_id"]
        == st.session_state.selected_patient_id
    ].iloc[0]


    # ========================================================
    # PAGE TITLE
    # ========================================================

    st.markdown(
        f"""
        <h1>
            🤖 AI Assistant
            <span style="color:#023e8a; font-weight:400;">
                — {selected['name']}
            </span>
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "Ask follow-up questions about this patient's diagnosis, "
        "treatment, or prescription."
    )


    # ========================================================
    # CHAT HISTORY
    # ========================================================

    if "prescription_chat" not in st.session_state:
        st.session_state.prescription_chat = []

    for msg in st.session_state.prescription_chat:

        if msg["role"] == "doctor":

            st.chat_message("user").markdown(
                msg["text"]
            )

        else:

            st.chat_message("assistant").markdown(
                msg["text"]
            )


    # ========================================================
    # CHAT INPUT
    # ========================================================

    doubt = st.chat_input(
        "Ask your doubt about this patient's case"
    )

    if doubt:

        diagnosis_ctx = None

        if st.session_state.diagnosis_result:

            diagnosis_ctx = (
                st.session_state
                .diagnosis_result
                .get("primary_diagnosis")
            )

        st.session_state.prescription_chat.append(
            {"role": "doctor", "text": doubt}
        )

        with st.spinner("Thinking..."):

            answer = ask_followup(
                selected.to_dict(),
                diagnosis_ctx,
                st.session_state.prescription_chat,
                doubt
            )

        st.session_state.prescription_chat.append(
            {"role": "ai", "text": answer}
        )

        st.rerun()