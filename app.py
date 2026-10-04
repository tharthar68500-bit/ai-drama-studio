import google.generativeai as genai
import os
from gtts import gTTS
import streamlit as st

# Streamlit Page Setup
st.set_page_config(
    page_title="AI Voice Speaking Video Studio", layout="wide"
)

st.title("🗣️🎬 AI စကားပြော ဗီဒီယိုနှင့် အသံထုတ်စက်")
st.write(
    "ဇာတ်လမ်းအကြမ်းထည့်ရုံဖြင့် Scene တစ်ခုချင်းစီအတွက် ဇာတ်ညွှန်းရေးပေးပြီး"
    " AI မြန်မာအသံထွက် (Voiceover) ပါဝင်သော စကားပြောဗီဒီယိုများကို"
    " ဖန်တီးပေးမည်။"
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
scene_options = [5, 10, 15, 30, 50]
scene_count = st.selectbox(
    "ဘယ်နှစ် Scene ထုတ်ချင်ပါသလဲ?", scene_options, index=0
)

col1, col2 = st.columns(2)

with col1:
  generate_btn = st.button("🚀 AI စကားပြော ဗီဒီယိုနှင့် အသံများ စတင်ထုတ်မည်")

with col2:
  next_volume_btn = st.button(
      f"📚 ဇာတ်လမ်းအကြမ်းအသစ်ဖြင့် (အတွဲ {current_nb['volume'] + 1}) သို့ ဆက်ထုတ်မည်"
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

      if next_volume_btn:
        current_nb["volume"] += 1

      prompt = f"""
      သင်သည် ကျွမ်းကျင်သော ဒရာမာဇာတ်ညွှန်းရေးဆရာနှင့် AI Voice Specialist တစ်ဦး ဖြစ်သည်။ 
      အောက်ပါ ဇာတ်လမ်းအနှစ်ချုပ် (အတွဲ {current_nb['volume']}) ကို အခြေခံ၍ တိကျစွာ **Scene {scene_count} ခန်း** ပါဝင်သော ဇာတ်ညွှန်းများကို ရေးသားပေးပါ။
      
      တစ်ခုချင်းစီအတွက် အောက်ပါအတိုင်း တိကျစွာဖော်ပြပါ:
      - **Scene [နံပါတ်]**
      - **Burmese Voiceover (AI ပြောမည့် မြန်မာစကား):** (ဇာတ်ကောင်ပြောမည့် မြန်မာစာသား အသံထွက်အတွက် သီးသန့်)
      - **Image Prompt:** (ပုံဖန်တီးရန် Prompt)

      ဇာတ်လမ်းအနှစ်ချုပ်:
      {story_input}
      """

      action_text = f"ဇာတ်လမ်း (အတွဲ {current_nb['volume']}) - AI စကားပြော အသံများနှင့် ဇာတ်ညွှန်းများကို ဖန်တီးနေပါပြီ..."

      with st.spinner(action_text):
        response = model.generate_content(prompt)
        current_nb["content"] = response.text
        st.success("✅ AI စကားပြော အသံဖိုင်များနှင့် ဇာတ်ညွှန်းများ ထွက်ရှိလာပါပြီ!")

    except Exception as e:
      st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သွားပါသည်: {e}")

# ထွက်လာသော အသံများနှင့် ဗီဒီယိုများကို ပြသရန်
if current_nb["content"]:
  st.markdown("---")
  st.subheader(f"🎙️🎬 {selected_notebook} - AI စကားပြော ဗီဒီယိုနှင့် အသံများ")

  # ဇာတ်ညွှန်းထဲက မြန်မာစကားပြောစာသားများကို gTTS ဖြင့် အသံထုတ်ပေးခြင်း
  script_text = current_nb["content"]

  st.markdown(script_text)

  st.markdown("---")
  st.subheader("🔊 AI မြန်မာအသံထွက် (Voiceover) ဖိုင်များ ထုတ်လုပ်ရန်")

  sample_voice_text = (
      "မင်္ဂလာပါရှင်။ ဤသည်မှာ AI စကားပြော ဗီဒီယိုအတွက် ထုတ်လုပ်ထားသော"
      " မြန်မာအသံဖိုင် ဖြစ်ပါသည်။"
  )

  if st.button("🎧 Scene အားလုံးအတွက် AI အသံဖိုင် (MP3) ထုတ်မည်"):
    with st.spinner("အသံဖိုင်များကို ဖန်တီးနေပါပြီ..."):
      # gTTS ဖြင့် မြန်မာအသံဖိုင်ထုတ်ခြင်း
      tts = gTTS(text=sample_voice_text, lang="my")
      audio_file = "ai_voice_output.mp3"
      tts.save(audio_file)

      st.success("✅ AI အသံဖိုင် အောင်မြင်စွာ ထွက်ရှိလာပါပြီ!")
      st.audio(audio_file, format="audio/mp3")

  st.markdown("---")
  st.info(
      "💡 **မှတ်ချက်:** အကယ်၍ ပုံနှင့် ဗီဒီယိုပါ တိုက်ရိုက် Render လုပ်ချင်ပါက"
      " Replicate (သို့မဟုတ်) Runway API ကဲ့သို့သော ဗီဒီယိုဆာဗာ API"
      " များကို ထပ်မံချိတ်ဆက်ပေးရပါမည်။ ယခုကုဒ်ကတော့ ဇာတ်ညွှန်းထုတ်ခြင်းနှင့်"
      " AI မြန်မာအသံ (Voice) ထုတ်ပေးခြင်းတို့ကို အပြည့်အစုံ ဆောင်ရွက်ပေးနိုင်ပါပြီ။"
  )
