import time
import fal_client
import google.generativeai as genai
import streamlit as st

# Streamlit Page Setup
st.set_page_config(
    page_title="AI Drama Paid Auto-Video Pipeline", layout="wide"
)

st.title(
    "🎬 AI Drama Studio - ၅ ခန်းတွဲ အော်တို ဗီဒီယို ဆက်တိုက်ထုတ်စနစ် (Paid/API"
    " Queue)"
)
st.write(
    "ဇာတ်လမ်းများကို ၅ ခန်းတစ်တွဲစီ ဖန်တီးပြီး၊ fal.ai API ဖြင့် Scene"
    " တစ်ခုချင်းစီကို တစ်ခုပြီးမှ တစ်ခု အော်တို ဆက်တိုက် ထုတ်လုပ်မည်။"
)

# Sidebar - API Keys
st.sidebar.header("⚙️ API Keys Setup")
gemini_api_key = st.sidebar.text_input("Gemini API Key ထည့်ပါ", type="password")
fal_api_key = st.sidebar.text_input(
    "fal.ai API Key ထည့်ပါ (Paid/Credit)", type="password"
)

if fal_api_key:
  import os

  os.environ["FAL_KEY"] = fal_api_key

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

# Notebooks စီမံခန့်ခွဲမှု
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
    height=130,
)

scene_count = st.selectbox(
    "ဘယ်နှစ် Scene ထုတ်ချင်ပါသလဲ? (၅ ခန်းစီ အုပ်စုဖွဲ့ပါမည်)",
    [5, 10, 15, 30],
    index=0,
)

col1, col2 = st.columns(2)

with col1:
  generate_prompts_btn = st.button("🚀 ၅ ခန်းတွဲ ဇာတ်ညွှန်းနှင့် Prompts ထုတ်မည်")

with col2:
  next_volume_btn = st.button(
      f"📚 ဇာတ်လမ်းအကြမ်းအသစ်ဖြင့် (အတွဲ {current_nb['volume'] + 1}) သို့"
      " ဆက်ထုတ်မည်"
  )

# 1. Prompts ထုတ်လုပ်ခြင်း
if generate_prompts_btn or next_volume_btn:
  if not gemini_api_key:
    st.error("ကျေးဇူးပြု၍ ဘယ်ဘက်ခြမ်းတွင် Gemini API Key ထည့်ပါ")
  elif not story_input:
    st.error("ကျေးဇူးပြု၍ ဇာတ်လမ်းအကြမ်း အရင်ထည့်ပါ")
  else:
    try:
      genai.configure(api_key=gemini_api_key)
      model = genai.GenerativeModel("gemini-1.5-flash")

      prompt = f"""
            သင်သည် ကျွမ်းကျင်သော ဒရာမာဇာတ်ညွှန်းရေးဆရာနှင့် AI Video Prompt Specialist တစ်ဦး ဖြစ်သည်။ 
            အောက်ပါ ဇာတ်လမ်းအနှစ်ချုပ်ကို အခြေခံ၍ တိကျစွာ **Scene {scene_count} ခန်း** ပါဝင်သော ဇာတ်ညွှန်းနှင့် Prompts များကို **Scene ၅ ခန်း တစ်တွဲစီ (Batch)** သပ်သပ်ရပ်ရပ် အုပ်စုခွဲ၍ ရေးသားပေးပါ။
            
            - **Voiceover / Dialogue (အသံအတွက် စာသား):** မြန်မာဘာသာဖြင့် တိကျစွာ ရေးသားပေးပါ။
            - **Subtitle (စာတန်းထိုးအတွက်):** ရွေးချယ်ထားသော **{sub_language}** ဖြင့် တိကျစွာ ဖော်ပြပေးပါ။

            တစ်ခုချင်းစီအတွက် ဤ Format အတိုင်း တိကျစွာရေးပါ:
            - **Scene [နံပါတ်] (ကြာချိန် - ၁၀ စက္ကန့်)**
            - **Image Prompt:** (AI ပုံဖန်တီးရန် အင်္ဂလိပ်လို Detailed Prompt)
            - **Video Prompt:** (၁၀ စက္ကန့်စာ ဗီဒီယိုလှုပ်ရှားမှုနှင့် ကင်မရာပုံစံ - အင်္ဂလိပ်လို)
            - **Burmese Voiceover:** (ဇာတ်ကြောင်းပြော မြန်မာစကား)
            - **Subtitle ({sub_language}):** (ဗီဒီယိုပေါ်တွင် ပြသမည့် စာတန်းထိုးစာသား)
            
            ဇာတ်လမ်းအနှစ်ချုပ်:
            {story_input}
            """

      with st.spinner("ဇာတ်လမ်း Scene များကို ၅ ခန်းတစ်တွဲစီ ဖန်တီးနေပါပြီ..."):
        response = model.generate_content(prompt)
        st.success("✅ ၅ ခန်းတွဲ Prompts များ ထွက်ရှိလာပါပြီ!")

        new_section = (
            f"\n\n=== 🎬 {selected_notebook} - အတွဲ"
            f" ({current_nb['volume']}) [Subtitle: {sub_language}] ===\n"
            + response.text
        )
        current_nb["content"] += new_section

    except Exception as e:
      st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သွားပါသည်: {e}")

