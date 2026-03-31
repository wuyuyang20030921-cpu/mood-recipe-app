
import streamlit as st
from openai import OpenAI
import urllib.request
from datetime import datetime, timedelta
import base64
import time
import re # 用于提取食材的工具

# ==========================================
# 🌟 第一部分：终极视觉魔法 & CSS 大改造
# ==========================================
st.set_page_config(page_title="情绪食谱 V3.0 至尊版", page_icon="🍲", layout="wide") 

# 初始化“短期记忆库” (只要网页没关，生成的食谱都会存在这里)
if "recipe_history" not in st.session_state:
    st.session_state.recipe_history = []
if "current_recipe" not in st.session_state:
    st.session_state.current_recipe = None # 存放当前正在展示的食谱
if "current_image" not in st.session_state:
    st.session_state.current_image = None # 存放当前生成的图片

st.markdown(
    """
    <style>
    /* ==================================
       核心魔法 1：高级动态呼吸背景 动画
       ================================== */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    body {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(-45deg, #fff9f3, #ffe8d6, #f9ecec, #ffffff);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #4a4a4a;
    }

    /* ==================================
       核心魔法 2：玻璃质感卡片 效果 (Glassmorphism)
       ================================== */
    div[data-testid="stSidebar"] {
        background-color: rgba(255, 232, 214, 0.2) !important;
        backdrop-filter: blur(20px) !important;
        padding-top: 1rem !important;
    }

    /* 输入框、容器的高级玻璃效果 */
    .stTextInput input, .stSelectbox select, .stTextArea textarea, .stCameraInput button, div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.03) !important;
        padding: 10px !important;
    }

    /* ==================================
       核心魔法 3：灵动按钮与 Tab 美化
       ================================== */
    div.stButton > button {
        background: linear-gradient(135deg, #ffb085 0%, #ff8c69 100%) !important;
        color: white !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(255, 140, 105, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(255, 140, 105, 0.6) !important;
    }

    /* 美化 Tab 标签页 */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255, 232, 214, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 10px 10px 0 0;
        padding-top: 10px; padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffb085 !important;
        color: white !important;
        font-weight: bold;
    }

    /* 全局组件微调 */
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #ffb085 !important;
        box-shadow: 0 0 0 1px #ffb085 !important;
    }
    .block-container { padding-top: 2rem !important; }
    div.stMarkdown h1, div.stMarkdown p { text-align: center; }
    
    /* 让标题加上一圈柔和的发光效果，提升视觉冲击 */
    div.stMarkdown h1 {
        color: #ff8c69;
        text-shadow: 0 4px 8px rgba(255, 140, 105, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🍲 情绪食谱生成器 V3.0 至尊版")
st.write("欢迎来到你的专属治愈厨房！(🌟 带短期记忆的商业满血版)")

# ==========================================
# 🌟 第二部分：侧边栏管家控制台 (更贴心的输入)
# ==========================================
with st.sidebar:
    st.markdown("## 👨‍🍳 主厨控制台")
    st.write("请告诉主厨你现在的状态和需求：")
    
    col_sb_1, col_sb_2 = st.columns(2)
    with col_sb_1:
        mood = st.selectbox("1. 感觉？", ["🤯 焦虑", "😭 难过", "🥱 疲惫", "🥳 开心", "😡 愤怒"])
    with col_sb_2:
        weather = st.selectbox("2. 天气？", ["☀️ 晴朗明媚", "🌧️ 阴雨绵绵", "☁️ 沉闷多云", "❄️ 寒冷刺骨", "🌬️ 狂风大作"])
    
    diet_goal = st.selectbox("3. 今天的饮食目标？", [
        "⚖️ 营养均衡 (不限)", "🥗 疯狂减脂 (低卡低脂)", "💪 增肌充碳 (高蛋白)", "🍵 肠胃友好 (好消化)", "😈 极致放纵 (好吃就行)"
    ])
    
    # --- 新增功能：主厨风格 ---
    chef_style = st.selectbox("4. 想要哪种风格的主厨？", [
        "👵 Gentle Grandma (温柔、外婆的味道)",
        "👨‍🍳 Michelin Star (专业、追求完美摆盘)",
        "🧘‍♂️ Zen master (神秘、注重冥想与身心)"
    ])
    
    st.markdown("---")
    st.markdown("## 5. 告诉主厨食材")
    
    camera_input = st.camera_input("📸 智能扫一扫识菜")
    manual_ingredients = st.text_input("或者手动输入（逗号分隔）", placeholder="例如：西红柿, 鸡蛋, 面条")
    
    api_key = st.secrets["ZHIPU_API_KEY"]
    
    final_ingredients_list = []
    if manual_ingredients:
        final_ingredients_list = manual_ingredients.split(',')

    if camera_input:
        with st.spinner("👀 👨‍🍳 主厨正看着照片... 正在识别食材"):
            try:
                camera_input_bytes = camera_input.read()
                base64_image = base64.b64encode(camera_input_bytes).decode('utf-8')
                client = OpenAI(api_key=api_key, base_url="https://open.bigmodel.cn/api/paas/v4/")
                vision_response = client.chat.completions.create(
                    model="glm-4v",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": "识别照片中的食材，输出中文逗号分隔的列表，不要废话。"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                detected_ingredients_str = vision_response.choices[0].message.content
                st.success("识图成功！:")
                st.info(detected_ingredients_str)
                final_ingredients_list.extend(detected_ingredients_str.split('，'))
            except Exception as e:
                st.error("识图失败，请在下方手动输入或重新拍摄。")

    final_ingredients_list = [item.strip() for item in final_ingredients_list if item.strip()]
    final_ingredients_str = '，'.join(set(final_ingredients_list))

    st.markdown("---")
    # 终极生成按钮 (撐满侧边栏)
    submit_button = st.button("✨ 顺应天时，烹饪我的治愈食谱 ✨", use_container_width=True)


# ==========================================
# 🌟 第三部分：主界面模块化 (Tab 标签页 & 状态同步)
# ==========================================
# 顶部的模块导航
tab_kitchen, tab_history = st.tabs(["👨‍🍳 创作厨房 (点餐区)", "📖 我的专属菜谱库 (历史)"])

with tab_kitchen:
    # 如果用户提交了点餐请求
    if submit_button:
        if not final_ingredients_str:
            st.warning("👈 请先在左侧控制台告诉主厨食材哦！")
        else:
            # 根据天气全屏下雪特效
            if weather in ["🌧️ 阴雨绵绵", "❄️ 寒冷刺骨", "🌬️狂风大作"]: st.snow()
            else: st.balloons()
            
            with st.spinner(f"👨‍🍳 【{chef_style.split(' ')[1]}】主厨看懂了食材和目标，正为你精心构思..."):
                try:
                    client = OpenAI(api_key=api_key, base_url="https://open.bigmodel.cn/api/paas/v4/")
                    current_time = datetime.utcnow() + timedelta(hours=8)
                    current_hour = current_time.hour
                    if 5 <= current_hour < 10: meal_time = "🌅 早餐"
                    elif 10 <= current_hour < 14: meal_time = "☀️ 午餐"
                    elif 14 <= current_hour < 17: meal_time = "☕ 下午茶"
                    elif 17 <= current_hour < 21: meal_time = "🌆 晚餐"
                    else: meal_time = "🌙 深夜食堂"

                    # 提示词彻底精进：加入主厨风格、营养师视角、饮品搭配
                    prompt = f"""
                 # 提示词彻底精进：加入极致排版的料理魔法模板
                    prompt = f"""
                    你是一个懂得心理学和营养学的米其林主厨。
                    【当前情境】- 心情：【{mood}】，天气：【{weather}】，时间：【{meal_time}】，食材：【{final_ingredients_str}】
                    【饮食目标】- 【{diet_goal}】
                    【主厨风格】- 此刻你的身份是：【{chef_style}】。请用这个身份的语气和方法来烹饪和安抚。
                    
                    请输出清晰、精美、带有 Markdown 格式的内容：
                    
                    ### 💌 疗愈寄语
                    > *(写下结合天气、时间与心情的温暖安抚话语，要温柔)*
                    
                    ---
                    
                    ### 🥘 [专属菜名]
                    
                    **💡 灵感**：*(为什么这道菜能解【{mood}】的毒)*
                    
                    #### 📊 营养估算 (每份)
                    | 卡路里 (kcal) | 蛋白质 (g) | 碳水化合物 (g) | 脂肪 (g) |
                    | :---: | :---: | :---: | :---: |
                    | [估算值] | [估算值] | [估算值] | [估算值] |
                    
                    #### 🛒 食材确认
                    *(列出食材清单，使用 - 符号的无序列表)*
                    
                    #### 👨‍🍳 料理魔法
                    *(重点要求：请极其详细、像手把手教新手一样列出步骤！绝对不允许把步骤挤在同一段落！必须严格使用以下排版格式，确保每一个步骤都有独立标题和引用框：)*
                    
                    **1️⃣ [步骤名称]** (⏱️ 预计用时: X分钟)
                    > [详细的具体操作动作、火候提示、判断熟没熟的技巧等，像在身边指导一样]
                    
                    **2️⃣ [步骤名称]** (⏱️ 预计用时: X分钟)
                    > [详细的操作说明...]
                    
                    *(以此类推，完成所有步骤)*
                    
                    ---
                    
                    ### 🧘‍♀️ 灶台前的 1 分钟冥想
                    *(在切菜或等待时的正念冥想)*
                    
                    ### 🎧 沉浸式影音与配饮
                    - **🎵 推荐歌单**：*(2首)*
                    - **🎬 治愈放映室**：*(1部电影)*
                    - **🍵 推荐配饮**：*(1款，并说明理由)*
                    """
                    """
                    
                    response = client.chat.completions.create(
                        model="glm-4-flash",
                        messages=[{"role": "system", "content": f"你是一个专业的情绪治愈主厨兼高级营养师。当前的身份是【{chef_style}】。"},
                                  {"role": "user", "content": prompt}]
                    )
                    recipe_text = response.choices[0].message.content
                    
                    image_prompt = f"一道精致的治愈系美食，米其林风格，时间是{meal_time}，天气{weather}。主要食材包含：{final_ingredients_str}。目标：{diet_goal}。氛围：{mood}的解解毒，顶级美食摄影，高清，诱人。"
                    image_response = client.images.generate(
                        model="cogview-3-plus", 
                        prompt=image_prompt
                    )
                    image_url = image_response.data[0].url
                    
                    # 模拟进度条，沉浸式体验
                    progress_bar = st.progress(0)
                    for percent_complete in range(100):
                        time.sleep(0.01) # 模拟处理时间
                        progress_bar.progress(percent_complete + 1)
                    
                    # 沉浸式成功动效：全屏五彩庆祝纸屑！
                    st.components.v1.html(
                        """
                        <script>
                            window.parent.postMessage({type: 'streamlit:report_progress', progress: 100}, '*')
                        </script>
                        """, height=0
                    )
                    st.success("👨‍🍳 厨艺施展完毕！全能满血版大餐已上桌 ✨")
                    
                    # --- 记忆同步魔法 ---
                    # 1. 存入当前展示的状态
                    st.session_state.current_recipe = recipe_text
                    st.session_state.current_image = image_url
                    
                    # 2. 存入菜谱记忆库 (去重，存一份干净的历史)
                    st.session_state.recipe_history.insert(0, {
                        "time": current_time.strftime('%Y-%m-%d %H:%M'),
                        "mood": mood,
                        "text": recipe_text,
                        "image": image_url,
                        "style": chef_style
                    })
                    
                except Exception as e:
                    st.error(f"哎呀，厨房出了点小状况：{e}")
    
    # --- 🌟 创作厨房 真正的响应式展示魔法 ---
    # 如果用户没有提交，但记忆库里有当前的食谱，就要在这里同步展示
    if st.session_state.current_recipe and st.session_state.current_image:
        res_col_left, res_col_right = st.columns([6, 4])
        
        with res_col_left:
            # 给文字区域套上玻璃卡片效果容器
            with st.container(border=True):
                st.markdown(st.session_state.current_recipe)
                st.markdown("---")
                
                # --- 新增：交互式采购 Checklist 采购清单 ---
                # 尝试通过简单的正则提取食材列表（假设 AI 按模板列出了短列表）
                ingredients_section = re.search(r"#### 🛒 食材确认\n([\s\S]*?)\n---", st.session_state.current_recipe)
                if ingredients_section:
                    st.markdown("#### 🛒 交互式采购清单")
                    st.write("在手机上点击选择，已经买好的可以划掉哦：")
                    # 提取食材行，清理废话
                    raw_items = ingredients_section.group(1).split('\n')
                    for item in raw_items:
                        item = item.strip().lstrip('- ').lstrip('* ').strip()
                        if item:
                            st.checkbox(f"**{item}**", key=f"buy_{item}")

                # --- 新增功能：导出 Markdown 文本食谱按钮 ---
                st.download_button(
                    label="💾 点击保存 Markdown 文本菜谱至电脑/手机备忘录",
                    data=st.session_state.current_recipe,
                    file_name="my_healing_recipe.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
        with res_col_right:
            st.image(st.session_state.current_image, caption="专属定制，请慢用 📸", use_column_width=True)
            image_bytes = urllib.request.urlopen(st.session_state.current_image).read()
            st.download_button(label="💾 点击保存美食概念图到相册", data=image_bytes, file_name="recipe.png", mime="image/png", use_container_width=True)
            
    # 如果没有生成过食谱，显示开场语
    elif not submit_button:
        st.info("👈 请在左侧控制台写下需求，主厨将把“治愈料理”在这片玻璃卡片上完美呈现！")


# ==========================================
# 🌟 第四部分：我的专属菜谱库 (读取记忆库 & 功能完善)
# ==========================================
with tab_history:
    st.markdown("### 📖 这里记录着你今天的所有治愈时刻")
    
    # 功能完善：一键清空记忆库
    if st.session_state.recipe_history:
        col_clear1, col_clear2, col_clear3 = st.columns([2, 1, 2])
        with col_clear2:
            if st.button("🗑️ 清空记忆库", use_container_width=True):
                st.session_state.recipe_history = []
                st.session_state.current_recipe = None # 也要清除当前主屏的展示
                st.session_state.current_image = None
                st.rerun() # 立即刷新页面

    if not st.session_state.recipe_history:
        st.write("目前厨房还没有开火记录哦，快去【创作厨房】做第一道菜吧！")
    else:
        # 遍历历史记录并展示
        for idx, item in enumerate(st.session_state.recipe_history):
            # 使用 expander (手风琴折叠面板) 整理历史记录
            with st.expander(f"🕰️ {item['time']} | 心情：{item['mood']} | 风格：{item['style'].split(' ')[1]}", expanded=(idx==0)):
                hist_col1, hist_col2 = st.columns([6, 4])
                with hist_col1:
                    st.markdown(item['text'])
                with hist_col2:
                    st.image(item['image'], use_column_width=True)
