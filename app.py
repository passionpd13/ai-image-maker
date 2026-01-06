import streamlit as st
import requests
import random
import json
import time
import os
import re
import shutil
import zipfile
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from google import genai
from google.genai import types

# ==========================================
# [설정] 페이지 기본 설정
# ==========================================
st.set_page_config(
    page_title="열정피디 AI 씬 생성기 (Pro)", 
    layout="wide", 
    page_icon="🎨",
    initial_sidebar_state="expanded"
)

# ==========================================
# [디자인] 다크모드 & 빅 텍스트 CSS 적용
# ==========================================
st.markdown("""
    <style>
    /* [긴급 수정 1] 상단 흰색 바 제거 및 여백 삭제 */
    header[data-testid="stHeader"] {
        background-color: #0E1117 !important; /* 헤더 배경을 어둡게 */
        visibility: hidden !important; /* 헤더 숨김 */
    }
    .block-container {
        padding-top: 2rem !important; /* 상단 여백 최소화 */
        padding-bottom: 5rem !important;
    }

    /* 1. 기본 배경 및 폰트 설정 (다크모드 강제) */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF !important;
        font-family: 'Pretendard', 'Malgun Gothic', sans-serif;
    }
    
    /* 2. 전체 글씨 크기 확대 */
    p, div, label, span, li {
        font-size: 1.15rem !important; 
        line-height: 1.6;
        color: #FFFFFF !important;
    }

    /* 헤더 텍스트 색상 강제 */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }

    /* 3. 헤더 (수강생 전용 배너) 스타일 */
    .student-banner {
        background: linear-gradient(90deg, #7F00FF 0%, #E100FF 100%);
        color: white !important;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 30px;
        box-shadow: 0 0 20px rgba(225, 0, 255, 0.5);
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        letter-spacing: 2px;
    }

    /* 4. 입력창 라벨 (제목, 대본 등) 아주 크게 */
    .stTextInput label p, .stTextArea label p, .stSelectbox label p {
        font-size: 1.6rem !important; 
        font-weight: 700 !important;
        color: #FFD700 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
        margin-bottom: 10px !important;
    }
    
    /* [긴급 수정 2] 입력창 내부 텍스트 및 안내 문구(Placeholder) 색상 변경 */
    .stTextInput input, .stTextArea textarea {
        background-color: #262730 !important;
        color: #FFFFFF !important; /* 입력 글씨 흰색 */
        font-size: 1.3rem !important;
        font-weight: 500 !important;
        border-radius: 12px !important;
        border: 2px solid #4A4A4A !important;
    }
    
    /* 안내 문구(Placeholder) 색상 강제 지정 */
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #CCCCCC !important; /* 밝은 회색 */
        opacity: 1 !important; /* 투명도 제거 */
        font-weight: 500 !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #E100FF !important;
        box-shadow: 0 0 10px rgba(225, 0, 255, 0.3);
    }

    /* 5. 버튼 스타일 */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
        color: #FFFFFF !important;
        font-size: 1.6rem !important;
        font-weight: 900 !important;
        padding: 18px 30px !important;
        border-radius: 15px !important;
        border: 2px solid rgba(255,255,255,0.2) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        text-shadow: 1px 1px 3px rgba(0,0,0,0.6);
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(37, 117, 252, 0.7);
        color: #FFFFFF !important;
    }
    
    /* 6. 결과 카드 스타일 */
    [data-testid="stVerticalBlock"] > [style*="border"] {
        background-color: #1A1C24 !important;
        border: 1px solid #444 !important;
        border-radius: 20px !important;
        padding: 25px !important;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* 7. 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background-color: #161920;
        border-right: 1px solid #333;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #E0E0E0 !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #D0D0D0 !important;
    }

    /* 8. 타이틀 폰트 */
    h1 { font-size: 3.5rem !important; font-weight: 900 !important; color: #ffffff !important; }
    h2 { font-size: 2.5rem !important; font-weight: 800 !important; color: #E0E0E0 !important; }
    h3 { font-size: 2.0rem !important; font-weight: 700 !important; color: #E100FF !important; }

    /* 9. 다운로드 버튼 별도 스타일 */
    [data-testid="stDownloadButton"] > button {
        background: #333 !important;
        border: 2px solid #555 !important;
        color: #FFFFFF !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        border-color: #E100FF !important;
        color: #E100FF !important;
    }
    
    .streamlit-expanderHeader {
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 1.2rem !important;
    }
    </style>

    <div class="student-banner">
        🎓 열정피디 수강생 전용 (Pro) 🎓
    </div>
""", unsafe_allow_html=True)

