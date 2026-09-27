import ast
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


# =========================================================
# Page configuration
# =========================================================

st.set_page_config(
    page_title="Obesity Management System",
    page_icon="🏃",
    layout="wide",
)


# =========================================================
# Load model and recommendation data
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "obesity_pipeline.pkl"
PROGRAM_PATH = BASE_DIR / "program_summary.csv"


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_programs():
    df = pd.read_csv(PROGRAM_PATH)

    # level and goal are stored as strings such as:
    # "['Beginner', 'Novice']"
    df["level"] = df["level"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )
    df["goal"] = df["goal"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )

    return df


try:
    obesity_pipeline = load_model()
    df_programs = load_programs()
except FileNotFoundError as e:
    st.error(f"ไม่พบไฟล์: {e.filename}")
    st.info(
        "ตรวจสอบว่า obesity_pipeline.pkl และ program_summary.csv "
        "อยู่ในโฟลเดอร์เดียวกับ app.py"
    )
    st.stop()
except Exception as e:
    st.error("ไม่สามารถโหลดไฟล์ของระบบได้")
    st.exception(e)
    st.stop()


# =========================================================
# Recommendation functions
# =========================================================

def get_exercise_recommendations(obesity_level):
    """Provides general exercise recommendations based on obesity level."""

    if obesity_level == "Insufficient_Weight":
        return (
            "Focus on strength training to build muscle mass, light cardio, "
            "and ensure a balanced, calorie-sufficient diet for healthy weight gain."
        )

    elif obesity_level == "Normal_Weight":
        return (
            "Maintain a balanced routine: 150 นาที of moderate cardio per week, "
            "combined with strength training 2-3 times per week, and a healthy diet."
        )

    elif obesity_level == "Overweight_ระดับ_I":
        return (
            "Increase moderate-intensity cardio to 200-250 นาที per week, "
            "incorporate consistent strength training, and focus on portion control "
            "and balanced nutrition."
        )

    elif obesity_level == "Overweight_ระดับ_II":
        return (
            "Aim for higher-intensity cardio (250-300 นาที per week), "
            "consistent strength training, and crucial dietary changes focused "
            "on calorie reduction and nutrient-dense foods."
        )

    elif obesity_level == "Obesity_Type_I":
        return (
            "Begin with low-impact cardio, gradually increasing intensity and duration. "
            "Focus on consistency, and seek professional guidance for both exercise "
            "and dietary plans."
        )

    elif obesity_level == "Obesity_Type_II":
        return (
            "Emphasize low-impact activities to protect joints, focus on improving "
            "mobility, and strictly follow medical and professional exercise supervision. "
            "Significant dietary modifications are required."
        )

    elif obesity_level == "Obesity_Type_III":
        return (
            "Medical supervision is paramount. Start with very light daily movements, "
            "prioritize mobility and flexibility, and adhere to a strict dietary plan "
            "under professional care."
        )

    return "Unknown obesity level. Please provide a valid 'NObeyesdad' category."


def get_program_recommendations(obesity_level, df_programs):
    """Return up to five exercise programs using the project's existing rules."""

    filtered_programs = pd.DataFrame()

    if obesity_level == "Insufficient_Weight":
        filtered_programs = df_programs[
            df_programs["level"].apply(
                lambda x: any(
                    l in x for l in ["Beginner", "Novice", "Intermediate"]
                )
            )
            & df_programs["goal"].apply(
                lambda x: any(
                    g in x
                    for g in [
                        "Bodybuilding",
                        "Muscle & Sculpting",
                        "Powerbuilding",
                    ]
                )
            )
            & df_programs["equipment"].isin(["Full Gym", "Garage Gym"])
            & (df_programs["time_per_workout"] >= 60)
            & (df_programs["time_per_workout"] <= 90)
        ]

    elif obesity_level == "Normal_Weight":
        filtered_programs = df_programs[
            df_programs["level"].apply(
                lambda x: any(l in x for l in ["Intermediate", "Advanced"])
            )
            & df_programs["goal"].apply(
                lambda x: any(
                    g in x
                    for g in ["Bodybuilding", "Muscle & Sculpting", "Athletics"]
                )
            )
            & (df_programs["time_per_workout"] >= 60)
            & (df_programs["time_per_workout"] <= 120)
        ]

    elif obesity_level in ["Overweight_ระดับ_I", "Overweight_ระดับ_II"]:
        filtered_programs = df_programs[
            df_programs["level"].apply(
                lambda x: any(
                    l in x for l in ["Beginner", "Novice", "Intermediate"]
                )
            )
            & df_programs["goal"].apply(
                lambda x: any(
                    g in x for g in ["Muscle & Sculpting", "Bodyweight Fitness"]
                )
            )
            & df_programs["equipment"].isin(
                ["Full Gym", "Garage Gym", "At Home"]
            )
            & (df_programs["time_per_workout"] >= 45)
            & (df_programs["time_per_workout"] <= 75)
        ]

    elif obesity_level in ["Obesity_Type_I", "Obesity_Type_II"]:
        filtered_programs = df_programs[
            df_programs["level"].apply(
                lambda x: any(l in x for l in ["Beginner", "Novice"])
            )
            & df_programs["goal"].apply(
                lambda x: any(
                    g in x for g in ["Bodyweight Fitness", "Muscle & Sculpting"]
                )
            )
            & df_programs["equipment"].isin(
                ["At Home", "Dumbbell Only", "Full Gym"]
            )
            & (df_programs["time_per_workout"] >= 30)
            & (df_programs["time_per_workout"] <= 60)
        ]

    elif obesity_level == "Obesity_Type_III":
        filtered_programs = df_programs[
            df_programs["level"].apply(
                lambda x: any(l in x for l in ["Beginner", "Novice"])
            )
            & df_programs["goal"].apply(
                lambda x: "Bodyweight Fitness" in x
            )
            & df_programs["equipment"].isin(["At Home", "Dumbbell Only"])
            & (df_programs["time_per_workout"] >= 10)
            & (df_programs["time_per_workout"] <= 30)
        ]

    if not filtered_programs.empty:
        return filtered_programs.sort_values(
            by=["program_length", "time_per_workout"]
        ).head(5)

    return filtered_programs


