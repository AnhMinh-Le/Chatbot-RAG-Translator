import os
from dotenv import load_dotenv
import streamlit as st
from langchain_community.llms import HuggingFaceHub
from langchain.chains.question_answering import load_qa_chain
from translate import *

from pdf_process import *

def load_huggingface_api_key():
    dotenv_path = "huggingface.env"
    load_dotenv(dotenv_path)
    huggingface_api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not huggingface_api_key:
        raise ValueError(f"Lỗi không lấy được HUGGINGFACEHUB_API_TOKEN từ {dotenv_path}")
    return huggingface_api_key

def create_llama_model():
    huggingface_api_key = load_huggingface_api_key()
    llama_model = HuggingFaceHub(
        repo_id="meta-llama/Meta-Llama-3.1-8B",
        model_kwargs={"temperature": 0},
        huggingfacehub_api_token=huggingface_api_key
    )
    return llama_model

def main():
    st.set_page_config(page_title="📄 Chatbot Hỗ Trợ Đọc PDF Nước Ngoài", layout="wide")

    st.title("📄 Chatbot Hỗ Trợ Đọc PDF Nước Ngoài")
    st.write("Bởi **Lê Anh Minh**")

    try:
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = load_huggingface_api_key()
    except ValueError as e:
        st.error(str(e))
        return

    uploaded_files = st.file_uploader("Đăng tệp tin PDF tại đây", type=['pdf'], accept_multiple_files=True)

    if uploaded_files:
        st.write("Đang xử lí tệp tin...")
        raw_text = extract_text_from_pdfs(uploaded_files)
        knowledgeBase = process_text(raw_text)
        st.write("Tệp tin đã xử lí xong")
        query = st.text_input("Bạn muốn tìm hiểu gì về nội dung tệp tin này?")

        if query:
            query_en = translate_vi_to_en(query, api_token)

            docs = knowledgeBase.similarity_search(query_en)
            llm = create_llama_model()
            chain = load_qa_chain(llm, chain_type='stuff')

            response_en = chain.run(input_documents=docs, question=query_en)

            response_vi = translate_en_to_vi(response_en, api_token)

            st.subheader('Câu trả lời: ')
            st.write(response_vi)


    elif uploaded_files is None:
        st.write("Định dạng file không hợp lệ hoặc file không tồn tại!")

if __name__ == '__main__':
    main()