# 파일 저장 경로 설정
BASE_PATH = "./web_result_files"
IMAGE_OUTPUT_DIR = os.path.join(BASE_PATH, "output_images")

# 텍스트 모델 설정 (프롬프트 작성용)
GEMINI_TEXT_MODEL_NAME = "gemini-2.5-pro" 

# ==========================================
# [함수] 1. 기본 유틸리티
# ==========================================
def init_folders():
    """이미지 저장 폴더 초기화"""
    if not os.path.exists(IMAGE_OUTPUT_DIR):
        os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)

def split_script_by_time(script, chars_per_chunk=100):
    """대본을 적절한 길이로 나누기"""
    temp_sentences = script.replace(".", ".|").replace("?", "?|").replace("!", "!|").split("|")
    chunks = []
    current_chunk = ""
    for sentence in temp_sentences:
        sentence = sentence.strip()
        if not sentence: continue
        if len(current_chunk) + len(sentence) < chars_per_chunk:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def make_filename(scene_num, text_chunk):
    """파일 이름 생성"""
    clean_line = text_chunk.replace("\n", " ").strip()
    clean_line = re.sub(r'[\\/:*?"<>|]', "", clean_line)
    words = clean_line.split()
    
    if len(words) <= 6:
        summary = " ".join(words)
    else:
        start_part = " ".join(words[:3])
        end_part = " ".join(words[-3:])
        summary = f"{start_part}...{end_part}"
    
    filename = f"S{scene_num:03d}_{summary}.png"
    return filename

def create_zip_buffer(source_dir):
    """폴더 압축"""
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.basename(file_path))
    buffer.seek(0)
    return buffer

