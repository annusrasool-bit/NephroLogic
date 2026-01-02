import streamlit as st
import kdigo_logic as core

st.set_page_config(page_title="NephroLogic AI", page_icon="kidney", layout="wide")

# --- APP HEADER ---
st.title("🏥 NephroLogic: KDIGO Evaluation Engine")
st.markdown("---")

# --- SIDEBAR & SETTINGS ---
with st.sidebar:
    st.header("⚙️ Clinical Settings")
    mode = st.radio("Select Workflow", ["Clinic (Chronic)", "ER (Acute)", "Dialysis Unit"])
    st.info("💡 **Tip:** This tool implements KDIGO 2024 Guidelines for AKI and CKD.")

# --- SHARED PATIENT DATA (Global) ---
st.subheader("📝 Patient Demographics & Vitals")
col1, col2, col3, col4 = st.columns(4)
with col1:
    age = st.number_input("Age", value=55)
    sex = st.selectbox("Sex", ["Male", "Female"])
with col2:
    creatinine = st.number_input("Creatinine (mg/dL)", value=1.2, format="%.2f")
    egfr = st.number_input("eGFR (ml/min)", value=65)
with col3:
    uacr = st.number_input("uACR (mg/g)", value=450, help="Urine Albumin-Creatinine Ratio")
    potassium = st.number_input("Potassium (K+)", value=4.5, format="%.1f")
with col4:
    sbp = st.number_input("Systolic BP", value=138)
    dbp = st.number_input("Diastolic BP", value=85)

# Initialize 'has_ckd' logic for the dictionary (Fixes the KeyError)
has_ckd_logic = True if egfr < 60 or uacr > 30 else False

# --- WORKFLOW 1: CLINIC (CHRONIC) ---
if mode == "Clinic (Chronic)":
    st.header("🛡️ Chronic Kidney Disease Management")
    
    tab1, tab2 = st.tabs(["Clinical Data", "Assessment & Plan"])
    
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Comorbidities")
            has_dm = st.checkbox("Diabetes Mellitus (T2D)")
            has_htn = st.checkbox("Hypertension")
            has_hf = st.checkbox("Heart Failure")
        with c2:
            st.subheader("Current Medications")
            on_ace_arb = st.checkbox("On ACEi or ARB")
            on_sglt2 = st.checkbox("On SGLT2 Inhibitor")
            on_mra = st.checkbox("On ns-MRA (Finerenone)")
            on_statin = st.checkbox("On Statin")

    with tab2:
        # 1. Staging Engine
        g_stage = core.get_g_stage(egfr)
        a_stage = core.get_a_stage(uacr)
        risk_color = core.get_risk_color(g_stage, a_stage)
        
        st.subheader(f"Diagnosis: CKD {g_stage}{a_stage}")
        
        # Visual Risk Display
        if risk_color == "Red":
            st.error(f"🚨 PROGNOSIS: Very High Risk (Red Zone)")
        elif risk_color == "Orange":
            st.warning(f"⚠️ PROGNOSIS: High Risk (Orange Zone)")
        elif risk_color == "Yellow":
            st.warning(f"⚖️ PROGNOSIS: Moderate Risk (Yellow Zone)")
        else:
            st.success(f"✅ PROGNOSIS: Low Risk (Green Zone)")

        # 2. Recommendation Engine
        # Create dictionary for logic
        pt_data = {
            'age': age, 'sex': sex, 'creatinine': creatinine, 'egfr': egfr,
            'uacr': uacr, 'potassium': potassium, 'sbp': sbp, 'dbp': dbp,
            'has_dm': has_dm, 'has_htn': has_htn, 'has_ckd': has_ckd_logic,
            'on_ace_arb': on_ace_arb, 'on_sglt2': on_sglt2, 'on_mra': on_mra,
            'g_stage': g_stage, 'a_stage': a_stage
        }
        
        st.subheader("🤖 AI Management Suggestions")
        recs = core.check_renoprotection(pt_data)
        if recs:
            for r in recs:
                st.info(r)
        else:
            st.success("🌟 Great Job! Current therapy matches KDIGO guidelines.")
            
        # 3. Note Generator
        st.markdown("### 📋 Copy-Paste Clinical Note")
        note = core.generate_note(pt_data, recs, risk_color)
        st.text_area("Select All & Copy", note, height=400)


