
import streamlit as st
from openai import OpenAI
import urllib.request
from datetime import datetime, timedelta
import base64
import time

# ==========================================
# 🌟 第一部分：基础设置、CSS 与 记忆初始化
# ==========================================
st.set_page_config(page_title="情绪食谱 V2.0", page_icon="🍲", layout="wide") 

# 🧠 黑科技：初始化“短期记忆库”
# 只要网页不刷新，生成的食谱都会存在这里
if "recipe_history" not in st.session_state:
    st.session_state.recipe_history = []

st.markdown(
    """
    <style>
    body { font-family: 'Poppins', sans-serif; }
    div[data-testid="stSidebar"] {
        background-color: rgba(255, 232, 214, 0.4) !important;
        backdrop-filter: blur(10px) !important;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #ffb085 0%, #ff8c69 100%) !important;
        color: white !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(255, 140, 105, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover { transform: translateY(-2px) !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 15px !important;
        border: 1px solid #f9ecec !important;
        background-color: white !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.04) !important;
        padding: 10px !important;
    }
    .stTextInput input:focus, .stSelectbox select:focus, .stCameraInput button:focus {
        border-color: #ffb085 !important;
        box-shadow: 0 0 0 1px #ffb085 !important;
    }
    .block-container { padding-top: 2rem !important; }
    div.stMarkdown h1, div.stMarkdown p { text-align: center; }
    
    /* 美化 Tab 标签页 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f9ecec;
        border-radius: 10px 10px 0 0;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffb085 !important;
        color: white !important;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🍲 情绪食谱生成器 V2.0")
st.write("欢迎来到你的专属治愈厨房！(🌟 带记忆的专业管家版)")

# ==========================================
# 🌟 第二部分：侧边栏管家控制台 (新增饮食目标)
# ==========================================
with st.sidebar:
    st.markdown("## 👨‍🍳 主厨控制台")
    
    mood = st.selectbox("1. 现在的感觉？", ["🤯 焦虑", "😭 难过", "🥱 疲惫", "🥳 开心", "😡 愤怒"])
    weather = st.selectbox("2. 窗外天气怎样？", ["☀️ 晴朗明媚", "🌧️ 阴雨绵绵", "☁️ 沉闷多云", "❄️ 寒冷刺骨", "🌬️ 狂风大作"])
    
    # --- 新增功能：健康与饮食目标 ---
    diet_goal = st.selectbox("3. 今天的饮食目标？", [
        "⚖️ 营养均衡 (不限)", 
        "🥗 疯狂减脂 (低卡低脂)", 
        "💪 增肌充碳 (高蛋白)", 
        "🍵 肠胃友好 (好消化)", 
        "😈 极致放纵 (不管热量，好吃就行)"
    ])
    
    st.markdown("---")
    st.markdown("## 4. 提供食材")
    
    camera_input = st.camera_input("📸 智能扫一扫识菜")
    manual_ingredients = st.text_input("或者手动输入（逗号分隔）", placeholder="例如：西红柿, 鸡蛋, 面条")
    
    api_key = st.secrets["ZHIPU_API_KEY"]
    
    final_ingredients_list = []
    if manual_ingredients:
        final_ingredients_list = manual_ingredients.split(',')

    if camera_input:
        with st.spinner("👀 正在识别食材..."):
            try:
                camera_input_bytes = camera_input.read()
                base64_image = base64.b64encode(camera_input_bytes).decode('utf-8')
                client = OpenAI(api_key=api_key, base_url="https://open.bigmodel.cn/api/paas/v4/")
                
                vision_response = client.chat.completions.create(
                    model="glm-4v",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "识别照片中的食材，输出中文逗号分隔的列表，不要废话。"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }]
                )
                detected_ingredients_str = vision_response.choices[0].message.content
                st.success("识图成功！包含：")
                st.info(detected_ingredients_str)
                final_ingredients_list.extend(detected_ingredients_str.split('，'))
            except Exception as e:
                st.error("识图失败，请手动输入。")

    final_ingredients_list = [item.strip() for item in final_ingredients_list if item.strip()]
    final_ingredients_str = '，'.join(set(final_ingredients_list))

    st.markdown("---")
    submit_button = st.button("✨ 顺应天时，开始烹饪 ✨", use_container_width=True)


# ==========================================
# 🌟 第三部分：主界面模块化 (Tab 标签页系统)
# ==========================================
# 将整个右侧屏幕分为两个独立的功能区
tab_kitchen, tab_history = st.tabs(["👨‍🍳 创作厨房 (点餐区)", "📖 我的专属菜谱库 (历史)"])

with tab_kitchen:
    # --- 核心 AI 生成逻辑 ---
    if submit_button:
        if not final_ingredients_str:
            st.warning("👈 请先在左侧控制台告诉主厨食材哦！")
        else:
            if weather in ["🌧️ 阴雨绵绵", "❄️ 寒冷刺骨", "🌬️ 狂风大作"]: st.snow()
            else: st.balloons()
            
            with st.spinner(f"👨‍🍳 主厨正根据【{diet_goal.split(' ')[1]}】目标为你构思..."):
                try:
                    client = OpenAI(api_key=api_key, base_url="https://open.bigmodel.cn/api/paas/v4/")
                    
                    current_time = datetime.utcnow() + timedelta(hours=8)
                    current_hour = current_time.hour
                    if 5 <= current_hour < 10: meal_time = "🌅 早餐"
                    elif 10 <= current_hour < 14: meal_time = "☀️ 午餐"
                    elif 14 <= current_hour < 17: meal_time = "☕ 下午茶"
                    elif 17 <= current_hour < 21: meal_time = "🌆 晚餐"
                    else: meal_time = "🌙 深夜食堂"

                    # 提示词大升级：加入营养估算表和饮食目标约束
                    prompt = f"""
                    你是一个懂心理学和营养学的米其林主厨。
                    【情境】- 心情:【{mood}】, 天气:【{weather}】, 时间:【{meal_time}】, 食材:【{final_ingredients_str}】
                    【核心约束】- 用户的饮食目标是：【{diet_goal}】。你的烹饪方法和选材必须严格符合这个目标！
                    
                    请严格按以下 Markdown 格式输出：
                    
                    ### 💌 疗愈寄语
                    > *(结合天气、心情与健康目标的安抚话语)*
                    
                    ---
                    
                    ### 🥘 [专属菜名]
                    
                    **💡 灵感**：*(为什么这道菜能治愈心情且符合健康目标)*
                    
                    #### 📊 营养估算 (每份)
                    | 卡路里 (kcal) | 蛋白质 (g) | 碳水化合物 (g) | 脂肪 (g) |
                    | :---: | :---: | :---: | :---: |
                    | [估算值] | [估算值] | [估算值] | [估算值] |
                    
                    #### 🛒 食材确认
                    *(短列表)*
                    
                    #### 👨‍🍳 料理魔法
                    *(分步骤做法，开头用 Emoji)*
                    
                    ---
                    
                    ### 🧘‍♀️ 灶台冥想
                    *(切菜或等待时的正念冥想)*
                    
                    ### 🎧 影音搭配
                    - **🎵 推荐歌单**：*(2首)*
                    - **🎬 治愈放映室**：*(1部电影)*
                    """
                    
                    response = client.chat.completions.create(
                        model="glm-4-flash",
                        messages=[
                            {"role": "system", "content": "你是一个专业的情绪治愈主厨兼高级营养师。"},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    recipe_text = response.choices[0].message.content
                    
                    image_prompt = f"一道精致的治愈系美食，时间是{meal_time}，天气{weather}。食材：{final_ingredients_str}。目标：{diet_goal}。氛围：{mood}的解药，顶级美食摄影，高清。"
                    image_response = client.images.generate(
                        model="cogview-3-plus", 
                        prompt=image_prompt
                    )
                    image_url = image_response.data[0].url
                    
                    # --- 记忆功能：将生成的数据保存到历史库 ---
                    st.session_state.recipe_history.insert(0, {
                        "time": current_time.strftime('%Y-%m-%d %H:%M'),
                        "mood": mood,
                        "text": recipe_text,
                        "image": image_url
                    })
                    
                    # 展示结果
                    res_col_left, res_col_right = st.columns([6, 4])
                    with res_col_left:
                        with st.container(border=True):
                            st.markdown(recipe_text)
                    with res_col_right:
                        st.image(image_url, caption="专属定制，请慢用 📸", use_column_width=True)
                        image_bytes = urllib.request.urlopen(image_url).read()
                        st.download_button("💾 保存美食卡片", data=image_bytes, file_name="recipe.png", mime="image/png", use_container_width=True)
                    
                except Exception as e:
                    st.error(f"厨房出了点小状况：{e}")
    else:
        st.info("👈 请在左侧控制台写下需求，然后点击开始烹饪！")

# ==========================================
# 🌟 第四部分：我的专属菜谱库 (读取记忆库)
# ==========================================
with tab_history:
    st.markdown("### 📖 这里记录着你今天的所有治愈时刻")
    if not st.session_state.recipe_history:
        st.write("目前厨房还没有开火记录哦，快去【创作厨房】做第一道菜吧！")
    else:
        # 遍历历史记录并展示
        for idx, item in enumerate(st.session_state.recipe_history):
            # 使用 expander (手风琴折叠面板) 让历史记录看起来整洁
            with st.expander(f"🕰️ {item['time']} | 当时心情：{item['mood']}", expanded=(idx==0)):
                hist_col1, hist_col2 = st.columns([6, 4])
                with hist_col1:
                    st.markdown(item['text'])
                with hist_col2:
                    st.image(item['image'], use_column_width=True)