# ==========================================
# [함수] 2. 프롬프트 생성 (한국어 고정 + Bright & Flat)
# ==========================================
def generate_prompt(api_key, index, text_chunk, style_instruction, video_title, genre_mode="info"):
    scene_num = index + 1
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_TEXT_MODEL_NAME}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}

    # [언어 고정] 무조건 한국어
    lang_guide = "화면 속 글씨는 **무조건 '한글(Korean)'로 표기**하십시오. (다른 언어 절대 금지)"
    lang_example = "(예: 'New York' -> '뉴욕', 'Tokyo' -> '도쿄')"

    # [모드 고정] 밝은 정보/이슈 (Bright & Flat)
    full_instruction = f"""
    [역할]
    당신은 복잡한 상황을 아주 쉽고 직관적인 그림으로 표현하는 '비주얼 커뮤니케이션 전문가'이자 '교육용 일러스트레이터'입니다.

    [전체 영상 주제]
    "{video_title}"

    [그림 스타일 가이드 - 절대 준수]
    {style_instruction}
    
    [필수 연출 지침]
    1. **조명(Lighting):** 무조건 **'밝고 화사한 조명(High Key Lighting)'**을 사용하십시오. 그림자가 짙거나 어두운 부분은 없어야 합니다.
    2. **색감(Colors):** 채도가 높고 선명한 색상을 사용하여 시인성을 높이십시오. (칙칙하거나 회색조 톤 금지)
    3. **구성(Composition):** 시청자가 상황을 한눈에 이해할 수 있도록 피사체를 화면 중앙에 명확하게 배치하십시오.
    4. **분위기(Mood):** 교육적이고, 중립적이며, 산뜻한 분위기여야 합니다. **(절대 우울하거나, 무섭거나, 기괴한 느낌 금지)**
    5. 분활화면으로 연출하지 말고 하나의 화면으로 연출한다.
    6. **[텍스트 언어]:** {lang_guide} {lang_example}
    - **[절대 금지]:** 화면의 네 모서리(Corners)나 가장자리(Edges)에 글자를 배치하지 마십시오. 글자는 반드시 중앙 피사체 주변에만 연출하십시오.
    7. 캐릭터의 감정도 느껴진다.

    [임무]
    제공된 대본 조각(Script Segment)을 바탕으로, 이미지 생성 AI가 그릴 수 있는 **구체적인 묘사 프롬프트**를 작성하십시오.
    
    [작성 요구사항]
    - **분량:** 최소 5문장 이상으로 상세하게 묘사.
    - **포함 요소:**
        - **캐릭터 행동:** 대본의 상황을 연기하는 캐릭터의 구체적인 동작.
        - **배경:** 상황을 설명하는 소품이나 장소 (배경은 깔끔하게).
        - **시각적 은유:** 추상적인 내용일 경우, 이를 설명할 수 있는 시각적 아이디어 (예: 돈이 날아가는 모습, 그래프가 하락하는 모습 등).
    
    [출력 형식]
    - **무조건 한국어(한글)**로만 작성하십시오.
    - 부가적인 설명 없이 **오직 프롬프트 텍스트만** 출력하십시오.
    """
    
    payload = {
        "contents": [{"parts": [{"text": f"지시사항(Instruction):\n{full_instruction}\n\n대본 내용(Script Segment):\n\"{text_chunk}\"\n\n이미지 프롬프트 결과:"}]}]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            try:
                prompt = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            except:
                prompt = text_chunk
            return (scene_num, prompt)
        elif response.status_code == 429:
            time.sleep(2)
            return (scene_num, f"일러스트 묘사: {text_chunk}")
        else:
            return (scene_num, f"Error generating prompt: {response.status_code}")
    except Exception as e:
        return (scene_num, f"Error: {e}")

# ==========================================
# [함수] 3. 이미지 생성 (API 제한 대응)
# ==========================================
def generate_image(client, prompt, filename, output_dir, selected_model_name):
    full_path = os.path.join(output_dir, filename)
    
    # 재시도 설정
    max_retries = 5
    
    # 안전 필터 설정
    safety_settings = [
        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"),
    ]

    for attempt in range(1, max_retries + 1):
        try:
            # 이미지 생성 요청
            response = client.models.generate_content(
                model=selected_model_name,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    image_config=types.ImageConfig(aspect_ratio="16:9"),
                    safety_settings=safety_settings 
                )
            )
            
            if response.parts:
                for part in response.parts:
                    if part.inline_data:
                        img_data = part.inline_data.data
                        image = Image.open(BytesIO(img_data))
                        image.save(full_path)
                        return full_path
            
            # 응답은 왔으나 이미지가 없는 경우
            print(f"⚠️ [시도 {attempt}/{max_retries}] 이미지 데이터 없음. 재시도... ({filename})")
            time.sleep(2)
            
        except Exception as e:
            error_msg = str(e)
            # 429 에러(속도 제한) 대응
            if "429" in error_msg or "ResourceExhausted" in error_msg:
                wait_time = (5 * attempt) + random.uniform(1, 3)
                print(f"🛑 [API 제한] {filename} - {wait_time:.1f}초 대기 후 재시도... (시도 {attempt})")
                time.sleep(wait_time)
            else:
                print(f"⚠️ [에러] {error_msg} ({filename}) - 5초 대기")
                time.sleep(5)
            
    return None

