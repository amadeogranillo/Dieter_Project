import streamlit as st
from constants import *

def display_boxes(phase, p_safe, p_uncertain, show_special=False):
    """
    Visualizes the two boxes with balls as emojis.
    For known probabilities, show red/black balls. For unknown, show '?'. For Rumsfeld, show special ball if show_special.
    """
    col1, col2 = st.columns(2)
    # Box A
    with col1:
        st.markdown("**Box A**")
        if phase == 1 or (phase == 2):
            # Known probability
            n_red = int(round(p_safe * 10))
            n_black = 10 - n_red
            balls = ' '.join(['🔴'] * n_red + ['⚫'] * n_black)
        else:
            # Ambiguity
            balls = ' '.join(['❓'] * 10)
        st.markdown(balls)
    # Box B
    with col2:
        st.markdown("**Box B**")
        if (phase == 1):
            # Ambiguity
            balls = ' '.join(['❓'] * 10)
        elif phase == 2:
            # Rumsfeld: unknown + possible special
            balls = ' '.join(['❓'] * 9)
            if show_special:
                balls += ' ⭐'
        elif phase == 3:
            # Rumsfeld: unknown + possible special
            balls = ' '.join(['❓'] * 8)
            if show_special:
                balls += ' ⭐ 🥈'
        st.markdown(balls)

def show_instructions(phase):
    if phase == 1:
        st.markdown("""
        - **Box A:** Known probability (risk)
        - **Box B:** Unknown probability (ambiguity)
        """)
    elif phase == 2:
        st.markdown("""
        - **Box A:** Known probability (risk)
        - **Box B:** Unknown probability + possible surprises (Rumsfeld)
        """)
    elif phase == 3:
        st.markdown("""
        - **Box A:** Unknown probability (ambiguity)
        - **Box B:** Unknown probability + possible surprises (Rumsfeld)
        """)

def show_feedback(result, reward, box):
    if result == 'red':
        st.success(f"You drew a red ball from Box {box} (+{reward} €)")
    elif result == 'black':
        st.error(f"You drew a black ball from Box {box} ({reward} €)")
    elif result == 'gold':
        st.success(f"Surprise! You drew a gold ball from Box {box} (+{reward} €)")
    elif result == 'silver':
        st.warning(f"Surprise! You drew a silver ball from Box {box} ({reward} €)")
