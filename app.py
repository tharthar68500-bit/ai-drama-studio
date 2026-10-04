import time
import google.generativeai as genai
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="တရုတ်ဒရာမာ ဇာတ်ညွှန်းနှင့် ဗီဒီယို အော်တိုထုတ်စနစ်", layout="wide"
)

st.title("🎬 တရုတ်ဒရာမာ ဇာတ်ညွှန်းနှင့် ဗီဒီယို အော်တိုထုတ်လုပ်ရေး စနစ်")
st.write(
    "ဇာတ်လမ်းအကြမ်းထည့်ပါ -> ဇာတ်ညွှန်း Prompts များ အော်တိုထုတ်ပါ -> Paid API"
    " ဖြင့် ဗီဒီယိုများ ဆက်တိုက်ထုတ်ပါ"
)

# Sidebar - API Keys Setup
st.sidebar.header("⚙️ API Keys Setup")
gemini_api_key = st.sidebar.text_input("Gemini API Key ထည့်ပါ", type="password")
kling_api_key = st.sidebar.text_input(
    "Kling / Paid API Key ထည့်ပါ", type="password"
)

# 1. ဇာတ်လမ်း အကြမ်း ရိုက်ထည့်ရန် နေရာ
st.markdown("---")
st.subheader("📝 အပိုင်း (၁) ဇာတ်လမ်းအကြမ်းမှ ဇာတ်ညွှန်း Prompts များ ထုတ်ရန်")

story_input = st.text_area(
    "✍️ တရုတ်ဒရာမာ ဇာတ်လမ်းအကြမ်း (သို့မဟုတ် ဆက်လက်ဖြစ်ပျက်မည့်အရာများ) ကို"
    " ဤတွင်ရေးပါ...",
    height=130,
)

total_scenes = st.selectbox(
    "ဘယ်နှစ်ခန်း (Scenes) စုစုပေါင်း ထုတ်ချင်ပါသလဲ?",
    [5, 10, 15, 20, 25, 30],
    index=0,
)

# ဇာတ်ညွှန်းထုတ်မည့် ခလုတ်
if st.button(f"🚀 ဇာတ်လမ်း Scene ({total_scenes} ခန်းစာ) ဇာတ်ညွှန်းထုတ်မည်"):
  if not gemini_api_key:
    st.error("ကျေးဇူးပြု၍ Gemini API Key ကို ထည့်ပါ")
  elif not story_input:
    st.error("ကျေးဇူးပြု၍ ဇာတ်လမ်းအကြမ်း အရင်ထည့်ပါ")
  else:
    try:
      genai.configure(api_key=gemini_api_key)
      model = genai.GenerativeModel("gemini-1.5-flash")

      prompt = f"""
            သင်သည် တရုတ်ဒရာမာဇာတ်လမ်းနှင့် AI Video Prompt ကျွမ်းကျင်ပညာရှင် ဖြစ်သည်။ 
            အောက်ပါ ဇာတ်လမ်းအကြမ်းကို အခြေခံ၍ တိကျစွာ **စုစုပေါင်း Scene {total_scenes} ခန်း** ပါဝင်သော ဇာတ်ညွှန်းနှင့် Prompts များကို အစဉ်လိုက် (Scene 1 မှ Scene {total_scenes} ထိ) ဇာတ်ကြောင်းစီးချက် (Rhythm) မပြတ်ဘဲ အသေးစိတ် ရေးသားပေးပါ။
            
            - **Style:** Traditional Chinese costume drama style, cinematic, high quality, dramatic lighting, 4k.
            
            တစ်ခုချင်းစီအတွက် ဤ Format အတိုင်း တိကျစွာရေးပါ:
            - **Scene [နံပါတ်]**
            - **Video Prompt:** (AI ဗီဒီယိုဖန်တီးရန် အင်္ဂလိပ်လို Detailed Prompt)
            
            ဇာတ်လမ်းအကြမ်း:
            {story_input}
            """

      with st.spinner(
          f"တရုတ်ဒရာမာ အပိုင်း ({total_scenes}) ခန်းစာ ဇာတ်ညွှန်းများကို"
          " ဖန်တီးနေပါပြီ..."
      ):
        response = model.generate_content(prompt)
        st.session_state["script_content"] = response.text
        st.success("✅ ဇာတ်ညွှန်း Prompts များ အောင်မြင်စွာ ထွက်ရှိလာပါပြီ!")

    except Exception as e:
      st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သွားပါသည်: {e}")