# ==========================================
# [UI] 사이드바 설정
# ==========================================
with st.sidebar:
    st.title("⚙️ 설정")
    
    # API Key 입력 로직 (에러 방지)
    api_key = ""
    try:
        if "general" in st.secrets and "google_api_key" in st.secrets["general"]:
            api_key = st.secrets["general"]["google_api_key"]
    except:
        pass

    if api_key:
        st.success("🔑 API Key가 로드되었습니다.")
    else:
        api_key = st.text_input("🔑 Google API Key", type="password", help="Google AI Studio 키 입력")
    
    st.markdown("---")
    
    st.subheader("🖼️ 모델 선택")
    model_choice = st.radio("모델:", ("나노바나나 프로", "나노바나나"), index=0)
    
    # [수정된 부분] 선택지 이름("나노바나나 프로")과 비교하도록 수정
    if "나노바나나 프로" in model_choice:
        SELECTED_IMAGE_MODEL = "gemini-3-pro-image-preview" 
    else:
        SELECTED_IMAGE_MODEL = "gemini-2.5-flash-image"
    
    st.markdown("---")
    st.subheader("⏱️ 장면 시간")
    chunk_duration = st.slider("초 단위:", 5, 60, 20, 5)
    chars_limit = chunk_duration * 8 
    
    st.markdown("---")
    
    # [설정 고정]
    SELECTED_GENRE_MODE = "info"

    st.subheader("🖌️ 그림체 지침")
    default_style = """
대사에 어울리는 2d 얼굴이 둥근 하얀색 스틱맨 연출로 설명과 이해가 잘되는 화면 자료 느낌으로 그려줘 상황을 잘 나타내게 분활화면으로 말고 하나의 장면으로
너무 어지럽지 않게, 글씨는 핵심 키워드 2~3만 나오게 한다
글씨가 너무 많지 않게 핵심만. 2D 스틱맨을 활용해 대본을 설명이 잘되게 설명하는 연출을 한다. 자막 스타일 연출은 하지 않는다.
글씨가 나올경우 핵심 키워드 중심으로만 나오게 너무 글이 많지 않도록 한다, 글자는 배경과 서물에 자연스럽게 연출, 전체 배경 연출은 2D로 디테일하게 몰입감 있게 연출해서 그려줘 (16:9)
다양한 장소와 상황 연출로 배경을 디테일하게 한다. 무조건 2D 스틱맨 연출
    """
    style_instruction = st.text_area("스타일 프롬프트", value=default_style.strip(), height=200)
    
    st.markdown("---")
    max_workers = st.slider("작업 속도", 1, 10, 5)

# ==========================================
# [UI] 메인 화면
# ==========================================
st.title("🎬 AI 씬(장면) 생성기 (Pro)")
st.caption(f"다크모드 & 빅 텍스트 에디션 | 🎨 Model: {SELECTED_IMAGE_MODEL}")

# 세션 초기화
if 'generated_results' not in st.session_state:
    st.session_state['generated_results'] = []
if 'video_title' not in st.session_state:
    st.session_state['video_title'] = ""

st.write("") # 여백

col_title_input, col_space = st.columns([3, 1])
with col_title_input:
    st.text_input(
        "📌 영상 제목/주제 (선택사항)",
        key="video_title", 
        placeholder="예: 부자들의 3가지 습관 (전체 분위기 결정)",
    )

st.write("") # 여백

script_input = st.text_area(
    "📜 대본 입력 (여기에 붙여넣기)", 
    height=350, 
    placeholder="안녕하세요. 오늘은..."
)

# [버튼 클릭 시 초기화 함수]
def clear_generated_results():
    st.session_state['generated_results'] = []

st.write("") # 여백
start_btn = st.button("🚀 이미지 생성 시작하기", type="primary", use_container_width=True, on_click=clear_generated_results)

