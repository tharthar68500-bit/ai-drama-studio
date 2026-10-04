import google.generativeai as genai
import streamlit as st

# Streamlit Page Setup
st.set_page_config(page_title="AI Drama Studio", layout="wide")

# စာမျက်နှာ ခေါင်းစဉ်
st.title("🎬 AI Drama Studio - အဆင့် (၁)")
st.write(
    "ဇာတ်လမ်းအနှစ်ချုပ်ထည့်ပါ၊ AI မှ Episode ခွဲခြားပေးခြင်း၊ ရွေးချယ်ထားသော"
    " Scene အရေအတွက်အလိုက် ဇာတ်ကွက်များထုတ်ပေးခြင်းနှင့် ဇာတ်ကောင်အချက်အလက်များကို"
    " ဖန်တီးပေးမည်။"
)

# Sidebar - API Key ထည့်ရန်
st.sidebar.header("API Configuration")
api_key = st.sidebar.text_input("Gemini API Key ထည့်ပါ", type="password")

# ဇာတ်လမ်း အနှစ်ချုပ် ထည့်ရန်နေရာ
story_input = st.text_area(
    "သင့်ရဲ့ ဇာတ်လမ်းအနှစ်ချုပ် (Story) ကို ဤနေရာတွင် ရေးပါ...", height=150
)

# Scene အရေအတွက် ရွေးချယ်စရာ (selectbox)
scene_count = st.selectbox(
    "ဘယ်နှစ် Scene ထုတ်ချင်ပါသလဲ?", [10, 20, 30, 50, 100]
)

# ဇာတ်လမ်း ထုတ်လုပ်မည့် ခလုတ်
if st.button("ဇာတ်လမ်း စတင်ဖန်တီးမည်"):
  if not api_key:
    st.error("ကျေးဇူးပြု၍ ဘယ်ဘက်ခြမ်းတွင် Gemini API Key ထည့်ပါ")
  elif not story_input:
    st.error("ကျေးဇူးပြု၍ ဇာတ်လမ်းအနှစ်ချုပ် အရင်ထည့်ပါ")
  else:
    try:
      # Gemini API ကို ချိတ်ဆက်ခြင်း
      genai.configure(api_key=api_key)
      model = genai.GenerativeModel("gemini-3.8-flash")

      # AI အတွက် Prompt တည်ဆောက်ခြင်း
      prompt = f"""
            သင်သည် ကျွမ်းကျင်သော ဇာတ်ညွှန်းရေးဆရာတစ်ဦး ဖြစ်သည်။ အောက်ပါ ဇာတ်လမ်းအနှစ်ချုပ်ကို အခြေခံ၍ အောက်ပါအတိုင်း အသေးစိတ် ဖန်တီးပေးပါ။
            
            ထွက်ရှိလာမည့် Scene စုစုပေါင်း အရေအတွက်မှာ တိကျစွာ **{scene_count} ခန်း** ရှိရမည်။
            
            1. **Story Structure (ဇာတ်လမ်းဖွဲ့စည်းပုံ)**
            2. **Detailed Scenes (Scene ၁ မှ {scene_count} ထိ အသေးစိတ် ဇာတ်ကွက်များ၊ ဇာတ်ကောင်ပြောမယ့် စာသားများ)**
            
            ဇာတ်လမ်းအနှစ်ချုပ်:
            {story_input}
            """

      with st.spinner(
          f"ဇာတ်လမ်း Scene {scene_count} ခန်းကို ဖန်တီးနေပါပြီ..."
      ):
        response = model.generate_content(prompt)
        st.success("ဇာတ်လမ်း ထွက်ရှိလာပါပြီ!")
        st.markdown(response.text)

    except Exception as e:
      st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သွားပါသည်: {e}")
