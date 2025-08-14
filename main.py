import streamlit as st
import time
from experiment import Experiment
from ui import display_boxes, show_instructions, show_feedback
from data import save_round_data, save_questionnaire, get_unique_filename
from questionnaires import post_phase_questionnaire, debrief_questionnaire
from constants import PHASES, ROUNDS_PER_PHASE

# Helper for double-click message
def double_click_msg():
    st.markdown("<span style='font-size: 0.85em; color: #888;'>* To avoid confusion, click button twice to continue</span>", unsafe_allow_html=True)

# Session state initialization
def init_session():
    st.session_state['step'] = 'welcome'
    st.session_state['participant_id'] = ''
    st.session_state['phase_idx'] = 0
    st.session_state['experiment'] = None
    st.session_state['round'] = 1
    st.session_state['last_result'] = None
    st.session_state['last_reward'] = None
    st.session_state['last_box'] = None
    st.session_state['show_feedback'] = False
    st.session_state['start_time'] = None
    st.session_state['questionnaire'] = {}
    st.session_state['phase_order'] = None
    st.session_state['phase_complete'] = False
    st.session_state['all_done'] = False
    st.session_state['awaiting_choice'] = True
    st.session_state['last_special'] = None
    st.session_state['exited'] = False
    st.session_state['exit_time'] = None

if 'step' not in st.session_state:
    init_session()

# Remove exit_button and its calls from all screens except exit_screen

def welcome_screen():
    st.title("Uncertainty Decision Experiment")
    st.markdown("""
    **Welcome to the experiment.**
    
    In each phase, you will choose between two boxes (A and B) for 25 rounds. Each box contains 100 balls (red = +5€, black = -2€). The information about the proportions or rules varies. Your goal is to maximize your (fictitious) earnings. At the end of each phase, you will answer a short questionnaire. You may leave at any time. All data is anonymous. Please do not reload the page during the experiment.
    
    **By clicking 'Continue', you consent to participate.**
    """)
    if st.button('Continue'):
        st.session_state['step'] = 'enter_id'
    double_click_msg()

def id_screen():
    st.subheader("Enter your participant ID")
    participant_id = st.text_input("Participant ID (numbers only)", value=st.session_state['participant_id'])
    start_clicked = st.button('Start Experiment')
    double_click_msg()
    if start_clicked:
        if participant_id.isdigit():
            st.session_state['participant_id'] = int(participant_id)
            # Randomize phase order
            exp = Experiment(st.session_state['participant_id'])
            st.session_state['phase_order'] = exp.phase_order
            st.session_state['experiment'] = exp
            st.session_state['step'] = 'instructions'
        else:
            st.warning("Please enter a valid numeric participant ID.")

def instructions_screen():
    display_phase_num = st.session_state['phase_idx'] + 1
    actual_phase = st.session_state['phase_order'][st.session_state['phase_idx']]
    st.subheader(f"Phase {display_phase_num} - Instructions")
    show_instructions(actual_phase)
    if st.button('Begin Rounds'):
        st.session_state['step'] = 'rounds'
        st.session_state['start_time'] = time.time()
        st.session_state['phase_complete'] = False
        st.session_state['experiment'].reset_for_phase(actual_phase)
        st.session_state['awaiting_choice'] = True
        st.session_state['last_result'] = None
        st.session_state['last_reward'] = None
        st.session_state['last_box'] = None
        st.session_state['last_special'] = None
    double_click_msg()

