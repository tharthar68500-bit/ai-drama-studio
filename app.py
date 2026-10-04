import re
import time
import google.generativeai as genai
import streamlit as st

# Streamlit Page Setup
st.set_page_config(
    page_title="AI Drama 5-Scene Batch Generator", layout="wide"
)

st.title("🎬 AI Drama Studio - ၅ ခန်းတွဲ ဇာတ်ညွှန်းနှင့် Prompts ထုတ်စက်")
st.write(
    "ဇာတ်လမ်းများကို Scene ၅ ခန်းစီ အုပ်စုဖွဲ့၍ Image Prompt၊ Video Prompt၊"
    " မြန်မာအသံထွက်နှင့် Subtitle များကို သပ်သပ်ရပ်ရပ် ထုတ်ပေးမည်။"
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
    f"✍ အတွဲ ({current_nb['volume']}) အတွက် ဇာတ်လမ်းအကြမ်း (သို့မဟုတ်)"
    " ဆက်လက်ဖြစ်ပျက်မည့် အကြောင်းအရာများ...",
    height=150,
)

# Scene အရေအတွက်
scene_options = [5, 10, 15, 30, 50, 70, 85, 100, 120, 150]
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
      f"📚 ဇာတ်လမ်းတွဲအားဆက်လက်ဖန်တီးမည် (အတွဲ {current_nb['volume'] + 1}) သို့ ဆက်ထုတ်မည်"
  )

if generate_btn or next_volume_btn:
  if not api_key:
    st.error("ကျေးဇူးပြု၍ ဘယ်ဘက်ခြမ်းတွင် Gemini API Key ထည့်ပါ")
  elif not story_input:
    st.error("ကျေးဇူးပြု၍ ဇာတ်လမ်းအကြမ်း အရင်ထည့်ပါ")
  else:
    try:
      genai.configure(api_key=api_key)
      model = genai.GenerativeModel("gemini-3.8-flash")

      if next_volume_btn:
        current_nb["volume"] += 1

      prompt = f"""
      သင်သည် ကျွမ်းကျင်သော ဒရာမာဇာတ်ညွှန်းရေးဆရာနှင့် AI Video Prompt Specialist တစ်ဦး ဖြစ်သည်။ 
      အောက်ပါ ဇာတ်လမ်းအနှစ်ချုပ် (အတွဲ {current_nb['volume']}) ကို အခြေခံ၍ တိကျစွာ **Scene {scene_count} ခန်း** ပါဝင်သော ဇာတ်ညွှန်းနှင့် Prompts များကို **Scene ၅ ခန်း တစ်တွဲစီ (ဥပမာ - Scene 1 မှ 5၊ Scene 6 မှ 10 စသည်ဖြင့်)** သပ်သပ်ရပ်ရပ် အုပ်စုခွဲ၍ ရေးသားပေးပါ။
      
      - **Voiceover / Dialogue (အသံအတွက် စာသား):** မြန်မာဘာသာဖြင့် တိကျစွာ ရေးသားပေးပါ။
      - **Subtitle (စာတန်းထိုးအတွက်):** ရွေးချယ်ထားသော **{sub_language}** ဖြင့် တိကျစွာ ဖော်ပြပေးပါ။

      တစ်ခုချင်းစီအတွက် ဤ Format အတိုင်း တိကျစွာရေးပါ:
      - **Scene [နံပါတ်] (ကြာချိန် - ၁၀ စက္ကန့်)**
      - **Image Prompt:** (AI ပုံဖန်တီးရန် အင်္ဂလိပ်လို Detailed Prompt)
      - **Video Prompt:** (၁၀ စက္ကန့်စာ ဗီဒီယိုလှုပ်ရှားမှုနှင့် ကင်မရာပုံစံ - ອင်္ဂလိပ်လို)
      - **Burmese Voiceover (အသံအတွက် မြန်မာစာသား):** (ဇာတ်ကောင်ပြောမည့် သို့မဟုတ် ဇာတ်ကြောင်းပြော မြန်မာစကား)
      - **Subtitle ({sub_language}):** (ဗီဒီယိုပေါ်တွင် ပြသမည့် စာတန်းထိုးစာသား)

      ဇာတ်လမ်းအနှစ်ချုပ်:
      {story_input}
      """

      action_text = f"ဇာတ်လမ်း (အတွဲ {current_nb['volume']}) - Scene {scene_count} ခန်းကို ဖန်တီးနေပါပြီ..."

      with st.spinner(action_text):
        response = model.generate_content(prompt)
        st.success(
            f"✅ {selected_notebook} - အတွဲ ({current_nb['volume']})"
            f" အောင်မြင်စွာ ထွက်ရှိလာပါပြီ!"
        )

        new_section = (
            f"\n\n=== 🎬 {selected_notebook} - အတွဲ"
            f" ({current_nb['volume']}) [Subtitle: {sub_language}] ===\n"
            + response.text
        )
        current_nb["content"] += new_section

    except Exception as e:
      st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သွားပါသည်: {e}")

# ၅ ခန်းစီ အုပ်စုခွဲ၍ ညာဘက်အပေါ်ထောင့်တွင် Copy ခလုတ်ပါသော st.code များဖြင့် ပြသရန်
if current_nb["content"]:
  st.markdown("---")
  st.subheader(
      f"📜 {selected_notebook} - ၅ ခန်းတွဲ အုပ်စုများ (Copy ကူးရန် ခလုတ်များပါရှိသည်)"
  )

  full_text = current_nb["content"]
  scene_splits = re.split(r"(?i)(?=Scene\s*\d+)", full_text)

  batches = []
  current_batch_scenes = []

  for part in scene_splits:
    if part.strip():
      current_batch_scenes.append(part.strip())
      if len(current_batch_scenes) == 5:
        batches.append("\n\n".join(current_batch_scenes))
        current_batch_scenes = []

  if current_batch_scenes:
    batches.append("\n\n".join(current_batch_scenes))

  if len(batches) <= 1:
    paragraphs = full_text.split("=== 🎬")
    batches = [p.strip() for p in paragraphs if p.strip()]

  for idx, batch_content in enumerate(batches):
    if len(batch_content) > 20:
      batch_title = (
          f"📦 ၅ ခန်းတွဲ အုပ်စု (Batch {idx + 1}) - ညာဘက်ထောင့်တွင် Copy ယူပါ"
      )
      st.markdown(f"#### {batch_title}")
      st.code(batch_content, language="markdown")
      st.markdown("---")
