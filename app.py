
import streamlit as st
from openai import OpenAI
import urllib.request
from datetime import datetime, timedelta
import base64 # 核心黑科技：用于图像编码
import time

# ==========================================
# 🌟 第一部分：终极 CSS 魔法 & 宽屏响应布局
# ==========================================
st.set_page_config(page_title="情绪食谱", page_icon="🍲", layout="wide") 

# 注入 CSS 魔法，精修侧边栏和主界面细节
st.markdown(
    """
    <style>
    /* 全局背景和字体微调，增加质感 */
    body {
        font-family: 'Poppins', sans-serif;
    }
    
    /* 让侧边栏看起来更高级，带一点毛玻璃质感 */
    div[data-testid="stSidebar"] {
        background-color: rgba(255, 232, 214, 0.4) !important;
        backdrop-filter: blur(10px) !important;
        padding-top: 1rem !important;
    }

    /* 美化主按钮：在侧边栏中撑满 */
    div.stButton > button {
        background: linear-gradient(135deg, #ffb085 0%, #ff8c69 100%) !important;
        color: white !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(255, 140, 105, 0.3) !important;
        transition: all 0.3s ease !important;
        use-container-width: True !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(255, 140, 105, 0.6) !important;
    }

    /* 2. 主界面文字卡片效果 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 15px !important;
        border: 1px solid #f9ecec !important;
        background-color: white !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.04) !important;
        padding: 5px !important;
    }

    /* 3. 美化输入框焦点状态 */
    .stTextInput input:focus, .stSelectbox select:focus, .stCameraInput button:focus {
        border-color: #ffb085 !important;
        box-shadow: 0 0 0 1px #ffb085 !important;
    }
    
    /* 4. 微调标题留白 */
    .block-container {
        padding-top: 3rem !important;
    }
    
    /* 让主页面的标题和简介居中，更有仪式感 */
    div.stMarkdown h1, div.stMarkdown p {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 🌟 第二部分：主界面标题与欢迎语 (现在非常开阔)
# ==========================================
st.title("🍲 情绪食谱生成器 Mood-Recipe")
st.write("欢迎来到你的专属治愈厨房！(🌟 全能满血神仙合体版)")
st.markdown("---")

# ==========================================
# 🌟 第三部分：侧边栏控制台 (全盘大搬家)
# ==========================================
with st.sidebar:
    st.markdown("## 👨‍🍳 主厨控制台")
    st.write("请告诉主厨你现在的感觉和环境：")
    
    mood = st.selectbox("1. 你现在的感觉？", ["🤯 焦虑", "😭 难过", "🥱 疲惫", "🥳 开心", "😡 愤怒"])
    weather = st.selectbox("2. 窗外天气怎样？", ["☀️ 晴朗明媚", "🌧️ 阴雨绵绵", "☁️ 沉闷多云", "❄️ 寒冷刺骨", "🌬️ 狂风大作"])
    
    st.markdown("---")
    
    # --- 🌟 黑科技 1：📸 摄像头识菜组件 ---
    st.markdown("## 3. 告诉主厨食材")
    st.write("你可以直接拍一张冰箱食材的照片，也可以手动输入：")
    
    camera_input = st.camera_input("📸 智能扫一扫识菜")
    manual_ingredients = st.text_input("或者手动输入（逗号分隔）", placeholder="例如：西红柿, 鸡蛋, 面条")
    
    # 从云端隐形保险箱读取 API Key
    api_key = st.secrets["ZHIPU_API_KEY"]
    
    # 将手动输入的食材处理成一个初始列表
    final_ingredients_list = []
    if manual_ingredients:
        final_ingredients_list = manual_ingredients.split(',')

    # --- 🌟 黑科技 2：📸 智能扫一扫逻辑 ---
    # 如果用户拍了照，我们就开启视觉大模型
    if camera_input:
        with st.spinner("👨‍🍳 主厨正在盯着照片看……正在识别食材"):
            try:
                # 必须将图片编码为 base64 才能喂给大模型
                camera_input_bytes = camera_input.read()
                base64_image = base64.b64encode(camera_input_bytes).decode('utf-8')
                
                client = OpenAI(
                    api_key=api_key, 
                    base_url="https://open.bigmodel.cn/api/paas/v4/"
                )
                
                # 调用强悍的 GLM-4V 视觉大模型
                vision_response = client.chat.completions.create(
                    model="glm-4v",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "这是一张用户冰箱里或厨房台面上食材的照片。作为智能主厨管家，请识别照片中的主要食材（西红柿、鸡蛋、面条、猪肉、牛肉等），并输出一个纯文本形式的、用中文逗号分隔的食材名称列表。不要输出任何菜谱或废话，只输出食材清单。"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}" # 必须加上这个前缀格式！
                                    }
                                }
                            ]
                        }
                    ]
                )
                
                # 获取 AI 识别到的食材字符串
                detected_ingredients_str = vision_response.choices[0].message.content
                st.success("👨‍🍳 主厨看懂了！照片里的食材有：")
                st.info(detected_ingredients_str)
                # 将识别到的食材也合并进最终食材列表中
                detected_ingredients_list = detected_ingredients_str.split('，')
                final_ingredients_list.extend(detected_ingredients_list)
                
            except Exception as e:
                st.error(f"哎呀，摄像头识菜环节出了点小状况：{e}")

    # 将所有食材合并，去重
    final_ingredients_list = [item.strip() for item in final_ingredients_list if item.strip()]
    final_ingredients_str = '，'.join(set(final_ingredients_list)) # 去重并拼接回字符串

    st.markdown("---")
    
    # 居中提交按钮在侧边栏撑满
    submit_button = st.button("✨ 顺应天时，烹饪我的治愈食谱 ✨", use_container_width=True)


# ==========================================
# 🌟 第四部分：核心 AI 逻辑与摆盘输出 (主屏幕)
# ==========================================
if submit_button:
    # 确保合并后的食材不为空
    if not final_ingredients_str:
        st.sidebar.warning("请先告诉主厨食材！可以用照片或手动输入。")
    else:
        # --- 🌟 黑科技 3：沉浸式动效引擎 ---
        # 根据选的天气，点击生成时全屏下雪特效！
        if weather == "🌧️ 阴雨绵绵" or weather == "❄️ 寒冷刺骨" or weather == "🌬️狂风大作":
             st.snow()
        else:
             st.balloons()
        
        with st.spinner(f"👨‍🍳 主厨看了一眼窗外的【{weather}】，正为你构思治愈料理，请稍候..."):
            
            try:
                client = OpenAI(
                    api_key=api_key, 
                    base_url="https://open.bigmodel.cn/api/paas/v4/"
                )
                
                # 获取系统时间用于 Prompt
                current_time = datetime.utcnow() + timedelta(hours=8)
                current_hour = current_time.hour
                if 5 <= current_hour < 10: meal_time = "🌅 早餐"
                elif 10 <= current_hour < 14: meal_time = "☀️ 午餐"
                elif 14 <= current_hour < 17: meal_time = "☕ 下午茶"
                elif 17 <= current_hour < 21: meal_time = "🌆 晚餐"
                else: meal_time = "🌙 深夜食堂"

                # 严格结构化 Prompt
                prompt = f"""
                你是一个懂得心理学和营养学的米其林主厨。
                【当前情境】- 心情：【{mood}】，天气：【{weather}】，时间：【{meal_time}】，食材：【{final_ingredients_str}】
                
                请严格按照以下 Markdown 格式输出，不要改变标题结构，直接填充内容：
                
                ### 💌 主厨的疗愈寄语
                > *(结合天气、时间与心情的温暖安抚话语，要像写信一样温柔)*
                
                ---
                
                ### 🥘 专属菜单：[为这道菜起一个诗意且治愈的名字]
                
                **💡 治愈灵感**：*(一句话说明为什么这道菜能解【{mood}】的毒)*
                
                #### 🛒 食材确认
                *(列出需要的食材，使用短列表形式)*
                
                #### 👨‍🍳 料理魔法
                *(分步骤写做法，要简明，开头用 1️⃣ 2️⃣ 3️⃣ 等 Emoji)*
                
                ---
                
                ### 🧘‍♀️ 灶台前的 1 分钟冥想
                *(提供一段在切菜或等水烧开时可以做的简短正念冥想)*
                
                ### 🎧 沉浸式影音搭配
                - **🎵 推荐歌单**：*(2首音乐，并简述理由)*
                - **🎬 治愈放映室**：*(1部电影，并简述理由)*
                """
                
                # 文本生成
                response = client.chat.completions.create(
                    model="glm-4-flash",
                    messages=[
                        {"role": "system", "content": "你是一个充满关怀、知冷知热的情绪治愈主厨。"},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                # 绘画图片 (同样感知时间和天气，使用 CogView-3-Plus)
                image_prompt = f"一道精致的治愈系美食，时间是{meal_time}，天气{weather}。主要食材包含：{final_ingredients_str}。氛围：{mood}的解药，顶级美食摄影，高清，诱人。"
                image_response = client.images.generate(
                    model="cogview-3-plus", 
                    prompt=image_prompt
                )
                image_url = image_response.data[0].url
                
                # 模拟一个进度条，让沉浸感更足
                progress_bar = st.progress(0)
                for percent_complete in range(100):
                    time.sleep(0.01) # 模拟处理时间
                    progress_bar.progress(percent_complete + 1)
                
                # --- 左右宽屏分屏展示 & 卡片边框 ---
                st.markdown("### 🍽️ 你的专属情绪大餐已上桌")
                
                res_col_left, res_col_right = st.columns([6, 4])
                
                with res_col_left:
                    # 给文字区域套上高级边框容器
                    with st.container(border=True):
                        st.markdown(response.choices[0].message.content)
                    
                with res_col_right:
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
