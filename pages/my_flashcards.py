import streamlit as st
import random
from utils.ui_styles import inject_custom_css, init_session_state, render_sidebar

st.set_page_config(
    page_title="Study Arena - Flashcard Generator Agent",
    page_icon="🧠",
    layout="wide"
)

init_session_state()
inject_custom_css()

render_sidebar()

# Check if there are generated cards
cards = st.session_state.generated_cards

if not cards:
    st.markdown('<div class="hero-section"><h1 class="hero-title">Study Arena</h1><p class="hero-subtitle">Review and master your generated flashcard decks</p></div>', unsafe_allow_html=True)
    st.warning("⚠️ No flashcards have been loaded or generated yet. Please upload content on the Home page first!")
    st.info("💡 Tip: You can also upload a CSV or APKG, or load previous decks from the History page.")
    st.stop()

# Header
st.markdown(f'<div class="hero-section"><h1 class="hero-title">Study Arena</h1><p class="hero-subtitle">Currently studying: {st.session_state.active_deck_name} ({len(cards)} cards)</p></div>', unsafe_allow_html=True)

# Select mode
study_mode = st.tabs(["📇 Study Mode (Flip Cards)", "✍️ Quiz Mode (MCQs)"])

# ----------------- Tab 1: Study Mode -----------------
with study_mode[0]:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        idx = st.session_state.study_index
        if idx >= len(cards):
            st.session_state.study_index = 0
            idx = 0
            
        card = cards[idx]
        
        # Render progress
        st.write(f"**Card {idx + 1} of {len(cards)}**")
        st.progress((idx + 1) / len(cards))
        
        # Flip State
        flipped = st.session_state.study_flipped
        card_class = "flashcard-inner is-flipped" if flipped else "flashcard-inner"
        
        # Render 3D Card
        st.markdown(f"""
        <div class="flashcard-container">
            <div class="{card_class}">
                <div class="flashcard-side flashcard-front">
                    <div class="flashcard-badge">{card.get('type', 'Basic')}</div>
                    <div class="flashcard-text">{card.get('front', '')}</div>
                    <div class="flashcard-hint">Click "FLIP" below to reveal the answer</div>
                </div>
                <div class="flashcard-side flashcard-back">
                    <div class="flashcard-badge">{card.get('type', 'Basic')}</div>
                    <div class="flashcard-text">{card.get('back', '')}</div>
                    <div class="flashcard-hint">Evaluate your retention</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Controls
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 1, 1])
        with ctrl_col2:
            if st.button("🔄 Flip Card", key="flip_btn"):
                st.session_state.study_flipped = not st.session_state.study_flipped
                st.rerun()
                
        # Self evaluation feedback when flipped
        if flipped:
            st.markdown("<h4 style='text-align: center;'>How well did you recall this?</h4>", unsafe_allow_html=True)
            choice_col1, choice_col2, choice_col3 = st.columns([1, 1, 1])
            
            with choice_col1:
                if st.button("🔴 Hard", key="hard_btn"):
                    st.session_state.study_flipped = False
                    st.session_state.study_index = (idx + 1) % len(cards)
                    st.toast("Card marked for review!", icon="📌")
                    st.rerun()
            with choice_col2:
                if st.button("🟡 Good", key="good_btn"):
                    st.session_state.study_flipped = False
                    st.session_state.study_index = (idx + 1) % len(cards)
                    st.toast("Well done!", icon="👍")
                    st.rerun()
            with choice_col3:
                if st.button("🟢 Easy", key="easy_btn"):
                    st.session_state.study_flipped = False
                    st.session_state.study_index = (idx + 1) % len(cards)
                    st.toast("Mastered!", icon="🏆")
                    st.rerun()
                    
        # Navigation shortcuts
        nav_col1, nav_col2 = st.columns(2)
        with nav_col1:
            if st.button("⬅️ Previous Card", disabled=(idx == 0)):
                st.session_state.study_flipped = False
                st.session_state.study_index = max(0, idx - 1)
                st.rerun()
        with nav_col2:
            if st.button("Next Card ➡️", disabled=(idx == len(cards) - 1)):
                st.session_state.study_flipped = False
                st.session_state.study_index = min(len(cards) - 1, idx + 1)
                st.rerun()

# ----------------- Tab 2: Quiz Mode -----------------
with study_mode[1]:
    if len(cards) < 4:
        st.warning("⚠️ Quiz Mode requires at least 4 flashcards to generate plausible distractor answers.")
        st.stop()
        
    # Generate static list of questions in session state if not set
    if not st.session_state.quiz_questions or len(st.session_state.quiz_questions) != len(cards):
        quiz_list = []
        for i, c in enumerate(cards):
            correct_ans = c.get("back", "")
            
            # Select 3 distractors
            other_backs = [other.get("back", "") for idx_other, other in enumerate(cards) if idx_other != i]
            distractors = random.sample(other_backs, min(3, len(other_backs)))
            
            # Combine and shuffle
            options = distractors + [correct_ans]
            random.shuffle(options)
            
            quiz_list.append({
                "question": c.get("front", ""),
                "correct": correct_ans,
                "options": options,
                "type": c.get("type", "Basic")
            })
        st.session_state.quiz_questions = quiz_list
        st.session_state.quiz_user_answers = {}
        st.session_state.quiz_score = 0
        
    st.subheader("📝 Practice Exam")
    
    correct_count = 0
    total_answered = 0
    
    # Render quiz questions
    for idx_q, q in enumerate(st.session_state.quiz_questions):
        st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"**Question {idx_q + 1}**: {q['question']}")
        
        # User answer key
        ans_key = f"quiz_ans_{idx_q}"
        
        # Find index of previously selected option if any
        prev_ans = st.session_state.quiz_user_answers.get(idx_q, None)
        prev_idx = q["options"].index(prev_ans) if prev_ans in q["options"] else None
        
        selected = st.radio(
            "Select the correct answer:",
            options=q["options"],
            index=prev_idx,
            key=ans_key,
            help="Choose the matching back of the card"
        )
        
        # If selection changed
        if selected != prev_ans:
            st.session_state.quiz_user_answers[idx_q] = selected
            st.rerun()
            
        # Feedback
        if selected:
            total_answered += 1
            if selected == q["correct"]:
                correct_count += 1
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. The correct answer is: {q['correct']}")
                
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Render final score panel
    if total_answered > 0:
        st.markdown('<div class="glass-card" style="text-align: center;">', unsafe_allow_html=True)
        score_pct = (correct_count / len(cards)) * 100
        st.markdown(f"### 🏆 Final Score: **{correct_count}/{len(cards)}** ({score_pct:.1f}%)")
        if score_pct == 100:
            st.balloons()
            st.success("Perfect Score! You have fully mastered this deck.")
        elif score_pct >= 70:
            st.info("Good job! Continue studying to hit 100%.")
        else:
            st.warning("Keep practicing to improve retention.")
            
        if st.button("🔄 Reset Quiz & Reshuffle Choices"):
            st.session_state.quiz_questions = []
            st.session_state.quiz_user_answers = {}
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