# 2. ထွက်လာသော ဇာတ်ညွှန်းများကို အသုံးပြု၍ ဗီဒီယို အော်တိုထုတ်မည့်နေရာ
st.markdown("---")
st.subheader(
    "🎬 အပိုင်း (၂) ဇာတ်ညွှန်းများမှ ဗီဒီယိုများသို့ အော်တို ဆက်တိုက်ထုတ်မည့်စနစ်"
)

# ဇာတ်ညွှန်း Prompts များကို ထည့်ရန် (အပေါ်က ထွက်လာတာကို အော်တို ယူသုံးမည်)
videos_input_text = st.text_area(
    "ဗီဒီယိုထုတ်မည့် Prompts များကို ဤနေရာတွင် စစ်ဆေးပါ (သို့မဟုတ် ကူးထည့်ပါ)",
    value=st.session_state.get("script_content", ""),
    height=200,
)

# ခလုတ်တစ်ချက်နှိပ်ရုံဖြင့် အော်တို ဗီဒီယိုများ စက်တိုက်ထွက်မည့်နေရာ
if st.button("🚀 ဗီဒီယိုများ အားလုံးကို အော်တို ဆက်တိုက် ထုတ်မည်"):
  if not kling_api_key:
    st.error("ကျေးဇူးပြု၍ Kling / Paid API Key ထည့်ပါ")
  elif not videos_input_text:
    st.error("ဗီဒီယို Prompts များ မရှိသေးပါ")
  else:
    # စာသားများကို တစ်ကြောင်းချင်း (သို့မဟုတ် Scene အလိုက်) ခွဲထုတ်ခြင်း
    prompts_list = [
        p.strip() for p in videos_input_text.split("\n") if p.strip()
    ]

    if len(prompts_list) == 0:
      st.warning("Prompt စာသားများ မတွေ့ရပါ။")
    else:
      progress_bar = st.progress(0)
      status_text = st.empty()
      generated_videos = []

      # Queue Loop - တစ်ခုချင်းစီကို API သို့ပို့၍ အော်တိုထုတ်ခြင်း
      for index, prompt_text in enumerate(prompts_list):
        scene_num = index + 1
        status_text.markdown(
            f"🔄 **Video {scene_num} / {len(prompts_list)}** ကို API ဖြင့်"
            " တည်ဆောက်နေပါပြီ..."
        )

        try:
          # API ချိတ်ဆက်ရန် Header နှင့် Payload
          headers = {
              "Authorization": f"Bearer {kling_api_key}",
              "Content-Type": "application/json",
          }

          payload = {
              "prompt": prompt_text,
              "style": "Traditional Chinese costume drama, 4k, cinematic",
          }

          # (ဒီနေရာမှာ ကိုယ်သုံးမယ့် Kling / Paid API ရဲ့ Request ကို တိုက်ရိုက်ချိတ်ပါမည်)
          time.sleep(2)  # စမ်းသပ်ရန် အချိန်ခဏစောင့်ခြင်း

          # ပြီးသွားသော ဗီဒီယိုလင့်ခ် (ဥပမာပြ ဗီဒီယိုလင့်ခ်)
          simulated_video_url = (
              "https://www.w3schools.com/html/mov_bbb.mp4"  # တကယ့် API URL
          )

          generated_videos.append((scene_num, simulated_video_url))
          st.success(f"✅ Video {scene_num} ထွက်လာပါပြီ!")
          st.video(simulated_video_url)

        except Exception as e:
          st.error(f"Video {scene_num} တွင် အမှားဖြစ်သွားသည်: {e}")

        progress_bar.progress((index + 1) / len(prompts_list))

      st.balloons()
      st.success("🎉 ဗီဒီယို အားလုံး အော်တို ထုတ်လုပ်ပြီးပါပြီ!")

      # ထွက်လာသမျှ ဗီဒီယိုများကို စုစည်းပြသပေးခြင်း
      if generated_videos:
        st.markdown("---")
        st.subheader("📥 ထွက်လာသည့် ဗီဒီယိုများ အားလုံး:")
        for s_num, v_url in generated_videos:
          st.markdown(f"- **Video {s_num}:** [Download Video]({v_url})")
