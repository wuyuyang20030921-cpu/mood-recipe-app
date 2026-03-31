import streamlit as st
from openai import OpenAI
import urllib.request
from datetime import datetime, timedelta

# 设置网页标题和图标
st.set_page_config(page_title="情绪食谱", page_icon="🍲") 

st.title("🍲 情绪食谱生成器 Mood-Recipe")
st.write("欢迎来到你的专属治愈厨房！(🌦️ 知冷知热的贴心主厨版)")

# --- 🌟 核心升级 1：获取真实时间并判断用餐场景 ---
# 云端服务器默认是 UTC 时间，我们加上 8 小时转换为北京时间
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

# 在页面上方温柔地提示当前时间
st.info(f"⏱️ 主厨看了一眼墙上的时钟：现在是 {current_time.strftime('%H:%M')}，正是为你准备【{meal_time.split(' ')[0]}】的时候。")

# --- 🌟 核心升级 2：优化的分列排版与天气输入 ---
col1, col2 = st.columns(2)
with col1:
    mood = st.selectbox("你现在的心情是？", ["🤯 焦虑", "😭 难过", "🥱 疲惫", "🥳 开心", "😡 愤怒"])
    weather = st.selectbox("窗外的天气怎样？", ["☀️ 晴朗明媚", "🌧️ 阴雨绵绵", "☁️ 沉闷多云", "❄️ 寒冷刺骨", "🌬️ 狂风大作"])
with col2:
    ingredients = st.text_input("冰箱里有什么食材？", placeholder="例如：西红柿, 鸡蛋, 面条, 猪肉")

# 隐形保险箱读取 API Key
api_key = st.secrets["ZHIPU_API_KEY"]

st.markdown("---")
# 按钮也做个居中美化
if st.button("✨ 顺应天时，生成我的治愈食谱", use_container_width=True):
    if not ingredients:
        st.warning("请先告诉我你有哪些食材！")
    else:
        st.success("👨‍🍳 主厨正在感受窗外的天气，为你构思专属料理...")
        
        try:
            client = OpenAI(
                api_key=api_key, 
                base_url="https://open.bigmodel.cn/api/paas/v4/"
            )
            
            # --- 🌟 核心升级 3：注入灵魂的 Prompt ---
            prompt = f"""
            你是一个懂得心理学和营养学的米其林主厨。
            
            【当前情境】
            - 用户心情：【{mood}】
            - 窗外天气：【{weather}】
            - 当前时间：【{meal_time}】
            - 现有食材：【{ingredients}】（可适当补充基础调料）
            
            【你的任务】
            请务必结合以上所有情境（尤其是天气和时间），输出：
            1. 🧡 一句安抚话语（必须巧妙地提到当前的天气、时间与心情的联系）。
            2. 🥘 用现有食材制作的治愈食谱。做法和口味必须极其契合当前的时间和天气（例如：下雨的深夜适合热汤面，晴朗的早晨适合清爽的做法）。
            3. 🧘 一段50字左右的烹饪冥想指南。
            4. 🎬 影音搭配：推荐2首适合边做菜边听的音乐，以及1部最适合此时此刻观看的【治愈系电影】。
            
            请用清晰的 Markdown 格式排版，多用一些 Emoji。
            """
            
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {"role": "system", "content": "你是一个充满关怀、知冷知热的情绪治愈主厨。"},
                    {"role": "user", "content": prompt}
                ]
            )
            
            st.markdown(response.choices[0].message.content)
            st.markdown("---")
            
            st.info("🎨 主厨正在进行最后的精美摆盘（生成图片中）...")
            # 让画图模型也感知天气和时间
            image_prompt = f"一道精致的治愈系美食，时间是{meal_time.split(' ')[0]}，天气{weather}。主要食材包含：{ingredients}。氛围：{mood}的解药，顶级美食摄影，高清，诱人。"
            
            image_response = client.images.generate(
                model="cogview-3-plus", 
                prompt=image_prompt
            )
            image_url = image_response.data[0].url
            
            st.image(image_url, caption=f"伴随 {weather.split(' ')[1]} 的天气，你的专属餐点，请慢用 📸", use_column_width=True)
            
            image_bytes = urllib.request.urlopen(image_url).read()
            st.download_button(
                label="💾 点击保存这道菜到手机相册",
                data=image_bytes,
                file_name="my_healing_recipe.png",
                mime="image/png",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"哎呀，厨房出了点小状况：{e}")
