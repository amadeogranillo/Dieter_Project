import streamlit as st

def post_phase_questionnaire(phase):
    st.subheader("Post-phase Questionnaire")
    responses = {}
    if phase == 1:
        responses['reason'] = st.text_input("Why did you choose each box? (e.g., safety, curiosity, intuition)")
        responses['pattern'] = st.text_input("When did you notice changes in probabilities or patterns?")
        responses['stress'] = st.slider("Stress level during this phase (1 = none, 5 = high)", 1, 5, 3)
        responses['confidence'] = st.slider("How confident were you in your choices? (1 = not at all, 5 = very confident)", 1, 5, 3)
        responses['perceived_control'] = st.slider("Did you feel you could influence the outcome? (1 = not at all, 5 = completely)", 1, 5, 3)
        responses['strategy'] = st.text_area("Did you use a specific strategy? If yes, please describe.")
    elif phase == 2:
        responses['avoided'] = st.text_input("Did you avoid Box B because of surprises?")
        responses['pattern'] = st.text_input("After how many rounds (box selection) did you detect patterns?")
        responses['motive'] = st.text_input("Reason for changes in your choices?")
        responses['stress'] = st.slider("Stress level during this phase (1 = none, 5 = high)", 1, 5, 3)
        responses['confidence'] = st.slider("How confident were you in your choices? (1 = not at all, 5 = very confident)", 1, 5, 3)
        responses['perceived_control'] = st.slider("Did you feel you could influence the outcome? (1 = not at all, 5 = completely)", 1, 5, 3)
        responses['strategy'] = st.text_area("Did you use a specific strategy? If yes, please describe.")
    elif phase == 3:
        responses['reason'] = st.text_input("Why did you prefer one box?")
        responses['risk'] = st.text_input("Did you feel more risk in Box B?")
        responses['mechanism'] = st.text_input("Did you detect dynamic mechanisms?")
        responses['stress'] = st.slider("Stress level during this phase (1 = none, 5 = high)", 1, 5, 3)
        responses['confidence'] = st.slider("How confident were you in your choices? (1 = not at all, 5 = very confident)", 1, 5, 3)
        responses['perceived_control'] = st.slider("Did you feel you could influence the outcome? (1 = not at all, 5 = completely)", 1, 5, 3)
        responses['strategy'] = st.text_area("Did you use a specific strategy? If yes, please describe.")
    return responses

def debrief_questionnaire():
    st.subheader("Debrief and Final Feedback")
    st.markdown("Thank you for participating! Please answer a few final questions about your overall experience.")
    feedback = {}
    feedback['overall_stress'] = st.slider("Overall, how stressful did you find the experiment? (1 = not at all, 5 = very stressful)", 1, 5, 3)
    feedback['overall_confidence'] = st.slider("How confident were you in your decisions overall? (1 = not at all, 5 = very confident)", 1, 5, 3)
    feedback['phase_preference'] = st.text_input("Which phase did you find most interesting or challenging, and why?")
    feedback['final_strategy'] = st.text_area("Did your strategy change across phases? Please describe.")
    feedback['comments'] = st.text_area("Any other comments or suggestions?")
    return feedback
