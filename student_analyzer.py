# Student Performance Analyzer Dashboard
# This is a real-time dashboard built with Streamlit to analyze student performance data.
# It simulates live data generation and provides interactive visualizations.

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import time
import random

# Function to generate simulated real-time student data
# This function uses numpy for random number generation and pandas for data structuring
def generate_student_data(num_students=10):
    """
    Generates simulated student performance data.
    
    Parameters:
    num_students (int): Number of student records to generate
    
    Returns:
    pd.DataFrame: DataFrame containing student data with columns:
                  - Student_ID: Unique identifier for each student
                  - Name: Randomly generated student name
                  - Subject: Academic subject (Math, Science, English, History)
                  - Score: Academic score (0-100)
                  - Attendance: Attendance percentage (0-100)
                  - Study_Hours: Hours spent studying (0-20)
    
    Libraries used:
    - numpy (np): Used for generating random numbers with normal distributions
                  to create realistic data variations
    - pandas (pd): Used to create and structure the data into a DataFrame,
                   which is perfect for tabular data manipulation and analysis
    """
    # List of possible subjects
    subjects = ['Math', 'Science', 'English', 'History']
    
    # Generate random data using numpy
    student_ids = np.arange(1, num_students + 1)  # Sequential IDs
    names = [f"Student_{i}" for i in range(1, num_students + 1)]  # Simple names
    subject_choices = np.random.choice(subjects, num_students)  # Random subject selection
    
    # Generate scores with some realistic distribution (normal around 75)
    scores = np.random.normal(75, 15, num_students)
    scores = np.clip(scores, 0, 100)  # Ensure scores are between 0-100
    
    # Generate attendance percentages (normal around 85%)
    attendance = np.random.normal(85, 10, num_students)
    attendance = np.clip(attendance, 0, 100)  # Ensure between 0-100
    
    # Generate study hours (normal around 8 hours)
    study_hours = np.random.normal(8, 3, num_students)
    study_hours = np.clip(study_hours, 0, 20)  # Reasonable range
    
    # Create pandas DataFrame
    df = pd.DataFrame({
        'Student_ID': student_ids,
        'Name': names,
        'Subject': subject_choices,
        'Score': scores.round(1),  # Round to 1 decimal place
        'Attendance': attendance.round(1),
        'Study_Hours': study_hours.round(1)
    })
    
    return df

# Main dashboard function
def main():
    # Set page configuration
    st.set_page_config(page_title="Student Performance Analyzer", layout="wide")
    
    # Title
    st.title("📊 Real-Time Student Performance Analyzer Dashboard")
    
    # Initialize session state for data storage
    # st.session_state allows us to persist data across Streamlit reruns
    # This is crucial for maintaining the "history" of data as it comes in
    if 'student_data' not in st.session_state:
        st.session_state.student_data = pd.DataFrame()
    
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    
    # Sidebar for controls
    st.sidebar.header("Dashboard Controls")
    
    # Toggle switch to start/stop live data feed
    start_stop = st.sidebar.toggle("Start Live Data Feed", value=st.session_state.is_running)
    st.session_state.is_running = start_stop
    
    # Dropdown to filter by subject
    all_subjects = ['All'] + list(['Math', 'Science', 'English', 'History'])
    selected_subject = st.sidebar.selectbox("Filter by Subject", all_subjects)
    
    # Create placeholders for dynamic updates
    # st.empty() creates placeholder containers that can be updated later
    # This allows us to refresh the content without recreating the entire layout
    kpi_placeholder = st.empty()
    scatter_placeholder = st.empty()
    violin_placeholder = st.empty()
    
    # Main loop for real-time updates
    while st.session_state.is_running:
        # Generate new batch of student data
        new_data = generate_student_data(num_students=5)  # Generate 5 new students each cycle
        
        # Append new data to existing data using pandas concat
        # pandas concat() is used to combine DataFrames vertically (adding rows)
        st.session_state.student_data = pd.concat([st.session_state.student_data, new_data], ignore_index=True)
        
        # Keep only last 100 records to prevent memory issues
        if len(st.session_state.student_data) > 100:
            st.session_state.student_data = st.session_state.student_data.tail(100)
        
        # Filter data based on selected subject
        if selected_subject != 'All':
            filtered_data = st.session_state.student_data[st.session_state.student_data['Subject'] == selected_subject]
        else:
            filtered_data = st.session_state.student_data
        
        # Calculate KPIs using pandas aggregation functions
        # pandas provides powerful groupby and aggregation methods
        if not filtered_data.empty:
            avg_score = filtered_data['Score'].mean()
            total_students = len(filtered_data)
            avg_attendance = filtered_data['Attendance'].mean()
            avg_study_hours = filtered_data['Study_Hours'].mean()
            
            # Display KPIs using Streamlit columns for clean layout
            with kpi_placeholder.container():
                st.subheader("📈 Key Performance Indicators")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Average Score", f"{avg_score:.1f}")
                with col2:
                    st.metric("Total Students", total_students)
                with col3:
                    st.metric("Average Attendance", f"{avg_attendance:.1f}%")
                with col4:
                    st.metric("Average Study Hours", f"{avg_study_hours:.1f}")
            
            # Create Plotly scatter plot for Attendance vs Scores
            # Plotly is used for interactive visualizations
            # It allows zooming, hovering, and other interactive features
            with scatter_placeholder.container():
                st.subheader("📊 Attendance vs Score Correlation")
                fig_scatter = px.scatter(
                    filtered_data, 
                    x='Attendance', 
                    y='Score', 
                    color='Subject',
                    hover_data=['Name', 'Study_Hours'],
                    title="Interactive Scatter Plot: Attendance vs Score"
                )
                st.plotly_chart(fig_scatter, width='stretch')
            
            # Create Seaborn violin plot for Score distribution by Subject
            # Seaborn is built on top of matplotlib and provides statistical visualizations
            # Violin plots show both the distribution shape and summary statistics
            with violin_placeholder.container():
                st.subheader("📋 Score Distribution by Subject")
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.violinplot(data=filtered_data, x='Subject', y='Score', ax=ax)
                ax.set_title("Violin Plot: Score Distribution Across Subjects")
                ax.set_ylabel("Score")
                ax.set_xlabel("Subject")
                st.pyplot(fig)
        else:
            # Display message when no data is available
            with kpi_placeholder.container():
                st.info("No data available. Start the live feed to begin collecting data.")
        
        # Wait 1 second before next update
        time.sleep(1)
        
        # Force Streamlit to rerun the script to update the display
        # This is necessary because Streamlit normally only reruns on user interaction
        st.rerun()
    
    # Display current data when not running
    if not st.session_state.student_data.empty:
        st.subheader("Current Data Snapshot")
        st.dataframe(st.session_state.student_data.tail(20))  # Show last 20 records
    else:
        st.info("Click 'Start Live Data Feed' in the sidebar to begin collecting real-time student data.")

if __name__ == "__main__":
    main()