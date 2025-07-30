import streamlit as st
import pandas as pd
import datetime
import requests
import os
import matplotlib.pyplot as plt


# CONFIGURATION

st.set_page_config(page_title="AI Productivity Tracker", layout="centered")
st.title("My AI Bestie: Productivity & Focus Tracker")


# 1. DAILY JOURNALING + AI FEEDBACK
st.header("Daily Reflection")
goals_file = "goals.csv"
journal_file = "journal_log.csv"

# Input
goal_today = st.text_input("What’s your main focus today?")
reflection = st.text_area("Reflect on today (distractions, wins, etc.)")

# Submit
if st.button("Submit Reflection"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_reflection = pd.DataFrame([[timestamp, goal_today, reflection]], columns=["timestamp", "goal", "reflection"])
    try:
        existing = pd.read_csv(journal_file)
        df_reflection = pd.concat([existing, df_reflection], ignore_index=True)
    except:
        pass
    df_reflection.to_csv(journal_file, index=False)
    
    # AI FEEDBACK via GROQ
    st.subheader(" AI Feedback")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",  
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You're a helpful productivity coach giving warm, honest daily feedback."},
            {"role": "user", "content": f"My reflection today: {reflection}. What can I do better tomorrow?"}
        ]
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
        feedback = res.json()["choices"][0]["message"]["content"]
        st.info(feedback)
    except:
        st.error("⚠️ AI feedback not available. Check your API key or internet.")



# 2. MULTIPLE GOALS TRACKING

st.header(" Goals Tracker")

with st.expander("➕ Add a New Goal"):
    new_goal = st.text_input("Enter goal")
    due_date = st.date_input("Due date", datetime.date.today())
    if st.button("Add Goal") and new_goal:
        status = "pending"
        df_new = pd.DataFrame([[new_goal, due_date, status]], columns=["goal", "due_date", "status"])
        try:
            df_goals = pd.read_csv(goals_file)
            df_goals = pd.concat([df_goals, df_new], ignore_index=True)
        except:
            df_goals = df_new
        df_goals.to_csv(goals_file, index=False)
        st.success("Goal added!")

# Display & Update Goals
try:
    df_goals = pd.read_csv(goals_file)
    st.subheader(" My Goals")
    for i, row in df_goals.iterrows():
        col1, col2, col3 = st.columns([5, 2, 2])
        with col1:
            st.write(f"{row['goal']} (Due: {row['due_date']})")
        with col2:
            if st.button("✅ Done", key=f"done_{i}"):
                df_goals.at[i, 'status'] = 'achieved'
        with col3:
            if st.button("🗑️ Delete", key=f"delete_{i}"):
                df_goals = df_goals.drop(i)
    df_goals.to_csv(goals_file, index=False)
except FileNotFoundError:
    st.info("No goals yet. Add one above!")


# 3. GOAL ACHIEVEMENT VISUALIZATION

st.header(" Goal Progress")
try:
    df = pd.read_csv(goals_file)
    chart_data = df['status'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(chart_data, labels=chart_data.index, autopct="%1.1f%%", colors=['green', 'orange'])
    ax.set_title("Goal Completion Ratio")
    st.pyplot(fig)
except:
    st.info("No goal data available for chart.")


# 4. POMODORO TIMER (Basic)

st.header("⏱ Pomodoro Timer")
st.markdown("Use this while working to stay focused.")
st.markdown("Use external tools like [Pomofocus](https://pomofocus.io/) or set a manual timer while tracking here.")



#  SIMPLE PROGRESS VISUAL
st.subheader("Daily Goal Progress")
try:
    df_logs = pd.read_csv(log_file)
    df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'])
    df_logs['date'] = df_logs['timestamp'].dt.date
    daily_counts = df_logs.groupby('date').count()['goal']
    st.line_chart(daily_counts)
except:
    pass

# REMINDER IF DISTRACTED
st.subheader("🔔 Focus Reminder")
if st.button("I'm still working"):
    st.success("👏 Great! Keep going!")
elif st.button("I'm distracted"):
    st.warning("😟 Try getting back to your goal. Maybe do a Pomodoro session.")