# 2. ရလဒ်များကို ပြသခြင်းနှင့် fal.ai API ဖြင့် တကယ့် ဗီဒီယို အော်တိုထုတ်မည့် Queue စနစ်
if current_nb["content"]:
  st.markdown("---")
  st.subheader("📋 ထွက်လာသော ၅ ခန်းတွဲ ဇာတ်ညွှန်းနှင့် Prompts များ")

  batch_text_area = st.text_area(
      "📌 ၅ ခန်းတွဲ အစုလိုက် (ထောင့်တွင် Copy ကူးရန် ခလုတ်ပါရှိသည်)",
      value=current_nb["content"],
      height=250,
      key="batch_prompts_textarea",
  )

  st.markdown("---")
  st.subheader(
      "⚡ fal.ai API ဖြင့် ၅ ခန်းတွဲ ဗီဒီယိုများကို တစ်ခုချင်း အော်တို ဆက်တိုက်"
      " ထုတ်လုပ်ရန်"
  )

  if st.button("🚀 ၅ ခန်းစလုံးကို fal.ai ဖြင့် အော်တို ဆက်တိုက် ထုတ်မည်"):
    if not fal_api_key:
      st.error("ကျေးဇူးပြု၍ ဘယ်ဘက်ခြမ်းတွင် fal.ai API Key ထည့်ပါ")
    else:
      scenes = [s.strip() for s in batch_text_area.split("Scene") if s.strip()]

      if len(scenes) == 0:
        st.warning("Scene ပုံစံ မတွေ့ရသေးပါ။ ကျေးဇူးပြု၍ Prompts အရင်ထုတ်ပါ။")
      else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        generated_videos = []

        for i, s_data in enumerate(scenes):
          scene_num = i + 1
          status_text.markdown(
              f"🔄 **Scene {scene_num}** ကို fal.ai ဖြင့် တကယ့် ဗီဒီယို"
              " ထုတ်လုပ်နေပါပြီ (ခေတ္တစောင့်ပါ)..."
          )

          try:
            arguments = {
                "prompt": (
                    "Cinematic drama shot, high quality, " + s_data[:300]
                )
            }

            handler = fal_client.submit("fal-ai/ltx-video", arguments=arguments)
            result = fal_client.result(handler)

            if "video" in result and "url" in result["video"]:
              vid_url = result["video"]["url"]
              generated_videos.append((scene_num, vid_url))
              st.success(
                  f"✅ Scene {scene_num} ဗီဒီယို အောင်မြင်စွာ ထွက်ရှိလာပါပြီ!"
              )
              st.video(vid_url)
            else:
              st.warning(
                  f"⚠️ Scene {scene_num} အတွက် ဗီဒီယိုလင့်ခ် မရရှိပါ။"
              )

            progress_bar.progress((i + 1) / len(scenes))

          except Exception as api_err:
            st.error(
                f"Scene {scene_num} ထုတ်လုပ်ရာတွင် အမှားဖြစ်သွားသည်:"
                f" {api_err}"
            )

        st.balloons()
        st.success(
            "🎉 ၅ ခန်းစလုံးအတွက် ဗီဒီယို အော်တိုထုတ်လုပ်ခြင်း အောင်မြင်စွာ"
            " ပြီးဆုံးပါပြီ!"
        )

        # 📥 ထွက်လာသော ဗီဒီယိုလင့်ခ်များကို ညာဘက်ထောင့် Copy ခလုတ်ပါသော Text Box များဖြင့် ပြသရန်
        if generated_videos:
          st.markdown("---")
          st.subheader("📥 ထွက်လာသော ဗီဒီယိုလင့်ခ်များ (Copy ကူးရန် ဘောင်များ)")

          all_links_text = "\n".join(
              [f"Scene {s_num}: {v_url}" for s_num, v_url in generated_videos]
          )
          st.text_area(
              "🔗 ဗီဒီယိုလင့်ခ် အားလုံး (All Links)",
              value=all_links_text,
              height=120,
              key="all_video_links_textarea",
          )

          st.markdown("##### 📌 Scene တစ်ခုချင်းအလိုက် လင့်ခ်များ Copy ကူးရန်:")
          for s_num, v_url in generated_videos:
            st.text_area(
                f"Scene {s_num} Video Link",
                value=v_url,
                height=70,
                key=f"unique_scene_link_box_{s_num}",
            )
