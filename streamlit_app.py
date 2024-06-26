import streamlit as st
from pandasai import SmartDataframe
from pandasai.callbacks import BaseCallback
from pandasai.llm import GooglePalm
from pandasai.responses.response_parser import ResponseParser
import pandas as pd
import os
import shutil

# Ensure the uploaded_files directory exists
upload_dir = "uploaded_files"
os.makedirs(upload_dir, exist_ok=True)

class StreamlitCallback(BaseCallback):
    def __init__(self, container) -> None:
        """Initialize callback handler."""
        self.container = container

    def on_code(self, response: str):
        """Override this method to prevent displaying the code."""
        pass  # Do nothing to avoid showing the code in the dashboard

class StreamlitResponse(ResponseParser):
    def __init__(self, context) -> None:
        super().__init__(context)

    def format_dataframe(self, result):
        st.dataframe(result["value"])
        return

    def format_plot(self, result):
        st.image(result["value"])
        return

    def format_other(self, result):
        st.write(result["value"])
        return

st.markdown('<style>h1 { color: #8c03fc; }</style>', unsafe_allow_html=True)
st.write("# Chat with Excel & CSV Data")

# Function to clear uploaded_files directory
def clear_uploaded_files(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            st.error(f"Failed to delete {file_path}. Reason: {e}")

# File upload section
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx", "xls"])
if uploaded_file:
    # Clear existing files
    clear_uploaded_files(upload_dir)

    # Save uploaded file to local directory
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"Saved file: {uploaded_file.name}")

    # Read the uploaded file
    file_extension = uploaded_file.name.split('.')[-1]
    if file_extension == 'csv':
        df = pd.read_csv(file_path)
    elif file_extension in ['xlsx', 'xls']:
        df = pd.read_excel(file_path)

    # Convert all column names to strings to avoid mixed type issues
    df.columns = df.columns.astype(str)

    with st.expander("🔎 Dataframe Preview"):
        st.write(df.tail(3))

    query = st.text_area("🗣️ Chat with Dataframe")
    container = st.container()

    if st.button("Enter"):
        if query:
            llm = GooglePalm(api_key="AIzaSyCzkOddpqfMmvWXy8SxFQVl55DkEnpOxqM")
            query_engine = SmartDataframe(
                df,
                config={
                    "llm": llm,
                    "response_parser": StreamlitResponse,
                    "callback": StreamlitCallback(container),
                },
            )

            answer = query_engine.chat(query)
else:
    st.info("Please upload a CSV or Excel file to proceed.")
