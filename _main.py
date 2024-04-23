import streamlit as st
from datetime import date, datetime
import pandas as pd
import os
import shutil
from utilities import setup_session, download_pdf
from getdata import fetch_data
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings, StorageContext, load_index_from_storage, Prompt
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.postprocessor.flag_embedding_reranker import FlagEmbeddingReranker
from llama_index.postprocessor.colbert_rerank import ColbertRerank
from llama_parse import LlamaParse

# Initialize session with custom settings
session = setup_session()
# Define global variables for directory paths
DATA_DIR = './data'
PERSIST_DIR = './storage'
# Set API keys and other configuration as environment variables
os.environ["LLAMA_CLOUD_API_KEY"] = "llx-lvCVaeyLE4mdQ8mayBSvU2IyK2vjpkKn3dnkAjAEK1lEDNPm"
os.environ["OPENAI_API_KEY"] = "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"
token = os.getenv('API_TOKEN', '8423494c9f5965bd44905b027a75f706')
ma_don_vi = '0'
url_loai_van_ban = 'https://angiang-api.vnptioffice.vn/api/danh-muc/danh-sach-loai-van-ban-no-authen'
url_co_quan = 'https://angiang-api.vnptioffice.vn/api/can-bo/ds-dv-by-chuoi-loai-don-vi'
url_van_ban_di = 'https://angiang-api.vnptioffice.vn/api/van-ban-di/ds-vb-cong-khai-an-giang'
data_van_ban_di = {
        'den_ngay': '21/02/2024',
        'ma_don_vi': '1088',
        'loai_van_ban': 'Công văn',
        'nam': '2024',
        'page': '1',
        'size': '5',
        'token': '8423494c9f5965bd44905b027a75f706',
        'tu_khoa': 'số',
        'tu_ngay': '21/01/2024',
    }
# Khai báo biến toàn cục để lưu trữ các item PDF
if 'global_pdf_items' not in st.session_state:
    st.session_state.global_pdf_items = []

# Function to get initial data
@st.cache_data(ttl=3600, show_spinner=True)
def get_initial_data():
    loai_van_ban_data = fetch_data(token, ma_don_vi, 'get', url_loai_van_ban)
    co_quan_data = fetch_data(token, ma_don_vi, 'get', url_co_quan)
    return loai_van_ban_data, co_quan_data

loai_van_ban_data, co_quan_data = get_initial_data()

def embedding():
    # Your embedding function code, but now use DATA_DIR and PERSIST_DIR as needed
    global DATA_DIR, PERSIST_DIR
    if 'embedding_initialized' not in st.session_state or not st.session_state.embedding_initialized:
        if 'recursive_query_engine' not in st.session_state:
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR)
                print(f"Thư mục {DATA_DIR} đã được tạo.")
            # Tải từng PDF file
            for pdf_item in st.session_state.global_pdf_items:
                ten_file = pdf_item.split("__")[-1]
                url = f'https://angiang-file.vnptioffice.vn/api/file-manage/read-file-not-login/{pdf_item}/view/{ten_file}'
                    
                # Tạo đường dẫn file để lưu trữ
                file_path = os.path.join(DATA_DIR, ten_file)
                
                # Gọi hàm tải PDF
                download_pdf(url, file_path, session)
            
            if not os.path.exists(PERSIST_DIR):
                parser = LlamaParse(
                    api_key="llx-lvCVaeyLE4mdQ8mayBSvU2IyK2vjpkKn3dnkAjAEK1lEDNPm",  # can also be set in your env as LLAMA_CLOUD_API_KEY
                    result_type="markdown",  # "markdown" and "text" are available
                    verbose=True
                )

                file_extractor = {".pdf": parser}
                documents = SimpleDirectoryReader(input_dir=DATA_DIR, file_extractor=file_extractor).load_data()
                raw_index = VectorStoreIndex.from_documents(documents)
                # Persist index to disk
                raw_index.storage_context.persist("storage")
            else:# Rebuild storage context
                storage_context = StorageContext.from_defaults(persist_dir="storage")
                # Load index from the storage context
                raw_index = load_index_from_storage(storage_context)
            
            template = (
                "We have provided context information below. \n"
                "---------------------\n"
                "{context_str}"
                "\n---------------------\n"
                "Given this information, please answer the question and each answer should start with code word AI Demos: {query_str}. Answer in Vietnamese\n"
            )
            qa_template = Prompt(template)
            raw_query_engine = raw_index.as_query_engine(text_qa_template=qa_template, similarity_top_k=15)
            st.session_state.recursive_query_engine = raw_query_engine
            st.session_state.embedding_initialized = True

    # raw_query_engine = raw_index.as_query_engine(similarity_top_k=15, node_postprocessors=[reranker])
    # print(len(nodes))
