import google.generativeai as genai
import streamlit as st

# Streamlit Page Setup
st.set_page_config(
    page_title="AI Drama 5-Scene Batch Generator", layout="wide"
)

st.title(
    "🎬 AI Drama Studio - ၅ ခန်းတွဲ (5-Scene Batch) ဇာတ်ညွှန်းနှင့် Prompts"
    " ထုတ်စက်"
)
st.write(
    "ဇာတ်လမ်းများကို Scene ၅ ခန်းစီ အုပ်စုဖွဲ့၍ Image Prompt၊ Video Prompt၊"
    " မြန်မာအသံထွက်နှင့် လိုချင်သည့် Subtitle ဘာသာစကားဖြင့်"
    " အသန့်ရှင်းဆုံးထုတ်ပေးမည်။"
)

# Sidebar - API Key နှင့် Settings
st.sidebar.header("⚙️ Settings")
api_key = st.sidebar.text_input("Gemini API Key ထည့်ပါ", type="password")

# Subtitle Language Selector
st.sidebar.markdown("---")
st.sidebar.subheader("🔤 စာတန်းထိုး (Subtitle) ဘာသာစကား")
sub_language = st.sidebar.selectbox(
    "Subtitle Language",
    [
        "မြန်မာ (Burmese Subtitle)",
        "အင်္ဂလိပ် (English Subtitle)",
        "တရုတ် (Chinese Subtitle)",
        "ထိုင်း (Thai Subtitle)",
    ],
)

# Notebooks များကို session_state ထဲတွင် သိမ်းဆည်းရန်
if "notebooks" not in st.session_state:
  st.session_state.notebooks = {
      "ဇာတ်လမ်းအသစ် (Notebook 1)": {"content": "", "volume": 1}
  }

selected_notebook = st.sidebar.selectbox(
    "📁 Notebook ရွေးရန်", list(st.session_state.notebooks.keys())
)

new_notebook_name = st.sidebar.text_input("➕ Notebook အသစ် ဖန်တီးရန်")
if st.sidebar.button("Notebook အသစ်လုပ်မည်") and new_notebook_name:
  if new_notebook_name not in st.session_state.notebooks:
    st.session_state.notebooks[new_notebook_name] = {"content": "", "volume": 1}
    st.rerun()

current_nb = st.session_state.notebooks[selected_notebook]

st.subheader(
    f"📖 လက်ရှိ Notebook: {selected_notebook} (အတွဲ {current_nb['volume']})"
)

# ဇာတ်လမ်း အနှစ်ချုပ် Input
story_input = st.text_area(
    f"✍️ အတွဲ ({current_nb['volume']}) အတွက် ဇာတ်လမ်းအကြမ်း (သို့မဟုတ်)"
    " ဆက်လက်ဖြစ်ပျက်မည့် အကြောင်းအရာများ...",
    height=150,
)

# Scene အရေအတွက် (၅ ခန်းတွဲကို အခြေခံသည်)
scene_options = [
    5,
    10,
    15,
    30,
    50,
    70,
    85,
    100,
    110,
    120,
    130,
    150,
]
scene_count = st.selectbox(
    "ဘယ်နှစ် Scene ထုတ်ချင်ပါသလဲ? (၅ ခန်းစီ အုပ်စုဖွဲ့ပါမည်)",
    scene_options,
    index=0,
)

col1, col2 = st.columns(2)

with col1:
  generate_btn = st.button("🚀 ၅ ခန်းတွဲ ဇာတ်ညွှန်းနှင့် Prompts စတင်ထုတ်မည်")

with col2:
  next_volume_btn = st.button(
      f"📚 ဇာတ်လမ်းအားပြန်ဆက်ရန် (အတွဲ {current_nb['volume'] + 1}) သို့ ဆက်ထုတ်မည်"
  )

if generate_btn or next_volume_btn:
  if not api_key:
    st.error("ကျေးဇူးပြု၍ ဘယ်ဘက်ခြမ်းတွင် Gemini API Key ထည့်ပါ")
  elif not story_input:
    st.error("ကျေးဇူးပြု၍ ဇာတ်လမ်းအကြမ်း အရင်ထည့်ပါ")
  else:
    try:
      genai.configure(api_key=api_key)
      model = genai.GenerativeModel("gemini-1.5-flash")

      prompt = f"""
            သင်သည် ကျွမ်းကျင်သော ဒရာမာဇာတ်ညွှန်းရေးဆရာနှင့် AI Video Prompt Specialist တစ်ဦး ဖြစ်သည်။ 
            အောက်ပါ ဇာတ်လမ်းအနှစ်ချုပ်ကို အခြေခံ၍ တိကျစွာ **Scene {scene_count} ခန်း** ပါဝင်သော ဇာတ်ညွှန်းနှင့် Prompts များကို **Scene ၅ ခန်း တစ်တွဲစီ (Batch: Scene 1-5, 6-10 စသည်ဖြင့်)** သပ်သပ်ရပ်ရပ် အုပ်စုခွဲ၍ ရေးသားပေးပါ။
            
            - **Voiceover / Dialogue (အသံအတွက် စာသား):** မြန်မာဘာသာဖြင့် တိကျစွာ ရေးသားပေးပါ။
            - **Subtitle (စာတန်းထိုးအတွက်):** ရွေးချယ်ထားသော **{sub_language}** ဖြင့် တိကျစွာ ဖော်ပြပေးပါ။

            တစ်ခုချင်းစီအတွက် ဤ Format အတိုင်း တိကျစွာရေးပါ:
            - **[Batch / Scene နံပါတ်] (ကြာချိန် - ၁၀ စက္ကန့်)**
            - **Image Prompt:** (AI ပုံဖန်တီးရန် အင်္ဂလိပ်လို Detailed Prompt)
            - **Video Prompt:** (၁၀ စက္ကန့်စာ ဗီဒီယိုလှုပ်ရှားမှုနှင့် ကင်မရာပုံစံ - အင်္ဂလိပ်လို)
            - **Burmese Voiceover (အသံအတွက် မြန်မာစာသား):** (ဇာတ်ကောင်ပြောမည့် သို့မဟုတ် ဇာတ်ကြောင်းပြော မြန်မာစကား)
            - **Subtitle ({sub_language}):** (ဗီဒီယိုပေါ်တွင် ပြသမည့် စာတန်းထိုးစာသား)
            
            (မှတ်ချက်။ ။ Scene ၅ ခန်းပြည့်တိုင်း "--- 🔄 [Next Batch] ---" ဟု ခြားပေးပါ)

            ဇာတ်လမ်းအနှစ်ချုပ်:
            {story_input}
            """

      action_text = f"ဇာတ်လမ်း Scene {scene_count} ခန်းကို ၅ ခန်းတစ်တွဲစီ ဖန်တီးနေပါပြီ..."

      with st.spinner(action_text):
        response = model.generate_content(prompt)
        st.success(
            f"✅ {selected_notebook} - အတွဲ ({current_nb['volume']})"
            f" (Scene {scene_count} ခန်း) ၏ ၅ ခန်းတွဲ Prompts များ ထွက်ရှိလာပါပြီ!"
        )

        new_section = (
            f"\n\n=== 🎬 {selected_notebook} - အတွဲ"
            f" ({current_nb['volume']}) [Subtitle: {sub_language}] ===\n"
            + response.text
        )
        current_nb["content"] += new_section

    except Exception as e:
      st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သွားပါသည်: {e}")

