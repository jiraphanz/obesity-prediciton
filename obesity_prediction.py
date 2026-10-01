import base64
import streamlit as st
import joblib
import pandas as pd
import os

st.set_page_config(page_title="Obesity Management System", layout="wide")

def yes_no(x):
    if x == "yes":
        return "ใช่"
    if x == "no":
        return "ไม่ใช่"

def caec_label(x):
    if x == "no":
        return "ไม่กิน"
    elif x == "Sometimes":
        return "บางครั้ง"
    elif x == "Frequently":
        return "บ่อย"
    elif x == "Always":
        return "เป็นประจำ"

def calc_label(x):
    if x == "no":
        return "ไม่ดื่ม"
    elif x == "Sometimes":
        return "บางครั้ง"
    elif x == "Frequently":
        return "บ่อย"
    elif x == "Always":
        return "เป็นประจำ"

def mtrans_label(x):
    if x == "Public_Transportation":
        return "ขนส่งสาธารณะ"
    elif x == "Automobile":
        return "รถยนต์"
    elif x == "Walking":
        return "เดิน"
    elif x == "Motorbike":
        return "มอเตอร์ไซค์"
    elif x == "Bike":
        return "จักรยาน"

st.title("Obesity Prediction System")
st.write("ระบบประเมินภาวะอ้วนและแนะนำการออกกำลังกาย")
st.divider()

with st.form("prediction_form"):
    st.subheader("ข้อมูลส่วนบุคคล")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        age = st.number_input("อายุ", min_value=14, max_value=100, value=20, step=1)
    with col2:
        gender = st.selectbox("เพศ", ["Male", "Female"])
    with col3:
        family_history = st.selectbox("ประวัติคนในครอบครัวมีภาวะน้ำหนักเกินหรือโรคอ้วน", ["yes", "no"], format_func=yes_no, help="ใช่ = มีประวัติคนในครอบครัวมีภาวะน้ำหนักเกิน, ไม่ใช่ = ไม่มีประวัติดังกล่าว")

    col1, col2 = st.columns(2)
    with col1:
        height = st.number_input("ส่วนสูง (เมตร)", min_value=1.0, max_value=2.5, value=1.65, step=0.01, format="%.2f")
    with col2:
        weight = st.number_input("น้ำหนัก (กิโลกรัม)", min_value=20.0, max_value=250.0, value=55.0, step=0.1, format="%.1f")

    st.subheader("พฤติกรรมการรับประทานอาหาร")
    col1, col2, col3 = st.columns(3)
    with col1:
        favc = st.selectbox("การรับประทานอาหารแคลอรีสูงเป็นประจำ (FAVC)", ["yes", "no"], format_func=yes_no)
        st.caption("วัดจากพฤติกรรมการรับประทานอาหารที่มีแคลอรีสูง เช่น อาหารทอด ของหวาน")
    with col2:
        fcvc = st.number_input("การรับประทานผัก (FCVC)", min_value=1.0, max_value=3.0, value=1.0, step=0.1, help="ค่าประมาณจากความถี่ในการรับประทานผัก: 1 = แทบไม่รับประทาน, 2 = รับประทานบางครั้ง, 3 = รับประทานเป็นประจำ/เกือบทุกมื้อ")
    with col3:
        ncp = st.number_input("จำนวนมื้ออาหารหลักต่อวัน (NCP)", min_value=1.0, max_value=4.0, value=1.0, step=0.1, help="จำนวนมื้ออาหารหลักต่อวัน: 1 = 1 มื้อ, 2 = 2 มื้อ, 3 = 3 มื้อ, 4 = มากกว่า 3 มื้อ")

    col1, col2 = st.columns(2)
    with col1:
        caec = st.selectbox("การรับประทานอาหารระหว่างมื้อ (CAEC)", ["no", "Sometimes", "Frequently", "Always"], format_func=caec_label, help="ความถี่ในการรับประทานอาหารระหว่างมื้อ")
    with col2:
        calc = st.selectbox("การดื่มแอลกอฮอล์ (CALC)", ["no", "Sometimes", "Frequently", "Always"], format_func=calc_label, help="ความถี่ในการดื่มเครื่องดื่มแอลกอฮอล์")

    st.subheader("ไลฟ์สไตล์และกิจกรรม")
    col1, col2, col3 = st.columns(3)
    with col1:
        ch2o = st.number_input("ปริมาณการดื่มน้ำต่อวัน (CH2O)", min_value=1.0, max_value=3.0, value=1.0, step=0.1, help="ปริมาณน้ำที่ดื่มต่อวัน: 1 = น้อยกว่า 1 ลิตร, 2 = ประมาณ 1–2 ลิตร, 3 = มากกว่า 2 ลิตร")
    with col2:
        faf = st.number_input("ความถี่ในการทำกิจกรรมทางกาย (FAF)", min_value=0.0, max_value=3.0, value=1.0, step=0.1, help="จำนวนวันที่ทำกิจกรรมทางกายต่อสัปดาห์: 0 = ไม่ทำ, 1 = 1–2 วัน, 2 = 2–4 วัน, 3 = 4–5 วัน")
    with col3:
        tue = st.number_input("ระยะเวลาใช้อุปกรณ์เทคโนโลยีต่อวัน (TUE)", min_value=0.0, max_value=2.0, value=1.0, step=0.1, help="เวลาที่ใช้โทรศัพท์ คอมพิวเตอร์ หรืออุปกรณ์เทคโนโลยีต่อวัน: 0 = 0–2 ชม., 1 = 3–5 ชม., 2 = มากกว่า 5 ชม.")

    col1, col2, col3 = st.columns(3)
    with col1:
        smoke = st.selectbox("การสูบบุหรี่ (SMOKE)", ["no", "yes"], format_func=yes_no, help="yes = สูบบุหรี่, no = ไม่สูบบุหรี่")
    with col2:
        scc = st.selectbox("การติดตามปริมาณแคลอรีที่รับประทาน (SCC)", ["no", "yes"], format_func=yes_no, help="yes = มีการติดตาม/ควบคุมปริมาณแคลอรีที่รับประทาน, no = ไม่มีการติดตาม")
    with col3:
        mtrans = st.selectbox("รูปแบบการเดินทาง (MTRANS)", ["Public_Transportation", "Automobile", "Walking", "Motorbike", "Bike"], format_func=mtrans_label, help="เลือกรูปแบบการเดินทางที่ใช้เป็นหลัก")

    submitted = st.form_submit_button("ทำนาย", use_container_width=True)

