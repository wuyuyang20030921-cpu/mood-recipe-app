import streamlit as st
from openai import OpenAI
import urllib.request # 用于下载图片的新工具

st.title("🍲 情绪食谱生成器 Mood-Recipe")
st.write("欢迎来到你的专属治愈厨房！(🎬 影音 & 视觉全能版)")

# 1. 密码框
api_key = st.text_input("🔑 请输入你的 智谱 API Key 唤醒主厨：", type="password")
mood = st.selectbox("你现在的心情是？", ["🤯 焦虑", "😭 难过", "🥱 疲惫", "🥳 开心", "😡 愤怒"])
ingredients = st.text_input("冰箱里有什么食材？ (例如：西红柿, 鸡蛋, 面条, 猪肉)")

# 2. 点击按钮触发
if st.button("✨ 生成我的治愈食谱"):
    if not api_key:
        st.warning("请先输入上面的 API Key 哦！")
    elif not ingredients:
        st.warning("请先告诉我你有哪些食材！")
    else:
        st.info("👨‍🍳 主厨正在为你构思料理，并绘制诱人的美食照片，请稍候...")
        
        try:
            # 连接到智谱的大脑
            client = OpenAI(
                api_key=api_key, 
                base_url="https://open.bigmodel.cn/api/paas/v4/"
            )
            
            # --- 🌟 升级 1：丰富菜单的 Prompt ---
            prompt = f"""
            你是一个懂得心理学和营养学的米其林主厨，擅长通过烹饪来治愈人心。
            用户今天的心情是：【{mood}】。
            用户现有的食材是：【{ingredients}】。
            请你输出：
            1. 一句共情和温暖的安抚话语。
            2. 用现有食材制作的治愈食谱，包含简明步骤。
            3. 一段50字左右的烹饪冥想指南。
            4. 影音搭配：推荐2首适合边做菜边听的音乐，以及1部最适合吃这道菜时观看的【治愈系电影】。
            请用清晰的 Markdown 格式排版，多用一些 Emoji 让排版更好看。
            """
            
            # 召唤文本主厨写菜谱
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {"role": "system", "content": "你是一个充满关怀的情绪治愈主厨。"},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # 展示文本结果
            st.success("✨ 你的专属治愈食谱出炉啦！")
            st.markdown("---")
            st.markdown(response.choices[0].message.content)
            st.markdown("---")
            
            # --- 🌟 升级 2：召唤画师主厨生成实物图 ---
            st.info("🎨 主厨正在进行最后的精美摆盘（生成图片中）...")
            image_prompt = f"一道精致的米其林级别治愈系美食，主要食材包含：{ingredients}。氛围：{mood}的解药，温暖，治愈，顶级美食摄影，高清，诱人。"
            
            # 调用智谱的 CogView-3 绘画模型
            image_response = client.images.generate(
                model="cogview-3-plus", 
                prompt=image_prompt
            )
            image_url = image_response.data[0].url
            
            # 在网页上展示图片
            st.image(image_url, caption="你的专属治愈系美食，请慢用 📸", use_column_width=True)
            
            # --- 🌟 升级 3：一键保存按钮 ---
            # 把图片地址转换成可以下载的文件流
            image_bytes = urllib.request.urlopen(image_url).read()
            st.download_button(
                label="💾 点击保存这道菜到手机相册",
                data=image_bytes,
                file_name="my_healing_recipe.png",
                mime="image/png"
            )
            
        except Exception as e:
            st.error(f"哎呀，厨房出了点小状况：{e}")