# ရလဒ်များကို ပြသရန်နှင့် ၅ ခန်းတွဲ အစုလိုက် ဘောင်ထောင့် Copy ခလုတ်များဖြင့် ပြသရန်
if current_nb["content"]:
  st.markdown("---")
  st.subheader(
      f"📜 {selected_notebook} - ၅ ခန်းတွဲ ဇာတ်လမ်း၊ Prompts နှင့် စာတန်းထိုးများ"
  )

  st.text_area(
      "📋 ၅ ခန်းတွဲ အစုလိုက် (အားလုံးကို Copy ကူးရန်)",
      value=current_nb["content"],
      height=200,
      key="all_content_textarea",
  )

  st.markdown("---")
  st.markdown(
      "##### 📌 ၅ ခန်းတွဲ (Batch) တစ်ခုချင်းအလိုက် သီးသန့် Copy ကူးရန်"
      " ဘောင်များ:"
  )

  batches = [
      b.strip() for b in current_nb["content"].split("--- 🔄") if b.strip()
  ]

  if len(batches) > 0:
    for idx, batch_text in enumerate(batches):
      st.text_area(
          f"📦 ၅ ခန်းတွဲ အုပ်စု (Batch {idx + 1}) - Copy ကူးရန်",
          value=batch_text,
          height=150,
          key=f"batch_box_{idx}",
      )
  else:
    scenes = [
        s.strip()
        for s in current_nb["content"].split("---")
        if "Scene" in s or "[" in s
    ]
    for idx, scene_text in enumerate(scenes):
      if len(scene_text) > 20:
        st.text_area(
            f"📌 Scene အုပ်စု ({idx + 1}) - Copy ကူးရန်",
            value=scene_text,
            height=120,
            key=f"scene_box_{idx}",
        )
import time
import streamlit as st
# ==========================================
# ဇာတ်ညွှန်းများမှ ဗီဒီယိုများသို့ အော်တို ဆက်တိုက်ထုတ်မည့်စနစ်
# ==========================================
st.markdown("---")
st.subheader("🎬 ဇာတ်ညွှန်းများမှ ဗီဒီယိုများသို့ အော်တို ဆက်တိုက်ထုတ်မည့်စနစ်")
# API Key ထည့်ရန် နေရာ
kling_api_key = st.text_input(
    "🔑 Kling API Key (သို့မဟုတ် သုံးမည့် Paid API Key) ကို ဤတွင်ထည့်ပါ",
    type="password",
)
# ဇာတ်ညွှန်း Prompts များကို ထည့်ရန် သို့မဟုတ် အပေါ်ကဟာကို ယူသုံးရန်
videos_input_text = st.text_area(
    "ဗီဒီယိုထုတ်မည့် Prompts များကို ဤနေရာတွင် စစ်ဆေးပါ (သို့မဟုတ် ကူးထည့်ပါ)",
    value=st.session_state.get(
        "script_content", ""
    ),  # အပေါ်က ထွက်လာတာကို အော်တို ယူသုံးမည်
    height=200,
)
# ခလုတ်တစ်ချက်နှိပ်ရုံဖြင့် အော်တို ဗီဒီယို ၅ ပုဒ် (သို့မဟုတ် အားလုံး) စက်တိုက်ထွက်မည့်နေရာ
if st.button("🚀 ဗီဒီယိုများ အားလုံးကို အော်တို ဆက်တိုက် ထုတ်မည်"):
  if not kling_api_key:
    st.error("ကျေးဇူးပြု၍ API Key ထည့်ပါ")
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
          time.sleep(2)  # စမ်းသပ်ရန် အချိန်ခဏစောင့်ခြင်း
          # ပြီးသွားသော ဗီဒီယိုလင့်ခ် (ဥပမာပြ ဗီဒီယိုလင့်ခ်)
          simulated_video_url = (
              "https://www.w3schools.com/html/mov_bbb.mp4"  # တကယ့် API URL
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


