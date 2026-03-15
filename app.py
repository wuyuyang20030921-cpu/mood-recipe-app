import streamlit as st

st.title("🍲 情绪食谱生成器 Mood-Recipe")
st.write("欢迎来到你的专属治愈厨房！")

# 获取用户输入
mood = st.selectbox("你现在的心情是？", ["🤯 焦虑", "😭 难过", "🥱 疲惫", "🥳 开心"])
ingredients = st.text_input("冰箱里有什么食材？ (例如：西红柿, 鸡蛋)")

if st.button("✨ 生成我的治愈食谱"):
    if ingredients:
        st.success("这只是一个测试界面！当你看到这段话，说明你的网页已经跑通啦！🎉")
    else:
        st.warning("请先输入食材哦！")