# --- WORKFLOW 2: ER (ACUTE) ---
elif mode == "ER (Acute)":
    st.header("🚨 Acute Kidney Injury / Emergency")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("The 'AEIOU' Checklist")
        aeiou_a = st.checkbox("A - Acidosis (pH < 7.15)")
        aeiou_e = st.checkbox("E - Electrolytes (Refractory K+)")
        aeiou_i = st.checkbox("I - Intoxications")
        aeiou_o = st.checkbox("O - Overload (Refractory Edema)")
        aeiou_u = st.checkbox("U - Uremia (Pericarditis/Encephalopathy)")
        
        urgent_dialysis = any([aeiou_a, aeiou_e, aeiou_i, aeiou_o, aeiou_u])

    with col_b:
        st.subheader("Urinalysis & Diagnostics")
        urine_sediment = st.selectbox("Urine Sediment", ["Bland", "Muddy Brown Casts (ATN)", "RBC Casts (GN)", "WBC Casts (AIN)"])
        hydronephrosis = st.checkbox("Hydronephrosis on US?")
    
    st.divider()
    if urgent_dialysis:
        st.error("🛑 CRITICAL ACTION: Emergency Dialysis Consultation Indicated (AEIOU met).")
    
    if potassium > 6.0:
        st.error(f"🛑 CRITICAL ACTION: Hyperkalemia ({potassium}). Initiate Medical Management.")

    # ER Note Logic
    st.subheader("📋 Acute Consult Note")
    er_note = f"""
    NEPHROLOGY ACUTE CONSULT
    Reason: AKI / Electrolyte Abnormality
    
    HPI: Patient is {age}yo {sex}.
    Labs: Cr {creatinine} | K+ {potassium}
    
    ASSESSMENT:
    1. Acute Kidney Injury
       - Etiology suspected: {urine_sediment}
       - Obstructive component: {'Yes' if hydronephrosis else 'No'}
    
    2. Indications for RRT (AEIOU):
       {'[x] Met criteria for emergent dialysis' if urgent_dialysis else '[ ] No emergent indications currently'}
    
    PLAN:
    - {'Prepare for HD catheter placement' if urgent_dialysis else '- Monitor urine output and chemistry'}
    - {'Relieve obstruction' if hydronephrosis else '- Fluid management as per volume status'}
    """
    st.text_area("Copy ER Note", er_note, height=300)


# --- WORKFLOW 3: DIALYSIS UNIT ---
elif mode == "Dialysis Unit":
    st.header("🩸 Hemodialysis Rounds")
    
    d1, d2, d3 = st.columns(3)
    with d1:
        st.subheader("Prescription")
        modality = st.selectbox("Modality", ["HD (In-Center)", "PD", "HDF"])
        access = st.selectbox("Access", ["AVF (Left Arm)", "AVF (Right Arm)", "AVG", "Tunneled Catheter"])
    with d2:
        st.subheader("Adequacy")
        spktv = st.number_input("spKt/V", value=1.2)
        urr = st.number_input("URR (%)", value=65)
    with d3:
        st.subheader("Volume")
        edw = st.number_input("Dry Weight (kg)", value=70.0)
        idwg = st.number_input("Weight Gain (kg)", value=2.5)

    # Dialysis Logic
    st.divider()
    if spktv < 1.2:
        st.warning(f"⚠️ Adequacy Alert: spKt/V is {spktv} (Goal > 1.2). Check access flow and treatment time.")
    
    if idwg > 4.0:
        st.warning(f"⚠️ Volume Alert: Large gains ({idwg} kg). Counsel on fluid restriction.")

    st.subheader("📋 Rounds Note")
    dialysis_note = f"""
    HEMODIALYSIS ROUNDS NOTE
    Patient: {age}yo {sex}
    Access: {access}
    
    DATA:
    - Pre-HD K+: {potassium}
    - Adequacy: Kt/V {spktv} | URR {urr}%
    - Volume: IDWG {idwg}kg | Dry Wt {edw}kg
    
    ASSESSMENT & PLAN:
    1. ESRD on {modality}
       - Access is functional.
       - {'Adequacy targets MET.' if spktv >= 1.2 else 'Adequacy NOT met. Plan: Increase blood flow/time.'}
    
    2. Volume Status
       - Target ultrafiltration: {idwg} L
    """
    st.text_area("Copy Rounds Note", dialysis_note, height=300)