if submitted == True:
    input_data = pd.DataFrame()
    input_data["Gender"] = [gender]
    input_data["Age"] = [age]
    input_data["Height"] = [height]
    input_data["Weight"] = [weight]
    input_data["family_history_with_overweight"] = [family_history]
    input_data["FAVC"] = [favc]
    input_data["FCVC"] = [fcvc]
    input_data["NCP"] = [ncp]
    input_data["CAEC"] = [caec]
    input_data["SMOKE"] = [smoke]
    input_data["CH2O"] = [ch2o]
    input_data["SCC"] = [scc]
    input_data["FAF"] = [faf]
    input_data["TUE"] = [tue]
    input_data["CALC"] = [calc]
    input_data["MTRANS"] = [mtrans]

    raw_prediction = obesity_pipeline.predict(input_data)[0]
    prediction = str(raw_prediction).strip().replace(" ", "_")
    
    probabilities = obesity_pipeline.predict_proba(input_data)[0]
    classes = obesity_pipeline.classes_
    
    max_prob = 0.0
    for p in probabilities:
        if p > max_prob:
            max_prob = p
    confidence = max_prob

    st.divider()
    st.subheader("ผลการทำนาย")

    result_col1, result_col2 = st.columns(2)

    with result_col1:
        st.metric("ระดับที่ระบบทำนาย", prediction.replace("_", " "))

    with result_col2:
        st.metric("ความมั่นใจของโมเดล", str(round(confidence * 100, 1)) + "%")

    if confidence < 0.60:
        st.warning("โมเดลมีความมั่นใจในการทำนายน้อยกว่า 60%ผลลัพธ์อาจไม่แม่นยำ")
    else:
        st.success("โมเดลมีความมั่นใจในการทำนายตั้งแต่ 60% ขึ้นไป")

    with st.expander("ดูความน่าจะเป็นของแต่ละกลุ่ม"):
        class_list = []
        for c in classes:
            class_list.append(c.replace("_", " "))
        
        prob_list = []
        for p in probabilities:
            prob_list.append(str(round(p * 100, 1)) + "%")
            
        probability_df = pd.DataFrame()
        probability_df["ระดับภาวะอ้วน"] = class_list
        probability_df["ความน่าจะเป็น"] = prob_list
        
        probability_df = probability_df.sort_values(by=["ความน่าจะเป็น"], ascending=False)
        
        st.dataframe(probability_df, hide_index=True, use_container_width=True)

    st.divider()
    st.subheader("คำแนะนำการออกกำลังกาย")

    exercise_recommendation = ""
    if prediction == "Insufficient_Weight":
        exercise_recommendation = "เน้นการฝึกเวทเทรนนิ่งเพื่อสร้างกล้ามเนื้อ ร่วมกับคาร์ดิโอเบา ๆ และรับประทานอาหารให้เพียงพอต่อการเพิ่มน้ำหนักอย่างเหมาะสม"
    elif prediction == "Normal_Weight":
        exercise_recommendation = "ออกกำลังกายอย่างสมดุล โดยทำคาร์ดิโอระดับปานกลางประมาณ 150 นาทีต่อสัปดาห์ ร่วมกับเวทเทรนนิ่ง 2–3 ครั้งต่อสัปดาห์ และรับประทานอาหารที่มีประโยชน์"
    elif prediction == "Overweight_Level_I":
        exercise_recommendation = "เพิ่มคาร์ดิโอระดับปานกลางประมาณ 200–250 นาทีต่อสัปดาห์ ร่วมกับเวทเทรนนิ่งอย่างสม่ำเสมอ และควบคุมปริมาณอาหารให้เหมาะสม"
    elif prediction == "Overweight_Level_II":
        exercise_recommendation = "เน้นคาร์ดิโอประมาณ 250–300 นาทีต่อสัปดาห์ ร่วมกับเวทเทรนนิ่งอย่างสม่ำเสมอ และปรับการรับประทานอาหารโดยลดพลังงานส่วนเกิน"
    elif prediction == "Obesity_Type_I":
        exercise_recommendation = "เริ่มจากการออกกำลังกายแบบแรงกระแทกต่ำ เช่น เดินหรือปั่นจักรยานเบา ๆ แล้วค่อย ๆ เพิ่มเวลาและความหนัก โดยเน้นความสม่ำเสมอ"
    elif prediction == "Obesity_Type_II":
        exercise_recommendation = "เน้นการออกกำลังกายที่มีแรงกระแทกต่ำ เพื่อช่วยลดแรงกดต่อข้อต่อ ร่วมกับการฝึกเคลื่อนไหวร่างกาย และควรได้รับคำแนะนำจากผู้เชี่ยวชาญ"
    elif prediction == "Obesity_Type_III":
        exercise_recommendation = "ควรเริ่มจากการเคลื่อนไหวร่างกายเบา ๆ ในชีวิตประจำวัน เน้นการเคลื่อนไหวและความยืดหยุ่น และควรออกกำลังกายภายใต้คำแนะนำของผู้เชี่ยวชาญ"
    else:
        exercise_recommendation = "ไม่พบระดับภาวะอ้วนที่ตรงกับข้อมูล"

    st.info(exercise_recommendation)

st.divider()
st.caption("ระบบนี้เป็นเพียงเครื่องมือที่สร้างมาเพื่อศึกษาและให้ข้อมูลเบื้องต้นเท่านั้น ไม่สามารถใช้แทนคำปรึกษาทางการแพทย์ได้")