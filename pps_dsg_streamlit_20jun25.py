import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.lines import Line2D

# Configure Streamlit page - side panel always open
st.set_page_config(
    page_title="District Performance Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Force sidebar to be visible and expanded */
    section[data-testid="stSidebar"] {
        display: block !important;
        width: 21rem !important;
        min-width: 21rem !important;
    }
    
    /* Hide the sidebar collapse button */
    button[kind="header"] {
        display: none !important;
    }
    
    /* Force sidebar content to be visible */
    .sidebar .sidebar-content {
        display: block !important;
    }
    
    .stPlotlyChart, .stPyplot {
        height: 500px !important;
    }
    .main h1 {
        font-size: 2rem !important;
        margin-bottom: 1rem !important;
    }
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("final_merged_assess_demo_df.csv", low_memory=False)

full_df = load_data()

# Define consistent colors (matplotlib default colors)
COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# Sidebar for navigation
st.sidebar.title("Dashboard Navigation")
page = st.sidebar.selectbox("Select Analysis", [
    "Chronic Absenteeism", 
    "Per Pupil Spending", 
    "4-Year Graduation Rate",
    "5/6-Year Graduation Rate",
    "Academic Achievement"
])

# Helper function to create seaborn KDE plot
def create_kde_plot(data, ax, label, color):
    """Create KDE plot using seaborn"""
    if len(data) > 0:
        sns.kdeplot(data, label=label, ax=ax, color=color, linewidth=2)
        return color
    return None

# Helper function to create summary table
def create_summary_table(df, year, metric_col, statewide_col, groups, format_func):
    table_data = []
    for group in groups:
        portland_val = df[
            (df['Year'] == year) &
            (df['District Name'] == 'Portland Public Schools') &
            (df['Population'] == group)
        ][metric_col]
        
        if portland_val.dtype == 'object':
            portland_val = pd.to_numeric(portland_val.str.replace('%', '').str.replace(',', ''), errors='coerce').dropna()
        else:
            portland_val = pd.to_numeric(portland_val, errors='coerce').dropna()

        state_val = df[
            (df['Year'] == year) &
            (df['Population'] == group)
        ][statewide_col]
        
        if state_val.dtype == 'object':
            state_val = pd.to_numeric(state_val.str.replace('%', '').str.replace(',', ''), errors='coerce').dropna()
        else:
            state_val = pd.to_numeric(state_val, errors='coerce').dropna()

        table_data.append([
            group,
            format_func(portland_val.iloc[0]) if not portland_val.empty else 'N/A',
            format_func(state_val.mean()) if not state_val.empty else 'N/A'
        ])
    return table_data

# Chronic Absenteeism Page
if page == "Chronic Absenteeism":
    st.title("Chronic Absenteeism Analysis")
    st.write("Distribution of chronic absenteeism rates across Maine school districts")
    
    years = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
    selected_year = st.radio("Select Year", years, index=6, horizontal=True)
    
    fig, ax = plt.subplots(figsize=(7, 3.5))
    
    for i, pop in enumerate(full_df['Population'].unique()):
        data = full_df[
            (full_df['Year'] == selected_year) &
            (full_df['Population'] == pop)
        ]['Percentage of Students Chronically Absent']
        data = pd.to_numeric(data.str.replace('%', ''), errors='coerce').dropna()
        
        if not data.empty:
            color = create_kde_plot(data, ax, pop, COLORS[i % len(COLORS)])
            
            # Add Portland line
            portland_val = full_df[
                (full_df['Year'] == selected_year) &
                (full_df['Population'] == pop) &
                (full_df['District Name'] == 'Portland Public Schools')
            ]['Percentage of Students Chronically Absent']
            portland_val = pd.to_numeric(portland_val.str.replace('%', ''), errors='coerce').dropna()
            
            if not portland_val.empty:
                ax.axvline(portland_val.iloc[0], color=COLORS[i % len(COLORS)], linestyle=':', linewidth=2)

    ax.set_xlabel('Percentage of Students Chronically Absent')
    ax.set_ylabel('Density')
    ax.set_title(f'Statewide Distribution of Chronic Absenteeism: {selected_year}')
    ax.set_xlim(0, 90)
    
    # Add legend
    dotted_line_legend = Line2D([], [], color='black', linestyle=':', linewidth=2, label='Portland Public Schools')
    handles, labels = ax.get_legend_handles_labels()
    handles.append(dotted_line_legend)
    labels.append('Portland Public Schools')
    ax.legend(handles, labels, title="Population", loc='upper right')
    
    st.pyplot(fig)
    
    # Summary table
    groups = ["All Students", "Economically Disadvantaged", "Students with Disabilities"]
    table_data = create_summary_table(
        full_df, selected_year, 
        'Percentage of Students Chronically Absent', 
        'Statewide - Percentage of Students Chronically Absent',
        groups, 
        lambda x: f"{x:.1f}%"
    )
    
    st.subheader("Portland vs State Comparison")
    df_table = pd.DataFrame(table_data, columns=["Population", "Portland", "State"])
    st.table(df_table)

# Per Pupil Spending Page
elif page == "Per Pupil Spending":
    st.title("Per Pupil Spending Analysis")
    st.write("Distribution of per pupil spending across Maine school districts")
    
    years = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
    selected_year = st.radio("Select Year", years, index=6, horizontal=True)
    
    fig, ax = plt.subplots(figsize=(7, 3.5))
    
    for i, pop in enumerate(full_df['Population'].unique()):
        data = full_df[
            (full_df['Year'] == selected_year) &
            (full_df['Population'] == pop)
        ]['Per Pupil Amount']
        data = pd.to_numeric(data.str.replace(',', ''), errors='coerce').dropna()
        
        if not data.empty:
            color = create_kde_plot(data, ax, pop, COLORS[i % len(COLORS)])
            
            # Add Portland line
            portland_val = full_df[
                (full_df['Year'] == selected_year) &
                (full_df['Population'] == pop) &
                (full_df['District Name'] == 'Portland Public Schools')
            ]['Per Pupil Amount']
            portland_val = pd.to_numeric(portland_val.str.replace(',', ''), errors='coerce').dropna()
            
            if not portland_val.empty:
                ax.axvline(portland_val.iloc[0], color=COLORS[i % len(COLORS)], linestyle=':', linewidth=2)

    ax.set_xlabel('Per Pupil Amount ($)')
    ax.set_ylabel('Density')
    ax.set_title(f'Statewide Distribution of Per Pupil Spending: {selected_year}')
    ax.set_xlim(5000, 35000)
    
    # Add legend
    dotted_line_legend = Line2D([], [], color='black', linestyle=':', linewidth=2, label='Portland Public Schools')
    handles, labels = ax.get_legend_handles_labels()
    handles.append(dotted_line_legend)
    labels.append('Portland Public Schools')
    ax.legend(handles, labels, title="Population", loc='upper right')
    
    st.pyplot(fig)
    
    # Summary table
    groups = ["All Students", "Economically Disadvantaged", "Students with Disabilities"]
    table_data = create_summary_table(
        full_df, selected_year, 
        'Per Pupil Amount', 
        'Statewide Per Pupil',
        groups, 
        lambda x: f"${x:,.0f}"
    )
    
    st.subheader("Portland vs State Comparison")
    df_table = pd.DataFrame(table_data, columns=["Population", "Portland", "State"])
    st.table(df_table)

# 4-Year Graduation Rate Page
elif page == "4-Year Graduation Rate":
    st.title("4-Year Graduation Rate Analysis")
    st.write("Distribution of 4-year graduation rates across Maine school districts")
    
    years = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
    selected_year = st.radio("Select Year", years, index=6, horizontal=True)

    fig, ax = plt.subplots(figsize=(7, 3.5))
    
    for i, pop in enumerate(full_df['Population'].unique()):
        data = full_df[
            (full_df['Year'] == selected_year) &
            (full_df['Population'] == pop)
        ]['Four Year Graduation Rate']
        
        if data.dtype == 'object':
            data = pd.to_numeric(data.str.replace('%', ''), errors='coerce').dropna()
        else:
            data = pd.to_numeric(data, errors='coerce').dropna()
        
        if not data.empty:
            color = create_kde_plot(data, ax, pop, COLORS[i % len(COLORS)])
            
            # Add Portland line
            portland_val = full_df[
                (full_df['Year'] == selected_year) &
                (full_df['Population'] == pop) &
                (full_df['District Name'] == 'Portland Public Schools')
            ]['Four Year Graduation Rate']
            
            if portland_val.dtype == 'object':
                portland_val = pd.to_numeric(portland_val.str.replace('%', ''), errors='coerce').dropna()
            else:
                portland_val = pd.to_numeric(portland_val, errors='coerce').dropna()
                
            if not portland_val.empty:
                ax.axvline(portland_val.iloc[0], color=COLORS[i % len(COLORS)], linestyle=':', linewidth=2)

    ax.set_xlabel('Four Year Graduation Rate (%)')
    ax.set_ylabel('Density')
    ax.set_title(f'Statewide Distribution of Four Year Graduation Rates: {selected_year}')
    ax.set_xlim(20, 100)
    
    # Add legend
    dotted_line_legend = Line2D([], [], color='black', linestyle=':', linewidth=2, label='Portland Public Schools')
    handles, labels = ax.get_legend_handles_labels()
    handles.append(dotted_line_legend)
    labels.append('Portland Public Schools')
    ax.legend(handles, labels, title="Population", loc='upper left')
    
    st.pyplot(fig)
    
    # Summary table
    groups = ["All Students", "Economically Disadvantaged", "Students with Disabilities"]
    table_data = create_summary_table(
        full_df, selected_year, 
        'Four Year Graduation Rate', 
        'Four Year Statewide Graduation Rate',
        groups, 
        lambda x: f"{x:.1f}%"
    )
    
    st.subheader("Portland vs State Comparison")
    df_table = pd.DataFrame(table_data, columns=["Population", "Portland", "State"])
    st.table(df_table)

# 5/6-Year Graduation Rate Page
elif page == "5/6-Year Graduation Rate":
    st.title("5/6-Year Graduation Rate Analysis")
    st.write("Distribution of 5/6-year graduation rates across Maine school districts")
    
    years = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
    selected_year = st.radio("Select Year", years, index=6, horizontal=True)
    
    fig, ax = plt.subplots(figsize=(7, 3.5))
    
    for i, pop in enumerate(full_df['Population'].unique()):
        data = full_df[
            (full_df['Year'] == selected_year) &
            (full_df['Population'] == pop)
        ]['Five/Six Year Graduation Rate']
        
        if data.dtype == 'object':
            data = pd.to_numeric(data.str.replace('%', ''), errors='coerce').dropna()
        else:
            data = pd.to_numeric(data, errors='coerce').dropna()
        
        if not data.empty:
            color = create_kde_plot(data, ax, pop, COLORS[i % len(COLORS)])
            
            # Add Portland line
            portland_val = full_df[
                (full_df['Year'] == selected_year) &
                (full_df['Population'] == pop) &
                (full_df['District Name'] == 'Portland Public Schools')
            ]['Five/Six Year Graduation Rate']
            
            if portland_val.dtype == 'object':
                portland_val = pd.to_numeric(portland_val.str.replace('%', ''), errors='coerce').dropna()
            else:
                portland_val = pd.to_numeric(portland_val, errors='coerce').dropna()
                
            if not portland_val.empty:
                ax.axvline(portland_val.iloc[0], color=COLORS[i % len(COLORS)], linestyle=':', linewidth=2)

    ax.set_xlabel('Five/Six Year Graduation Rate (%)')
    ax.set_ylabel('Density')
    ax.set_title(f'Statewide Distribution of Five/Six Year Graduation Rates: {selected_year}')
    ax.set_xlim(30, 100)
    
    # Add legend
    dotted_line_legend = Line2D([], [], color='black', linestyle=':', linewidth=2, label='Portland Public Schools')
    handles, labels = ax.get_legend_handles_labels()
    handles.append(dotted_line_legend)
    labels.append('Portland Public Schools')
    ax.legend(handles, labels, title="Population", loc='upper left')
    
    st.pyplot(fig)
    
    # Summary table
    groups = ["All Students", "Economically Disadvantaged", "Students with Disabilities"]
    table_data = create_summary_table(
        full_df, selected_year, 
        'Five/Six Year Graduation Rate', 
        'Five/Six Year Statewide Graduation Rate',
        groups, 
        lambda x: f"{x:.1f}%"
    )
    
    st.subheader("Portland vs State Comparison")
    df_table = pd.DataFrame(table_data, columns=["Population", "Portland", "State"])
    st.table(df_table)

# Academic Achievement Page
elif page == "Academic Achievement":
    st.title("Academic Achievement Analysis")
    st.write("Students performing at or above state expectations")
    
    years = ["2015-2016", "2016-2017", "2017-2018", "2018-2019", "2022-2023", "2023-2024"]
    subjects = ['ELA', 'Math', 'Science']
    
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.radio("Select Year", years, index=5, horizontal=True)
    with col2:
        selected_subject = st.selectbox("Select Subject", subjects)
    
    fig, ax = plt.subplots(figsize=(7, 3.5))
    
    # Filter for achievement levels to combine
    at_or_above_df = full_df[full_df['Achievement Level'] == 'At or Above State Expectations']
    at_df = full_df[full_df['Achievement Level'] == 'At State Expectations']
    above_df = full_df[full_df['Achievement Level'] == 'Above State Expectations']
    filtered_df = pd.concat([at_or_above_df, at_df, above_df], ignore_index=True)
    
    subject_column = f'Percentage of Students at Achievement Level_{selected_subject}'
    
    for i, pop in enumerate(filtered_df['Population'].unique()):
        pop_year_data = filtered_df[
            (filtered_df['Year'] == selected_year) &
            (filtered_df['Population'] == pop)
        ]
        
        # Aggregate by district
        combined_data = []
        for district in pop_year_data['District Name'].unique():
            district_data = pop_year_data[pop_year_data['District Name'] == district]
            total_pct = 0
            count = 0
            
            for _, row in district_data.iterrows():
                val = row[subject_column]
                if pd.notna(val) and val != '*':
                    if isinstance(val, str):
                        numeric_val = pd.to_numeric(val.replace('%', ''), errors='coerce')
                    else:
                        numeric_val = pd.to_numeric(val, errors='coerce')
                    
                    if pd.notna(numeric_val):
                        total_pct += numeric_val
                        count += 1
            
            if count > 0:
                combined_data.append(total_pct)
        
        if combined_data:
            data = pd.Series(combined_data)
            color = create_kde_plot(data, ax, pop, COLORS[i % len(COLORS)])
            
            # Add Portland line
            portland_data = pop_year_data[pop_year_data['District Name'] == 'Portland Public Schools']
            portland_total = 0
            portland_count = 0
            
            for _, row in portland_data.iterrows():
                val = row[subject_column]
                if pd.notna(val) and val != '*':
                    if isinstance(val, str):
                        numeric_val = pd.to_numeric(val.replace('%', ''), errors='coerce')
                    else:
                        numeric_val = pd.to_numeric(val, errors='coerce')
                    
                    if pd.notna(numeric_val):
                        portland_total += numeric_val
                        portland_count += 1
            
            if portland_count > 0:
                ax.axvline(portland_total, color=COLORS[i % len(COLORS)], linestyle=':', linewidth=2)

    ax.set_xlabel(f'{selected_subject} Achievement - At or Above State Expectations (%)')
    ax.set_ylabel('Density')
    ax.set_title(f'Statewide Distribution of {selected_subject} Achievement: {selected_year}')
    ax.set_xlim(0, 100)
    
    # Add legend
    dotted_line_legend = Line2D([], [], color='black', linestyle=':', linewidth=2, label='Portland Public Schools')
    handles, labels = ax.get_legend_handles_labels()
    handles.append(dotted_line_legend)
    labels.append('Portland Public Schools')
    ax.legend(handles, labels, title="Population", loc='upper right')
    
    st.pyplot(fig)
    
    # Summary table for achievement
    groups = ["All Students", "Economically Disadvantaged", "Students with Disabilities"]
    table_data = []
    
    for group in groups:
        # Portland combined value
        portland_data = filtered_df[
            (filtered_df['Year'] == selected_year) &
            (filtered_df['District Name'] == 'Portland Public Schools') &
            (filtered_df['Population'] == group)
        ]
        
        portland_total = 0
        portland_count = 0
        for _, row in portland_data.iterrows():
            val = row[subject_column]
            if pd.notna(val) and val != '*':
                if isinstance(val, str):
                    numeric_val = pd.to_numeric(val.replace('%', ''), errors='coerce')
                else:
                    numeric_val = pd.to_numeric(val, errors='coerce')
                
                if pd.notna(numeric_val):
                    portland_total += numeric_val
                    portland_count += 1

        # State average of combined values
        group_data = filtered_df[
            (filtered_df['Year'] == selected_year) &
            (filtered_df['Population'] == group)
        ]
        
        district_totals = []
        for district in group_data['District Name'].unique():
            district_data = group_data[group_data['District Name'] == district]
            district_total = 0
            district_count = 0
            
            for _, row in district_data.iterrows():
                val = row[subject_column]
                if pd.notna(val) and val != '*':
                    if isinstance(val, str):
                        numeric_val = pd.to_numeric(val.replace('%', ''), errors='coerce')
                    else:
                        numeric_val = pd.to_numeric(val, errors='coerce')
                    
                    if pd.notna(numeric_val):
                        district_total += numeric_val
                        district_count += 1
            
            if district_count > 0:
                district_totals.append(district_total)

        table_data.append([
            group,
            f"{portland_total:.1f}%" if portland_count > 0 else 'N/A',
            f"{pd.Series(district_totals).mean():.1f}%" if district_totals else 'N/A'
        ])
    
    st.subheader("Portland vs State Comparison")
    df_table = pd.DataFrame(table_data, columns=["Population", "Portland", "State"])
    st.table(df_table)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Dashboard for District Decision Makers**")
st.sidebar.markdown("Compare Portland Public Schools performance against statewide distributions")