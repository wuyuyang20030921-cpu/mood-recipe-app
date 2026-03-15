import streamlit as st
from openai import OpenAI

st.title("🍲 情绪食谱生成器 Mood-Recipe")
st.write("欢迎来到你的专属治愈厨房！(🇨🇳 国产顶流主厨版)")

# 1. 密码框
api_key = st.text_input("🔑 请输入你的 智谱 API Key 唤醒主厨：", type="password")

# 2. 获取用户输入
mood = st.selectbox("你现在的心情是？", ["🤯 焦虑", "😭 难过", "🥱 疲惫", "🥳 开心", "😡 愤怒"])
ingredients = st.text_input("冰箱里有什么食材？ (例如：西红柿, 鸡蛋, 面条, 猪肉)")

# 3. 点击按钮触发
if st.button("✨ 生成我的治愈食谱"):
    if not api_key:
        st.warning("请先输入上面的 API Key 哦！")
    elif not ingredients:
        st.warning("请先告诉我你有哪些食材！")
    else:
        st.info("👨‍🍳 国产顶级主厨正在为你构思专属料理，请稍候...")
        
        try:
            # 💡 核心代码：使用通用的 OpenAI 库，连接到智谱的大脑
            client = OpenAI(
                api_key=api_key, 
                base_url="https://open.bigmodel.cn/api/paas/v4/" # 指向智谱的服务器
            )
            
            prompt = f"""
            你是一个懂得心理学和营养学的米其林主厨，擅长通过烹饪来治愈人心。
            用户今天的心情是：【{mood}】。
            用户现有的食材是：【{ingredients}】。
            请你输出：
            1. 一句共情和温暖的安抚话语。
            2. 用现有食材制作的治愈食谱，包含简明步骤。
            3. 一段50字左右的烹饪冥想指南。
            4. 推荐2首适合边做这道菜边听的音乐。
            请用清晰的 Markdown 格式排版，多用一些 Emoji 让排版更好看。
            """
            
            # 召唤永远免费的 glm-4-flash 主厨
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {"role": "system", "content": "你是一个充满关怀的情绪治愈主厨。"},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # 展示结果
            st.success("✨ 你的专属治愈食谱出炉啦！")
            st.markdown("---")
            st.markdown(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"哎呀，厨房出了点小状况：{e}")
