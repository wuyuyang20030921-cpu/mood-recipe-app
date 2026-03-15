import streamlit as st
import google.generativeai as genai

st.title("🍲 情绪食谱生成器 Mood-Recipe")
st.write("欢迎来到你的专属治愈厨房！(☁️ 云端完全体版)")

api_key = st.text_input("🔑 请输入你的 Gemini API Key 唤醒主厨：", type="password")
mood = st.selectbox("你现在的心情是？", ["🤯 焦虑", "😭 难过", "🥱 疲惫", "🥳 开心", "😡 愤怒"])
ingredients = st.text_input("冰箱里有什么食材？ (例如：西红柿, 鸡蛋, 面条, 猪肉)")

if api_key:
    genai.configure(api_key=api_key)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected_model = st.selectbox("👨‍🍳 请手动挑选一位当班主厨：", available_models)
    except Exception as e:
        selected_model = None
        st.warning("等待连接厨房后勤...")

if st.button("✨ 生成我的治愈食谱"):
    if not api_key:
        st.warning("请先输入上面的 API Key 哦！")
    elif not ingredients:
        st.warning("请先告诉我你有哪些食材！")
    elif not selected_model:
        st.error("哎呀，还没有成功请到主厨，请检查 API Key。")
    else:
        st.info(f"👨‍🍳 正在呼叫 {selected_model.replace('models/', '')} 为你炒菜，请稍候...")
        try:
            model = genai.GenerativeModel(selected_model)
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
            response = model.generate_content(prompt)
            st.success("✨ 你的专属治愈食谱出炉啦！")
            st.markdown("---")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"哎呀，厨房出了点小状况：{e}")