def chat(new_question):
    if 'recursive_query_engine' in st.session_state and st.session_state.recursive_query_engine is not None:
        # Sử dụng recursive_query_engine từ st.session_state
        # response = st.session_state.recursive_query_engine.query(new_question)
        response = st.session_state.recursive_query_engine.query(new_question)
        return response
    else:
        # Khởi tạo nếu cần thiết
        embedding()
        if 'recursive_query_engine' in st.session_state and st.session_state.recursive_query_engine is not None:
            # response = st.session_state.recursive_query_engine.query(new_question)
            response = st.session_state.recursive_query_engine.query(new_question)
            return response
        else:
            return "Engine tìm kiếm chưa sẵn sàng. Khởi tạo thất bại."


    # query = "tóm tắt nội dung TIẾN ĐỘ TRIỂN KHAI CÁC NHIỆM VỤ ĐƯỢC PHÂN CÔNG. theo đó,sở thông tin và truyền thông đã làm gì? nêu các tồn tại, hạn chế? Answer in VietNamese"

    # response_1 = raw_query_engine.query(query)
    # st.info("\n***********New LlamaParse+ Basic Query Engine***********")
    # st.success(response_1)

    # response_2 = recursive_query_engine.query(query)
    # st.info("\n***********New LlamaParse+ Recursive Retriever Query Engine***********")
    # st.success(response_2)
    #########################
        
# Initialize session state for date inputs if not already present
if 'tu_ngay' not in st.session_state:
    st.session_state['tu_ngay'] = date.today()
if 'den_ngay' not in st.session_state:
    st.session_state['den_ngay'] = date.today()
# Khởi tạo session_state cho df_filtered_data nếu chưa có
if 'df_filtered_data' not in st.session_state:
    st.session_state.df_filtered_data = pd.DataFrame()
# Sử dụng st.form để nhóm các thành phần nhập liệu và nút submit
with st.form(key='question_form'):
    new_question = st.text_input("Câu hỏi:", value="")  # Đặt giá trị mặc định là chuỗi rỗng
    submit_button = st.form_submit_button(label='Gửi câu hỏi')

if submit_button:
    if new_question:  # Kiểm tra xem chuỗi có nội dung hay không
        response = chat(new_question)
        st.success(response)
    else:
        st.error("Vui lòng nhập câu hỏi trước khi gửi.")  # Hiển thị thông báo nếu trường nhập liệu rỗng

# Kiểm tra và hiển thị df_filtered_data nếu có
if not st.session_state.df_filtered_data.empty:
    st.title('Danh sách văn bản')
    st.table(st.session_state.df_filtered_data)

with st.sidebar.form("search_form"):
    st.write("Form Tìm Kiếm")
    tu_khoa = st.text_input("Từ khóa")

    # Dropdown for document types
    loai_van_ban_options = [(item["ma_loai_van_ban_kc"], item["ten_loai_van_ban"]) for item in loai_van_ban_data["data"]]
    loai_van_ban_options.insert(0, ("0", "Tất cả"))
    loai_van_ban_selected = st.selectbox("Loại văn bản", options=loai_van_ban_options, format_func=lambda x: x[1])[1]

    # Dropdown for issuing agencies
    co_quan_options = [(item["ma_don_vi_kc"], item["ten_don_vi_rut_gon"]) for item in co_quan_data["data"]]
    default_index = 9  # Example default index
    co_quan_selected = st.selectbox("Cơ quan ban hành", options=co_quan_options, format_func=lambda x: x[1], index=default_index)[0]

    tu_ngay = st.date_input("Từ ngày", value=st.session_state.tu_ngay, min_value=date(2020, 1, 1), max_value=datetime.today().date(), key='tu_ngay')
    den_ngay = st.date_input("Đến ngày", value=st.session_state.den_ngay, min_value=date(2020, 1, 1), max_value=datetime.today().date(), key='den_ngay')

    search_submit_button  = st.form_submit_button("Tìm kiếm")
