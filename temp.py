# dummy pyfile

import streamlit as st
import pandas as pd
import os

from reportlab.pdfgen import canvas

st.write("Here's our first attempt at using data to create a table:")
st.write(pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
}))

# Create a section header
st.header("Download PDF")


current_directory = os.getcwd()
path = current_directory + '/example.pdf'
# path = current_directory + '/dummy.txt'

pdf_url = "[DownloadPDF](" + path + ")"
print(pdf_url)
# Provide a link to download the PDF
# st.markdown("[Download PDF](sandbox:/" + pdf_url + "f)", unsafe_allow_html=True)
st.markdown(pdf_url, unsafe_allow_html=True)

# st.title("Download PDF Example")

# def download_pdf():
#     with open(path, "rb") as pdf_file:
#         pdf_contents = pdf_file.read()
    
#     print(pdf_contents)
#     st.download_button(label="Download PDF", data=path, key="download_button")

# if st.button("Download PDF"):
#     download_pdf()