# =========================================================
# UI
# =========================================================

st.title("🏃 ระบบประเมินภาวะอ้วนและแนะนำการออกกำลังกาย")
st.write(
    "Predict an obesity level from personal and lifestyle information, "
    "then receive exercise guidance and recommended workout programs."
)

st.info(
    "This is a machine-learning prototype for educational purposes. "
    "The prediction is not a medical diagnosis."
)

st.divider()

with st.form("prediction_form"):

    st.subheader("👤 ข้อมูลส่วนบุคคล")

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input(
            "อายุ",
            min_value=14,
            max_value=100,
            value=23,
            step=1,
        )

    with col2:
        gender = st.selectbox(
            "เพศ",
            ["Male", "Female"],
        )

    with col3:
        family_history = st.selectbox(
            "ประวัติคนในครอบครัวมีภาวะน้ำหนักเกิน",
            ["yes", "no"],
        )

    col1, col2 = st.columns(2)

    with col1:
        height = st.number_input(
            "ส่วนสูง (เมตร)",
            min_value=1.0,
            max_value=2.5,
            value=1.70,
            step=0.01,
            format="%.2f",
        )

    with col2:
        weight = st.number_input(
            "น้ำหนัก (กิโลกรัม)",
            min_value=20.0,
            max_value=250.0,
            value=70.0,
            step=0.1,
            format="%.1f",
        )

    st.subheader("🍽️ พฤติกรรมการรับประทานอาหาร")

    col1, col2, col3 = st.columns(3)

    with col1:
        favc = st.selectbox(
            "การรับประทานอาหารแคลอรีสูงเป็นประจำ (FAVC)",
            ["yes", "no"],
        )

    with col2:
        fcvc = st.number_input(
            "การรับประทานผัก (FCVC)",
            min_value=1.0,
            max_value=3.0,
            value=2.0,
            step=0.1,
        )

    with col3:
        ncp = st.number_input(
            "จำนวนมื้ออาหารหลักต่อวัน (NCP)",
            min_value=1.0,
            max_value=4.0,
            value=3.0,
            step=0.1,
        )

    col1, col2 = st.columns(2)

    with col1:
        caec = st.selectbox(
            "การรับประทานอาหารระหว่างมื้อ (CAEC)",
            ["no", "Sometimes", "Frequently", "Always"],
        )

    with col2:
        calc = st.selectbox(
            "การดื่มแอลกอฮอล์ (CALC)",
            ["no", "Sometimes", "Frequently", "Always"],
        )

    st.subheader("🏃 ไลฟ์สไตล์และกิจกรรม")

    col1, col2, col3 = st.columns(3)

    with col1:
        ch2o = st.number_input(
            "ปริมาณการดื่มน้ำ (CH2O)",
            min_value=1.0,
            max_value=3.0,
            value=2.0,
            step=0.1,
        )

    with col2:
        faf = st.number_input(
            "ความถี่ในการทำกิจกรรมทางกาย (FAF)",
            min_value=0.0,
            max_value=3.0,
            value=1.0,
            step=0.1,
        )

    with col3:
        tue = st.number_input(
            "ระยะเวลาใช้อุปกรณ์เทคโนโลยี (TUE)",
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.1,
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        smoke = st.selectbox(
            "การสูบบุหรี่ (SMOKE)",
            ["no", "yes"],
        )

    with col2:
        scc = st.selectbox(
            "การติดตามปริมาณแคลอรีที่รับประทาน (SCC)",
            ["no", "yes"],
        )

    with col3:
        mtrans = st.selectbox(
            "รูปแบบการเดินทาง (MTRANS)",
            [
                "Public_Transportation",
                "Automobile",
                "Walking",
                "Motorbike",
                "Bike",
            ],
        )

    submitted = st.form_submit_button(
        "🔍 ทำนายและแนะนำ",
        use_container_width=True,
    )


# =========================================================
# Prediction + Recommendation
# =========================================================

if submitted:

    input_data = pd.DataFrame(
        [
            {
                "Gender": gender,
                "Age": age,
                "Height": height,
                "Weight": weight,
                "family_history_with_overweight": family_history,
                "FAVC": favc,
                "FCVC": fcvc,
                "NCP": ncp,
                "CAEC": caec,
                "SMOKE": smoke,
                "CH2O": ch2o,
                "SCC": scc,
                "FAF": faf,
                "TUE": tue,
                "CALC": calc,
                "MTRANS": mtrans,
            }
        ]
    )

    try:
        prediction = obesity_pipeline.predict(input_data)[0]
        probabilities = obesity_pipeline.predict_proba(input_data)[0]

        classes = obesity_pipeline.classes_
        confidence = float(max(probabilities))

        # -------------------------------------------------
        # Prediction result
        # -------------------------------------------------

        st.divider()
        st.subheader("🎯 ผลการทำนาย")

        result_col1, result_col2 = st.columns(2)

        with result_col1:
            st.metric(
                "ระดับที่ระบบทำนาย",
                prediction.replace("_", " "),
            )

        with result_col2:
            st.metric(
                "ความมั่นใจของโมเดล",
                f"{confidence:.1%}",
            )

        if confidence < 0.60:
            st.warning(
                "Prediction confidence is below 60%. "
                "The result may be uncertain and should be interpreted cautiously."
            )
        else:
            st.success("โมเดลมีความมั่นใจในการทำนายตั้งแต่ 60% ขึ้นไป")

        # -------------------------------------------------
        # ความน่าจะเป็น distribution
        # -------------------------------------------------

        with st.expander("ดูความน่าจะเป็นของแต่ละกลุ่ม"):
            probability_df = pd.DataFrame(
                {
                    "ระดับภาวะอ้วน": [
                        c.replace("_", " ") for c in classes
                    ],
                    "ความน่าจะเป็น": probabilities,
                }
            ).sort_values("ความน่าจะเป็น", ascending=False)

            probability_df["ความน่าจะเป็น"] = probability_df["ความน่าจะเป็น"].map(
                lambda x: f"{x:.1%}"
            )

            st.dataframe(
                probability_df,
                hide_index=True,
                use_container_width=True,
            )

        # -------------------------------------------------
        # General exercise recommendation
        # -------------------------------------------------

        st.subheader("💪 คำแนะนำการออกกำลังกาย")

        recommendation = get_exercise_recommendations(prediction)

        st.write(recommendation)

        # -------------------------------------------------
        # Program recommendations
        # -------------------------------------------------

        st.subheader("📋 โปรแกรมออกกำลังกายที่แนะนำ")

        recommended_programs = get_program_recommendations(
            prediction,
            df_programs,
        )

        if recommended_programs.empty:
            st.warning(
                "No workout programs were found for this predicted category "
                "using the current recommendation rules."
            )
        else:
            for i, (_, row) in enumerate(
                recommended_programs.iterrows(),
                start=1,
            ):
                with st.expander(
                    f"{i}. {row['title']}"
                ):
                    st.write(row["description"])

                    info_col1, info_col2, info_col3 = st.columns(3)

                    with info_col1:
                        st.write(
                            f"**ระดับ:** "
                            f"{', '.join(row['level'])}"
                        )

                    with info_col2:
                        st.write(
                            f"**เป้าหมาย:** "
                            f"{', '.join(row['goal'])}"
                        )

                    with info_col3:
                        st.write(
                            f"**อุปกรณ์:** {row['equipment']}"
                        )

                    st.write(
                        f"**ระยะเวลาโปรแกรม:** "
                        f"{row['program_length']:.0f} สัปดาห์"
                    )

                    st.write(
                        f"**เวลาในการออกกำลังกายแต่ละครั้ง:** "
                        f"{row['time_per_workout']:.0f} นาที"
                    )

                    st.write(
                        f"**จำนวนท่าออกกำลังกาย:** "
                        f"{row['total_exercises']}"
                    )

    except Exception as e:
        st.error("เกิดข้อผิดพลาดระหว่างการทำนาย")
        st.exception(e)


# =========================================================
# Footer
# =========================================================

st.divider()

st.caption(
    "ระบบประเมินภาวะอ้วนและแนะนำการออกกำลังกาย — Random Forest + Exercise Recommendation"
)
st.caption(
    "AI disclosure: ChatGPT was used to assist with code explanation, "
    "UI design, and code review. The project team reviewed and adapted "
    "the implementation for the submitted system."
)