if search_submit_button:
    
    if os.path.exists(DATA_DIR):
        # Remove the directory and all its contents
        shutil.rmtree(DATA_DIR)
        print(f"Thư mục {DATA_DIR} đã được xóa.")
    if os.path.exists(PERSIST_DIR):
        # Remove the directory and all its contents
        shutil.rmtree(PERSIST_DIR)
        print(f"Thư mục {PERSIST_DIR} đã được xóa.")
    # Hiển thị thông báo với giá trị của Loại văn bản đã chọn
    # st.success(f"Loại văn bản được chọn: {loai_van_ban_selected}")
    # st.success(f"Cơ quan được chọn: {co_quan_selected}")
    
    # Validate date logic and provide user feedback instead of modifying den_ngay directly
    if den_ngay < tu_ngay:
        st.error("Đến ngày không thể nhỏ hơn Từ ngày. Vui lòng chọn lại.")
    # else:
        # Proceed with processing as dates are logically consistent
        # st.success(f"Từ ngày: {tu_ngay.strftime('%Y-%m-%d')}, Đến ngày: {den_ngay.strftime('%Y-%m-%d')}")
        # Further processing logic here

    # Cập nhật `data_van_ban_di` với các giá trị từ form
    data_van_ban_di.update({
        'tu_khoa': tu_khoa,
        # Update 'loai_van_ban' based on the selected option
        'loai_van_ban': '' if loai_van_ban_selected == "Tất cả" else loai_van_ban_selected,
        'ma_don_vi': str(int(float(co_quan_selected))),
        'tu_ngay': tu_ngay.strftime('%d/%m/%Y'),  # Adjusted to match expected format
        'den_ngay': den_ngay.strftime('%d/%m/%Y'),
    })

    data_json = fetch_data(token, '0', 'post', url_van_ban_di, data=data_van_ban_di)
    # st.success(f"Thông số: {data_van_ban_di}")
    # st.success(f"Kết quả: {data_json}")

    if data_json and "data" in data_json:
        # Tạo dữ liệu lọc
        filtered_data = []
        for item in data_json["data"]:
            # Lọc và trích xuất các item PDF
            pdf_items = [item for item in item.get("file_van_ban_bs", "").split(":") if item.endswith(".pdf")]
            
            # Thêm vào dữ liệu lọc
            filtered_data.append({
                # "File": pdf_items,
                "Số ký hiệu": item.get("so_ky_hieu", ""),
                "Trích yếu": item.get("trich_yeu", ""),
                "Ngày ban hành": item.get("ngay_ban_hanh", ""),
                "Tên cán bộ soạn": item.get("ten_can_bo_soan", ""),
                "Cơ quan ban hành": item.get("co_quan_ban_hanh_rut_gon", "")
            })
            
            # Thêm các item PDF vào biến toàn cục
            st.session_state.global_pdf_items.extend(pdf_items)
        # Tạo DataFrame từ dữ liệu lọc
        df_filtered_data = pd.DataFrame(filtered_data)
        df_filtered_data.index += 1
        
        st.session_state.df_filtered_data = pd.DataFrame(filtered_data)
        st.title('Danh sách văn bản')        
        st.table(df_filtered_data)
    else:
        st.write("Không có dữ liệu để hiển thị.")
    # Bổ sung khu vực cho Q&A
# Sử dụng st.form để nhóm các thành phần nhập liệu và nút submit
# with st.form(key='question_form'):
#     new_question = st.text_input("Câu hỏi:")
#     submit_button = st.form_submit_button(label='Gửi câu hỏi')

# if submit_button:
#     response = chat(new_question)
#     st.success(response)