if start_btn:
    if not api_key:
        st.error("⚠️ Google API Key를 사이드바에 입력해주세요.")
    elif not script_input:
        st.warning("⚠️ 대본을 입력해주세요.")
    else:
        # 초기화 및 폴더 준비
        st.session_state['generated_results'] = [] 
        if os.path.exists(IMAGE_OUTPUT_DIR):
            shutil.rmtree(IMAGE_OUTPUT_DIR)
        init_folders()
        
        client = genai.Client(api_key=api_key)
        
        status_box = st.status("작업 진행 중...", expanded=True)
        progress_bar = st.progress(0)
        
        # 1. 대본 분할
        status_box.write(f"✂️ 대본 분할 중...")
        chunks = split_script_by_time(script_input, chars_per_chunk=chars_limit)
        total_scenes = len(chunks)
        status_box.write(f"✅ {total_scenes}개 장면으로 분할 완료.")
        
        current_video_title = st.session_state.get('video_title', "").strip()
        if not current_video_title:
            current_video_title = "전반적인 대본 분위기에 어울리는 배경 (Context based on the script)"

        # 2. 프롬프트 생성 (병렬)
        status_box.write(f"📝 프롬프트 작성 중... (Mode: Bright & Flat)")
        prompts = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            for i, chunk in enumerate(chunks):
                futures.append(executor.submit(
                    generate_prompt, 
                    api_key, 
                    i, 
                    chunk, 
                    style_instruction, 
                    current_video_title, 
                    SELECTED_GENRE_MODE
                ))
            
            for i, future in enumerate(as_completed(futures)):
                prompts.append(future.result())
                progress_bar.progress((i + 1) / (total_scenes * 2))
        
        prompts.sort(key=lambda x: x[0])
        
        # 3. 이미지 생성 (병렬 처리)
        status_box.write(f"🎨 이미지 생성 중 ({SELECTED_IMAGE_MODEL})...")
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_meta = {}
            for s_num, prompt_text in prompts:
                idx = s_num - 1
                orig_text = chunks[idx]
                fname = make_filename(s_num, orig_text)
                
                # 순서 꼬임 방지 미세 지연
                time.sleep(0.1) 
                
                future = executor.submit(generate_image, client, prompt_text, fname, IMAGE_OUTPUT_DIR, SELECTED_IMAGE_MODEL)
                future_to_meta[future] = (s_num, fname, orig_text, prompt_text)
            
            # 결과 수집
            completed_cnt = 0
            for future in as_completed(future_to_meta):
                s_num, fname, orig_text, p_text = future_to_meta[future]
                path = future.result()
                
                if path:
                    results.append({
                        "scene": s_num,
                        "path": path,
                        "filename": fname,
                        "script": orig_text,
                        "prompt": p_text
                    })
                else:
                    st.error(f"Scene {s_num} 이미지 생성 최종 실패.")

                completed_cnt += 1
                progress_bar.progress(0.5 + (completed_cnt / total_scenes * 0.5))
        
        results.sort(key=lambda x: x['scene'])
        st.session_state['generated_results'] = results
        
        status_box.update(label="✅ 생성 완료!", state="complete", expanded=False)

# ==========================================
# [결과 화면] 리스트 및 재생성
# ==========================================
if st.session_state['generated_results']:
    st.divider()
    st.markdown(f"## 📸 결과물 ({len(st.session_state['generated_results'])}장)")
    
    # 전체 다운로드 버튼
    zip_data = create_zip_buffer(IMAGE_OUTPUT_DIR)
    st.download_button("📦 전체 이미지 ZIP 다운로드", data=zip_data, file_name="all_images.zip", mime="application/zip", use_container_width=True)
    
    st.markdown("---")

    # 개별 리스트 출력
    for index, item in enumerate(st.session_state['generated_results']):
        with st.container(border=True):
            cols = st.columns([1, 2])
            
            # [왼쪽] 이미지 및 재생성 버튼
            with cols[0]:
                try: st.image(item['path'], use_container_width=True)
                except: st.error("이미지 파일 없음")
                
                # 이미지 개별 재생성 버튼
                if st.button(f"🔄 이미지 다시 생성", key=f"regen_img_{index}", use_container_width=True):
                    if not api_key:
                        st.error("API Key가 필요합니다.")
                    else:
                        with st.spinner(f"Scene {item['scene']} 다시 그리는 중..."):
                            client = genai.Client(api_key=api_key)
                            
                            # 1. 프롬프트 다시 생성
                            current_title = st.session_state.get('video_title', '')
                            _, new_prompt = generate_prompt(
                                api_key, index, item['script'], style_instruction,
                                current_title, SELECTED_GENRE_MODE
                            )
                            
                            # 2. 이미지 생성
                            new_path = generate_image(
                                client, new_prompt, item['filename'], 
                                IMAGE_OUTPUT_DIR, SELECTED_IMAGE_MODEL
                            )
                            
                            if new_path:
                                st.session_state['generated_results'][index]['path'] = new_path
                                st.session_state['generated_results'][index]['prompt'] = new_prompt
                                st.success("이미지가 변경되었습니다!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error("이미지 생성에 실패했습니다.")

            # [오른쪽] 정보 및 다운로드
            with cols[1]:
                st.markdown(f"### Scene {item['scene']:02d}")
                st.markdown(f"**대본:**\n\n{item['script']}")
                
                with st.expander("📝 프롬프트 확인"):
                    st.text(item['prompt'])
                
                st.write("")
                try:
                    with open(item['path'], "rb") as file:
                        st.download_button("⬇️ 이미지 저장", data=file, file_name=item['filename'], mime="image/png", key=f"btn_down_{item['scene']}")
                except: pass