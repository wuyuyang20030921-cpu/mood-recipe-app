import streamlit as st
from openai import OpenAI
import urllib.request
from datetime import datetime, timedelta
import base64
import time
import re

# ==========================================
# 🌟 第一部分：终极视觉魔法 & 记忆库初始化
# ==========================================
st.set_page_config(page_title="情绪食谱 V4.0 稳定版", page_icon="🍲", layout="wide") 

if "recipe_history" not in st.session_state:
    st.session_state.recipe_history = []
if "current_recipe" not in st.session_state:
    st.session_state.current_recipe = None 
if "current_image" not in st.session_state:
    st.session_state.current_image = None 

st.markdown(
    """
    <style>
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    body {
        font-family: 'PingFang SC', 'Helvetica Neue', sans-serif;
        background: linear-gradient(-45deg, #fff9f3, #ffe8d6, #f9ecec, #ffffff);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #4a4a4a;
    }
    div[data-testid="stSidebar"] {
        background-color: rgba(255, 232, 214, 0.25) !important;
        backdrop-filter: blur(20px) !important;
        padding-top: 1rem !important;
    }
    .stTextInput input, .stSelectbox select, .stTextArea textarea, div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        box-shadow: 0 8px 30px rgba(0,0,0,0.04) !important;
        padding: 10px !important;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #ff8c69 0%, #ff6b6b 100%) !important;
        color: white !important;
        border-radius: 25px !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        border: none !important;
        box-shadow: 0 6px 15px rgba(255, 107, 107, 0.3) !important;
        transition: all 0.3s ease !important;
        padding: 15px !important;
    }
    div.stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 20px rgba(255, 107, 107, 0.5) !important;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        background-color: rgba(255, 232, 214, 0.3);
        backdrop-filter: blur(10px);
        border-radius: 12px 12px 0 0;
        font-size: 1.1rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff8c69 !important;
        color: white !important;
        font-weight: bold;
    }
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #ff8c69 !important;
        box-shadow: 0 0 0 2px rgba(255, 140, 105, 0.3) !important;
    }
    div.stMarkdown h1 {
        color: #ff6b6b;
        text-shadow: 0 4px 12px rgba(255, 107, 107, 0.15);
        text-align: center;
        font-weight: 900;
    }
    div.stMarkdown p { text-align: center; font-size: 1.1rem; color: #666;}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🍲 情绪食谱 V4.0 全感官幻境")
st.write("听着音乐，调配生活 —— 欢迎来到你的高维治愈厨房 ✨")

# ==========================================
# 🌟 第二部分：侧边栏大升级
# ==========================================
with st.sidebar:
    st.markdown("## 👨‍🍳 今日心境")
    col_sb_1, col_sb_2 = st.columns(2)
    with col_sb_1:
        mood = st.selectbox("1. 感觉？", ["🤯 焦虑", "😭 难过", "🥱 疲惫", "🥳 开心", "😡 愤怒", "🧘 平静"])
    with col_sb_2:
        weather = st.selectbox("2. 天气？", ["☀️ 晴朗", "🌧️ 阴雨", "☁️ 多云", "❄️ 寒冷", "🌬️ 大风"])
    
    with st.expander("⚙️ 主厨高级定制 (口味/时间/目标)"):
        diet_goal = st.selectbox("饮食目标", ["⚖️ 营养均衡", "🥗 疯狂减脂", "💪 增肌充碳", "🍵 肠胃友好", "😈 极致放纵"])
        chef_style = st.selectbox("主厨风格", ["👵 Gentle Grandma (外婆的唠叨)", "👨‍🍳 Michelin Star (米其林高傲主厨)", "🧘‍♂️ Zen Master (禅意冥想大师)"])
        taste_pref = st.selectbox("口味偏好", ["🌟 都可以", "🌶️ 无辣不欢", "🍋 嗜酸开胃", "🍬 嗜甜星人", "🧂 清淡原味"])
        time_limit = st.selectbox("烹饪时间", ["⏱️ 15分钟快手菜", "⏱️ 30分钟从容搞定", "⏱️ 1小时周末大餐", "⏳ 慢炖时光 (不限时)"])
    
    st.markdown("---")
    st.markdown("## 🛒 厨房库存")
    manual_ingredients = st.text_input("✍️ 手动输入（逗号分隔）", placeholder="例如：西红柿, 鸡蛋, 牛肉")
    use_camera = st.toggle("📸 开启智能摄像头识菜")
    
    camera_input = None
    if use_camera:
        camera_input = st.camera_input("对准食材拍一张")
    
    api_key = st.secrets["ZHIPU_API_KEY"]
    final_ingredients_list = []
    if manual_ingredients: 
        # 安全修复：将中文逗号替换为英文逗号，防止分割失败
        final_ingredients_list = manual_ingredients.replace('，', ',').split(',')

    if camera_input:
        with st.spinner("👀 扫描食材中..."):
            try:
                base64_image = base64.b64encode(camera_input.read()).decode('utf-8')
                client = OpenAI(api_key=api_key, base_url="https://open.bigmodel.cn/api/paas/v4/")
                vision_response = client.chat.completions.create(
                    model="glm-4v",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": "识别食材，输出中文逗号分隔的列表，不要废话。"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                detected = vision_response.choices[0].message.content
                st.success("识图成功！")
                st.info(detected)
                final_ingredients_list.extend(detected.split('，'))
            except Exception as e:
                st.error("识图失败，请确认额度充足。")

    final_ingredients_str = '，'.join(set([item.strip() for item in final_ingredients_list if item.strip()]))

    st.markdown("---")
    submit_button = st.button("✨ 顺应天时，开启料理魔法 ✨", use_container_width=True)
    
  st.markdown("---")
    st.markdown("### 📻 厨房治愈电台")
    st.caption("🎵 治愈 Lo-Fi 轻音乐，一键秒播")
    
    # 核心修复：使用网易云音乐的 HTML 嵌入播放器，彻底解决网络和一键播放问题
    st.components.v1.html(
        """
        <div style="display: flex; justify-content: center;">
            <iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width="100%" height="86" 
            src="//music.163.com/outchain/player?type=2&id=1460039233&auto=0&height=66">
            </iframe>
        </div>
        """,
        height=100
    )

# ==========================================
# 🌟 第三部分：主界面核心逻辑
# ==========================================
tab_kitchen, tab_history = st.tabs(["👨‍🍳 创作厨房", "📖 我的菜谱手账"])

with tab_kitchen:
    if submit_button:
        if not final_ingredients_str:
            st.warning("👈 巧妇难为无米之炊，请先告诉主厨食材！")
        else:
            if weather in ["🌧️ 阴雨", "❄️ 寒冷", "🌬️ 大风"]: st.snow()
            else: st.balloons()
            
            with st.spinner(f"👨‍🍳 【{chef_style.split(' ')[1]}】主厨正在为您构思 {time_limit.split(' ')[1]} 的专属料理..."):
                try:
                    client = OpenAI(api_key=api_key, base_url="https://open.bigmodel.cn/api/paas/v4/")
                    current_hour = (datetime.utcnow() + timedelta(hours=8)).hour
                    if 5 <= current_hour < 10: meal_time = "🌅 早餐"
                    elif 10 <= current_hour < 14: meal_time = "☀️ 午餐"
                    elif 14 <= current_hour < 17: meal_time = "☕ 下午茶"
                    elif 17 <= current_hour < 21: meal_time = "🌆 晚餐"
                    else: meal_time = "🌙 深夜食堂"

                    prompt = f"""
                    你是一个懂得心理学和营养学的米其林主厨。
                    【情境】心情：{mood} | 天气：{weather} | 时间：{meal_time} | 食材：{final_ingredients_str}
                    【强制约束】目标：{diet_goal} | 口味偏好：{taste_pref} | 严格时间限制：{time_limit}
                    【主厨风格】此刻你的身份是：{chef_style}。
                    
                    请输出清晰的 Markdown 格式：
                    
                    ### 💌 疗愈寄语
                    > *(结合天气与心情的温柔安抚)*
                    
                    ---
                    
                    ### 🥘 [专属菜名]
                    
                    **💡 灵感**：*(为什么这道菜能解压并符合口味)*
                    
                    #### 📊 营养估算 (每份)
                    | 卡路里 (kcal) | 蛋白质 (g) | 碳水化合物 (g) | 脂肪 (g) |
                    | :---: | :---: | :---: | :---: |
                    | [估算值] | [估算值] | [估算值] | [估算值] |
                    
                    #### 🛒 食材确认
                    *(列出食材，用 - 符号)*
                    
                    #### 👨‍🍳 料理魔法 (请确保总时长在 {time_limit} 内)
                    
                    **1️⃣ [步骤名称]** (⏱️ X分钟)
                    > [详细操作指导]
                    
                    **2️⃣ [步骤名称]** (⏱️ X分钟)
                    > [详细操作指导]
                    
                    ---
                    
                    ### 🧘‍♀️ 灶台冥想与影音搭配
                    - **🧘 冥想**：*(等待时的1分钟正念)*
                    - **🎵 推荐歌单**：*(2首)*
                    - **🎬 治愈放映**：*(1部电影)*
                    - **🍵 推荐配饮**：*(1款)*
                    
                    ---
                    
                    ### 📱 朋友圈打卡文案
                    [用适合当前主厨风格的口吻，写一段极其诱人、带情绪共鸣的社交媒体文案，附带3-4个相关的 Hashtag（如 #情绪食谱 #治愈系做饭 等），方便用户直接复制发送]
                    """
                    
                    response = client.chat.completions.create(
                        model="glm-4-flash",
                        messages=[{"role": "system", "content": f"你是顶级情绪主厨。风格是【{chef_style}】。"},
                                  {"role": "user", "content": prompt}]
                    )
                    recipe_text = response.choices[0].message.content
                    
                    # 召唤 CogView-3-Plus 画师
                    image_prompt = f"一道精致的治愈系美食，时间是{meal_time}，天气{weather}。食材：{final_ingredients_str}。口味倾向：{taste_pref}。氛围：{mood}的解药，顶级美食摄影，微距，景深，高清，诱人。"
                    image_response = client.images.generate(model="cogview-3-plus", prompt=image_prompt)
                    image_url = image_response.data[0].url
                    
                    # 安全修复：使用 st.empty() 制作原生进度条，放弃容易报错的底层 HTML
                    progress_placeholder = st.empty()
                    my_bar = progress_placeholder.progress(0)
                    for percent_complete in range(100):
                        time.sleep(0.01) 
                        my_bar.progress(percent_complete + 1)
                    progress_placeholder.empty() # 加载完后自动消失
                    
                    st.success("👨‍🍳 大餐已上桌！快看下方为您准备的朋友圈文案 ✨")
                    
                    st.session_state.current_recipe = recipe_text
                    st.session_state.current_image = image_url
                    
                    st.session_state.recipe_history.insert(0, {
                        "time": (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M'),
                        "mood": mood,
                        "text": recipe_text,
                        "image": image_url,
                        "style": chef_style
                    })
                    
                except Exception as e:
                    st.error(f"出错了，请确认您的智谱账号余额大于 0 元哦：{e}")
    
    if st.session_state.current_recipe and st.session_state.current_image:
        res_col_left, res_col_right = st.columns([6, 4])
        
        with res_col_left:
            with st.container(border=True):
                st.markdown(st.session_state.current_recipe)
                st.markdown("---")
                
                # 交互式清单
                ingredients_section = re.search(r"#### 🛒 食材确认\n([\s\S]*?)\n---", st.session_state.current_recipe)
                if ingredients_section:
                    st.markdown("#### 🛒 采购小黑板 (点击划掉)")
                    raw_items = ingredients_section.group(1).split('\n')
                    for item in raw_items:
                        item = item.strip().lstrip('- ').lstrip('* ').strip()
                        if item: st.checkbox(f"**{item}**", key=f"buy_{item}")

                st.download_button(
                    label="💾 保存图文菜谱至备忘录",
                    data=st.session_state.current_recipe,
                    file_name="my_healing_recipe.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
        with res_col_right:
            st.image(st.session_state.current_image, caption="专属定制，请慢用 📸", use_column_width=True)
            image_bytes = urllib.request.urlopen(st.session_state.current_image).read()
            st.download_button(label="💾 保存绝美大片到手机相册", data=image_bytes, file_name="recipe.png", mime="image/png", use_container_width=True)
            
    elif not submit_button:
        st.info("👈 主厨已就位，请在左侧下单，可以在下方点首 Lofi 音乐放松一下~")

# ==========================================
# 🌟 第四部分：我的菜谱手账 (安全重构版)
# ==========================================
with tab_history:
    st.markdown("### 📖 这里珍藏着你的每一次治愈时刻")
    
    if st.session_state.recipe_history:
        col_clear1, col_clear2, col_clear3 = st.columns([2, 1, 2])
        with col_clear2:
            if st.button("🗑️ 清空手账本", use_container_width=True):
                st.session_state.recipe_history = []
                st.session_state.current_recipe = None 
                st.session_state.current_image = None
                # 安全修复：兼容不同版本的网页刷新指令
                if hasattr(st, 'rerun'):
                    st.rerun()
                elif hasattr(st, 'experimental_rerun'):
                    st.experimental_rerun()

    if not st.session_state.recipe_history:
        st.write("手账本还是空的，快去厨房留下第一道菜的记忆吧！")
    else:
        for idx, item in enumerate(st.session_state.recipe_history):
            safe_style = item.get('style', '👨‍🍳 默认')
            style_name = safe_style.split(' ')[1] if ' ' in safe_style else safe_style
            
            with st.expander(f"🕰️ {item.get('time', '')} | 心情：{item.get('mood', '')} | 风格：{style_name}", expanded=(idx==0)):
                hist_col1, hist_col2 = st.columns([6, 4])
                with hist_col1:
                    st.markdown(item.get('text', '获取失败'))
                with hist_col2:
                    if item.get('image'):
                        st.image(item['image'], use_column_width=True)
