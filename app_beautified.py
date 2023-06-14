import streamlit as st
from databricks_api import DatabricksAPI
import requests, json, tempfile, os

# getting environment variables
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center; font-size: 5em; color: orange;'>Q&A Bot using Dolly</h1>", unsafe_allow_html=True)
col1, _, col2 = st.columns([1, 0.5, 2])

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_TOKEN =os.getenv("DATABRICKS_TOKEN")
API_endpoint = os.getenv("API_endpoint")
# print(DATABRICKS_HOST)
# print(DATABRICKS_TOKEN)


def res(query=str):
    response = requests.request(method='POST',
                                headers={'Authorization': f'Bearer {DATABRICKS_TOKEN}'},
                                url=API_endpoint,
                                data=query)
    print(response.content)
    return response.content

def main():
    col1.header("Upload PDF Text")
    col2.header("Ask your PDF 💬")

    pdf = col1.file_uploader("Upload your PDF") #, type=["pdf"])

    if pdf is not None:
        if col1.button(f"Upload"):
            file_details = {"FileName": pdf.name, "FileType": pdf.type}
            # st.write(file_details)

            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(pdf.read())
                file_path = temp_file.name

            # st.write("File Path:", file_path)

            db = DatabricksAPI(host=DATABRICKS_HOST, token=DATABRICKS_TOKEN)
            progress_text = col1.empty()
            progress_text.text("File is being indexed...")
            db.dbfs.put(path=f"dbfs:/data/{pdf.name}",
                        src_path=file_path,
                        overwrite=True)
            os.remove(file_path)
            progress_text.empty()
            prog_text = col1.empty()
            prog_text.text(f"{pdf.name} \n Indexed Successfully")

    user_question = col2.text_input("Ask a question about your PDF:")
    # if col2.button(f"Submit_{hash('query')}"):
    if col2.button(f"Submit query"):
        if user_question:
            response = res(user_question)
            generated_text = json.loads(response)
            col2.write(generated_text)

if __name__ == '__main__':
    main()
