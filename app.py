
import streamlit as st
from openai import OpenAI
import urllib.request
from datetime import datetime, timedelta

# ==========================================
# 🌟 第一部分：网页基础设置与 CSS 视觉魔法
# ==========================================
st.set_page_config(page_title="情绪食谱", page_icon="🍲", layout="wide") 

# 注入 CSS 魔法，精修界面细节
st.markdown(
    """
    <style>
    /* 1. 美化主按钮：圆角、渐变色、悬浮动态阴影 */
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

    /* 2. 让文字卡片更有呼吸感 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 15px !important;
        border: 1px solid #f9ecec !important;
        background-color: rgba(255, 255, 255, 0.7) !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.04) !important;
        padding: 5px !important;
    }

    /* 3. 美化输入框和下拉菜单的焦点状态 */
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #ffb085 !important;
        box-shadow: 0 0 0 1px #ffb085 !important;
    }
    
    /* 4. 微调页面顶部的留白 */
    .block-container {
        padding-top: 3rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 🌟 第二部分：标题与环境感知 (时间系统)
# ==========================================
st.title("🍲 情绪食谱生成器 Mood-Recipe")
st.write("欢迎来到你的专属治愈厨房！(🌟 满血终极版)")

# 获取真实时间并判断用餐场景 (北京时间 UTC+8)
current_time = datetime.utcnow() + timedelta(hours=8)
current_hour = current_time.hour

if 5 <= current_hour < 10:
    meal_time = "🌅 早餐 (需要唤醒活力，清淡易消化)"
elif 10 <= current_hour < 14:
    meal_time = "☀️ 午餐 (需要补充能量，扛饿，抗疲劳)"
elif 14 <= current_hour < 17:
    meal_time = "☕ 下午茶 (缓解工作焦虑，适合甜品或清爽小吃)"
elif 17 <= current_hour < 21:
    meal_time = "🌆 晚餐 (慰藉一天的疲惫，低脂、安神、丰盛)"
else:
    meal_time = "🌙 深夜食堂 (极简，暖胃，绝对治愈，不增加肠胃负担)"

# 页面上方温柔地提示当前时间
st.info(f"⏱️ 主厨看了一眼墙上的时钟：现在是 {current_time.strftime('%H:%M')}，正是为你准备【{meal_time.split(' ')[0]}】的时候。")
st.markdown("---")

# ==========================================
# 🌟 第三部分：页面布局 (三列点餐区)
# ==========================================
st.markdown("### 📝 第一步：写下今天的点餐单")
col_input1, col_input2, col_input3 = st.columns(3)

with col_input1:
    mood = st.selectbox("现在的感觉？", ["🤯 焦虑", "😭 难过", "🥱 疲惫", "🥳 开心", "😡 愤怒"])
with col_input2:
    weather = st.selectbox("窗外天气？", ["☀️ 晴朗明媚", "🌧️ 阴雨绵绵", "☁️ 沉闷多云", "❄️ 寒冷刺骨", "🌬️ 狂风大作"])
with col_input3:
    ingredients = st.text_input("冰箱里有啥？", placeholder="例如：西红柿, 鸡蛋, 面条, 猪肉")

# 从云端隐形保险箱读取 API Key
api_key = st.secrets["ZHIPU_API_KEY"]
st.markdown("<br>", unsafe_allow_html=True) 

# 居中提交按钮 (使用 1:2:1 的列比例)
col_spacer1, col_btn, col_spacer3 = st.columns([1, 2, 1])
with col_btn:
    submit_button = st.button("✨ 顺应天时，开始烹饪我的治愈食谱 ✨", use_container_width=True)

st.markdown("---")

# ==========================================
# 🌟 第四部分：核心 AI 逻辑与摆盘输出
# ==========================================
if submit_button:
    if not ingredients:
        st.warning("请先告诉我你有哪些食材！")
    else:
        st.success("👨‍🍳 主厨正在为你施展魔法，请稍候...")
        
        try:
            client = OpenAI(
                api_key=api_key, 
                base_url="https://open.bigmodel.cn/api/paas/v4/"
            )
            
            # 严格的结构化 Prompt，融入了所有环境变量
            prompt = f"""
            你是一个懂得心理学和营养学的米其林主厨。
            【当前情境】- 心情：【{mood}】，天气：【{weather}】，时间：【{meal_time}】，食材：【{ingredients}】
            
            请严格按照以下 Markdown 格式输出，不要改变标题结构，直接填充内容：
            
            ### 💌 主厨的疗愈寄语
            > *(请在这里写下结合天气、时间与心情的温暖安抚话语，要像写信一样温柔)*
            
            ---
            
            ### 🥘 专属菜单：[请为这道菜起一个诗意且治愈的名字]
            
            **💡 治愈灵感**：*(一句话说明为什么这道菜能解【{mood}】的毒)*
            
            #### 🛒 食材确认
            *(列出需要的食材，使用短列表形式)*
            
            #### 👨‍🍳 料理魔法
            *(分步骤写出做法，步骤要简明，开头用 1️⃣ 2️⃣ 3️⃣ 等 Emoji)*
            
            ---
            
            ### 🧘‍♀️ 灶台前的 1 分钟冥想
            *(提供一段在切菜或等水烧开时可以做的简短正念冥想)*
            
            ### 🎧 沉浸式影音搭配
            - **🎵 推荐歌单**：*(2首音乐，并简述理由)*
            - **🎬 治愈放映室**：*(1部电影，并简述理由)*
            """
            
            # 召唤文本主厨写菜谱
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {"role": "system", "content": "你是一个充满关怀、知冷知热的情绪治愈主厨。"},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # 召唤画师主厨生成图片 (同样感知时间和天气)
            image_prompt = f"一道精致的治愈系美食，时间是{meal_time.split(' ')[0]}，天气{weather}。主要食材包含：{ingredients}。氛围：{mood}的解药，顶级美食摄影，高清，诱人。"
            image_response = client.images.generate(
                model="cogview-3-plus", 
                prompt=image_prompt
            )
            image_url = image_response.data[0].url
            
            # --- 左右宽屏分屏展示 ---
            st.markdown("### 🍽️ 你的专属情绪大餐已上桌")
            
            # 比例为 6:4 分列
            res_col_left, res_col_right = st.columns([6, 4])
            
            with res_col_left:
                # 给左侧的文字套上高级边框容器
                with st.container(border=True):
                    st.markdown(response.choices[0].message.content)
                
            with res_col_right:
                # 右侧展示美食图和下载按钮
                st.caption("✨ AI 视觉主厨为你生成的概念图")
                st.image(image_url, caption=f"伴随 {weather.split(' ')[1]} 的天气，请慢用 📸", use_column_width=True)
                
                image_bytes = urllib.request.urlopen(image_url).read()
                st.download_button(
                    label="💾 点击保存这道菜到手机",
                    data=image_bytes,
                    file_name="my_healing_recipe.png",
                    mime="image/png",
                    use_container_width=True
                )
            
        except Exception as e:
            st.error(f"哎呀，厨房出了点小状况：{e}")
