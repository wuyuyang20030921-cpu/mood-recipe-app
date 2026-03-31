import streamlit as st
from openai import OpenAI
import urllib.request
from datetime import datetime, timedelta

# --- 🌟 改造 1：开启宽屏模式 ---
# layout="wide" 会让你的网页瞬间舒展开来，占满整个屏幕
st.set_page_config(page_title="情绪食谱", page_icon="🍲", layout="wide") 

st.title("🍲 情绪食谱生成器 Mood-Recipe")
st.write("欢迎来到你的专属治愈厨房！(🎨 米其林高级摆盘版)")

# 获取真实时间并判断用餐场景
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

st.info(f"⏱️ 主厨看了一眼墙上的时钟：现在是 {current_time.strftime('%H:%M')}，正是为你准备【{meal_time.split(' ')[0]}】的时候。")
st.markdown("---")

# --- 🌟 改造 2：点餐区三列并排 ---
st.markdown("### 📝 第一步：写下今天的点餐单")
# 将屏幕平分为三等份
col_input1, col_input2, col_input3 = st.columns(3)

with col_input1:
    mood = st.selectbox("现在的感觉？", ["🤯 焦虑", "😭 难过", "🥱 疲惫", "🥳 开心", "😡 愤怒"])
with col_input2:
    weather = st.selectbox("窗外天气？", ["☀️ 晴朗明媚", "🌧️ 阴雨绵绵", "☁️ 沉闷多云", "❄️ 寒冷刺骨", "🌬️ 狂风大作"])
with col_input3:
    ingredients = st.text_input("冰箱里有啥？", placeholder="例如：西红柿, 鸡蛋, 面条")

api_key = st.secrets["ZHIPU_API_KEY"]
st.markdown("<br>", unsafe_allow_html=True) # 加一点空行留白

# --- 🌟 居中按钮的小魔法 ---
# 按 1:2:1 的比例分三列，把按钮放在中间那列，它就居中了！
col_spacer1, col_btn, col_spacer3 = st.columns([1, 2, 1])
with col_btn:
    submit_button = st.button("✨ 顺应天时，开始烹饪我的治愈食谱 ✨", use_container_width=True)

st.markdown("---")

# --- 开始处理核心逻辑 ---
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
            
            prompt = f"""
            你是一个懂得心理学和营养学的米其林主厨。
            【当前情境】- 心情：【{mood}】，天气：【{weather}】，时间：【{meal_time}】，食材：【{ingredients}】
            请输出：
            1. 🧡 一句安抚话语（巧妙结合天气、时间与心情）。
            2. 🥘 专属治愈食谱（极度契合当前的时间和天气）。
            3. 🧘 50字烹饪冥想指南。
            4. 🎬 影音搭配：2首音乐，1部治愈系电影。
            请用清晰的 Markdown 格式排版，多用 Emoji。
            """
            
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {"role": "system", "content": "你是一个充满关怀、知冷知热的情绪治愈主厨。"},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # 让画图模型开始工作
            image_prompt = f"一道精致的治愈系美食，时间是{meal_time.split(' ')[0]}，天气{weather}。主要食材包含：{ingredients}。氛围：{mood}的解药，顶级美食摄影，高清，诱人。"
            image_response = client.images.generate(
                model="cogview-3-plus", 
                prompt=image_prompt
            )
            image_url = image_response.data[0].url
            
            # --- 🌟 改造 3：输出区左右分屏展示 ---
            st.markdown("### 🍽️ 你的专属情绪大餐已上桌")
            
            # 将下方区域按 6:4 的比例分为左右两列
            res_col_left, res_col_right = st.columns([6, 4])
            
            with res_col_left:
                # 左边放文字：食谱、冥想、电影推荐
                st.markdown(response.choices[0].message.content)
                
            with res_col_right:
                # 右边放视觉：美食图片和下载按钮
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