def rounds_screen():
    exp = st.session_state['experiment']
    display_phase_num = st.session_state['phase_idx'] + 1
    actual_phase = exp.phase
    # Show instructions for the current phase at the top
    st.markdown(f"**Phase {display_phase_num} Instructions:**")
    show_instructions(actual_phase)
    st.subheader(f"Phase {display_phase_num} - Round {exp.round} of {ROUNDS_PER_PHASE}")
    st.write(f"Cumulative earnings: {exp.cumulative_earnings} €")
    display_boxes(actual_phase, exp.p_safe, exp.p_uncertain)
    if st.session_state['awaiting_choice']:
        st.write("Choose a box:")
        col1, col2 = st.columns(2)
        box_chosen = None
        with col1:
            if st.button('Box A', key=f"A_{display_phase_num}_{exp.round}"):
                box_chosen = 'A'
            double_click_msg()
        with col2:
            if st.button('Box B', key=f"B_{display_phase_num}_{exp.round}"):
                box_chosen = 'B'
            double_click_msg()
        if box_chosen:
            decision_time = time.time() - st.session_state['start_time']
            result, reward, special = exp.draw_ball(box_chosen)
            exp.cumulative_earnings += reward
            # Save data (actual_phase is the true phase number)
            exp.data.append([
                st.session_state['participant_id'], actual_phase, exp.round, box_chosen,
                round(decision_time, 3), result, reward, exp.cumulative_earnings,
                round(exp.p_safe, 3), round(exp.p_uncertain, 3)
            ])
            exp.adjust_probabilities(box_chosen)
            # Feedback
            st.session_state['last_result'] = result
            st.session_state['last_reward'] = reward
            st.session_state['last_box'] = box_chosen
            st.session_state['last_special'] = special
            st.session_state['awaiting_choice'] = False
            st.session_state['start_time'] = time.time()
    else:
        # Show feedback and Next button
        show_feedback(st.session_state['last_result'], st.session_state['last_reward'], st.session_state['last_box'])
        if st.button('Next'):
            if exp.round < ROUNDS_PER_PHASE:
                exp.round += 1
                st.session_state['awaiting_choice'] = True
                st.session_state['last_result'] = None
                st.session_state['last_reward'] = None
                st.session_state['last_box'] = None
                st.session_state['last_special'] = None
            else:
                st.session_state['phase_complete'] = True
                st.session_state['step'] = 'questionnaire'
        double_click_msg()

def questionnaire_screen():
    exp = st.session_state['experiment']
    display_phase_num = st.session_state['phase_idx'] + 1
    actual_phase = exp.phase
    responses = post_phase_questionnaire(actual_phase)
    if st.button('Submit Questionnaire & Start Next Phase'):
        # Save round data with initial probs and seeds
        save_round_data(
            exp.data,
            st.session_state['participant_id'],
            initial_probs=exp.get_initial_probs(),
            seeds=exp.get_seeds()
        )
        save_questionnaire(st.session_state['participant_id'], actual_phase, responses)
        st.session_state['phase_complete'] = False
        # Next phase or finish
        if st.session_state['phase_idx'] < 2:
            st.session_state['phase_idx'] += 1
            st.session_state['step'] = 'instructions'
        else:
            st.session_state['all_done'] = True
            st.session_state['step'] = 'debrief'
    double_click_msg()

def debrief_screen():
    st.subheader("Debrief and Final Feedback")
    st.markdown("Thank you for participating! Please answer a few final questions about your overall experience.")
    feedback = debrief_questionnaire()
    if st.button('Submit Final Feedback'):
        # Save debrief with unique filename
        filename = get_unique_filename('debrief', st.session_state['participant_id'])
        import pandas as pd
        pd.DataFrame([{**{'participant_id': st.session_state['participant_id']}, **feedback}]).to_csv(filename, index=False)
        st.session_state['step'] = 'thank_you'
    double_click_msg()

def exit_screen():
    st.subheader("Experiment Exited")
    st.markdown(f"You have exited the experiment at {st.session_state['exit_time']}.")
    st.markdown("If you exited by mistake, you may restart below.")
    if st.button('Restart'):
        init_session()
    double_click_msg()

def thank_you_screen():
    st.subheader("Thank you for your participation!")
    st.markdown("You have completed all phases. Your data has been saved. ")
    if st.button('Restart'):
        init_session()
    double_click_msg()

# Main app flow
if st.session_state['step'] == 'welcome':
    welcome_screen()
elif st.session_state['step'] == 'enter_id':
    id_screen()
elif st.session_state['step'] == 'instructions':
    instructions_screen()
elif st.session_state['step'] == 'rounds':
    rounds_screen()
elif st.session_state['step'] == 'questionnaire':
    questionnaire_screen()
elif st.session_state['step'] == 'debrief':
    debrief_screen()
elif st.session_state['step'] == 'exit_screen':
    exit_screen()
elif st.session_state['step'] == 'thank_you':
    thank_you_screen()
