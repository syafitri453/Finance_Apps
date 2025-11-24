import streamlit as st
import pandas as pd
import plotly.express as px
import os  # Diperbaiki dari 'eo' menjadi 'os'
from groq import Groq
from dotenv import load_dotenv

# Load API key securely
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("API key is missing! Set it in Streamlit Secrets or a .env file.")
    st.stop()

# Streamlit App UI
st.set_page_config(
    page_title="Budget vs. Actuals AI", 
    page_icon="📊",  # Diperbaiki dari "**"**"
    layout="wide"
)

st.title("📊 Budget vs. Actuals AI - Variance Analysis & Commentary")
st.write("Upload your Budget vs. Actuals file and get AI-driven financial insights!")

# Initialize Groq client
try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"Error initializing Groq client: {e}")
    st.stop()

# File upload section
uploaded_file = st.file_uploader(
    "Upload Excel/CSV File", 
    type=['csv', 'xlsx', 'xls'],
    help="Upload your budget vs actuals file in CSV or Excel format"
)

if uploaded_file is not None:
    try:
        # Read file based on type
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("File uploaded successfully!")
        
        # Show data preview
        st.subheader("Data Preview")
        st.dataframe(df.head())
        
        # Basic data info
        st.subheader("Data Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Rows", len(df))
        
        with col2:
            st.metric("Total Columns", len(df.columns))
        
        with col3:
            st.metric("Data Types", f"{len(df.select_dtypes(include='number').columns)} numeric")
        
        # Show columns for user selection
        st.subheader("Column Selection")
        columns = df.columns.tolist()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            budget_col = st.selectbox("Select Budget Column", columns)
        
        with col2:
            actual_col = st.selectbox("Select Actual Column", columns)
        
        with col3:
            category_col = st.selectbox("Select Category Column (optional)", [""] + columns)
        
        # Calculate variances
        if budget_col and actual_col:
            df['Variance'] = df[actual_col] - df[budget_col]
            df['Variance_Percentage'] = (df['Variance'] / df[budget_col]) * 100
            
            # Show variance analysis
            st.subheader("Variance Analysis")
            
            # Summary metrics
            total_budget = df[budget_col].sum()
            total_actual = df[actual_col].sum()
            total_variance = total_actual - total_budget
            variance_percentage = (total_variance / total_budget) * 100
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Budget", f"${total_budget:,.2f}")
            
            with col2:
                st.metric("Total Actual", f"${total_actual:,.2f}")
            
            with col3:
                st.metric("Total Variance", f"${total_variance:,.2f}")
            
            with col4:
                st.metric("Variance %", f"{variance_percentage:.2f}%")
            
            # Show detailed table
            st.dataframe(df)
            
            # AI Analysis Section
            st.subheader("🤖 AI Analysis & Commentary")
            
            if st.button("Generate AI Insights"):
                with st.spinner("Analyzing data with AI..."):
                    try:
                        # Prepare data for AI analysis
                        analysis_data = df[[budget_col, actual_col, 'Variance', 'Variance_Percentage']].describe()
                        
                        # Create prompt for AI
                        prompt = f"""
                        Analyze this budget vs actuals data and provide financial insights:
                        
                        Total Budget: ${total_budget:,.2f}
                        Total Actual: ${total_actual:,.2f}
                        Total Variance: ${total_variance:,.2f} ({variance_percentage:.2f}%)
                        
                        Key statistics:
                        {analysis_data.to_string()}
                        
                        Please provide:
                        1. Overall performance summary
                        2. Key areas of concern (significant variances)
                        3. Recommendations for improvement
                        4. Positive highlights (if any)
                        
                        Keep the analysis professional and actionable.
                        """
                        
                        # Get AI response
                        chat_completion = client.chat.completions.create(
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a financial analyst expert in budget variance analysis."
                                },
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            model="llama3-8b-8192",
                            temperature=0.3,
                            max_tokens=1024
                        )
                        
                        ai_response = chat_completion.choices[0].message.content
                        
                        st.success("AI Analysis Complete!")
                        st.write(ai_response)
                        
                    except Exception as e:
                        st.error(f"Error in AI analysis: {e}")
            
            # Visualization Section
            st.subheader("📈 Visualizations")
            
            # Bar chart - Budget vs Actual
            if category_col:
                fig = px.bar(
                    df, 
                    x=category_col, 
                    y=[budget_col, actual_col],
                    title="Budget vs Actual by Category",
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Variance chart
            fig2 = px.bar(
                df, 
                y='Variance',
                title="Variance by Item",
                color='Variance',
                color_continuous_scale=['red', 'yellow', 'green']
            )
            st.plotly_chart(fig2, use_container_width=True)
                        
    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("👆 Please upload a CSV or Excel file to get started")

# Sidebar with instructions
with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    1. **Upload** your budget vs actuals file (CSV/Excel)
    2. **Select** the appropriate columns
    3. **View** automatic variance analysis
    4. **Generate** AI-powered insights
    5. **Explore** interactive visualizations
    
    ### Required Columns:
    - Budget amounts
    - Actual amounts  
    - Category (optional but recommended)
    """)
    
    st.header("API Setup")
    st.markdown("""
    Get your Groq API key:
    1. Visit [Groq Cloud](https://console.groq.com)
    2. Create account and get API key
    3. Set as environment variable:
    ```bash
    export GROQ_API_KEY="your-api-key"
    ```
    """)
