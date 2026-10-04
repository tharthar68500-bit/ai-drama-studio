import google.generativeai as genai
import streamlit as st

# Streamlit Page Setup
st.set_page_config(page_title="AI Drama Studio - Notebook", layout="wide")

st.title("📓 AI Drama Studio - Notebook & Volume Manager (Scene 300 အထိ)")
st.write(
    "Notebook ပုံစံဖြင့် ဇာတ်လမ်းများကို အပိုင်းလိုက် (အတွဲ ၁၊ အတွဲ ၂၊ ...)"
    " စနစ်တကျ သိမ်းဆည်းကာ Scene ၃၀၀ အထိ ကာရိုက်တာမပျက်ဘဲ ဆက်လက်ဖန်တီးပါ။"
)

# Sidebar - API Key နှင့် Notebook စီမံခန့်ခွဲမှု
st.sidebar.header("⚙️ Settings & Notebooks")
api_key = st.sidebar.text_input("Gemini API Key ထည့်ပါ", type="password")

# Notebooks များကို session_state ထဲတွင် သိမ်းဆည်းရန်
if "notebooks" not in st.session_state:
  st.session_state.notebooks = {"ဇာတ်လမ်းအသစ် (Notebook 1)": {"content": "", "volume": 1}}

# Notebook အသစ်ဖန်တီးရန် သို့မဟုတ် ရွေးချယ်ရန်
selected_notebook = st.sidebar.selectbox(
    "📁 သင်၏ Notebook ကို ရွေးပါ", list(st.session_state.notebooks.keys())
)

new_notebook_name = st.sidebar.text_input("➕ Notebook အသစ် ထပ်ထည့်ရန်")
if st.sidebar.button("Notebook အသစ်ဖန်တီးမည်") and new_notebook_name:
  if new_notebook_name not in st.session_state.notebooks:
    st.session_state.notebooks[new_notebook_name] = {"content": "", "volume": 1}
    st.rerun()

# ပင်မ မျက်နှာပြင်
current_nb = st.session_state.notebooks[selected_notebook]

st.subheader(
    f"📖 လက်ရှိ Notebook: {selected_notebook} (အတွဲ {current_nb['volume']})"
)

# ဇာတ်လမ်း အနှစ်ချုပ် သို့မဟုတ် ဆက်လက်ရေးမည့် အကြောင်းအရာ (အတွဲအသစ်အတွက် အကြမ်းထည့်ရန်)
story_input = st.text_area(
    f"✍️ အတွဲ ({current_nb['volume']}) အတွက် ဇာတ်လမ်းအကြမ်း (သို့မဟုတ်)"
    " ဆက်လက်ဖြစ်ပျက်မည့် အကြောင်းအရာများကို ဤနေရာတွင် ရေးပါ...",
    height=150,
)

# Scene အရေအတွက် ရွေးချယ်စရာ (Scene 300 အထိ ရွေးချယ်နိုင်ရန် တိုးမြှင့်ထားသည်)
scene_options = [10, 20, 30, 50, 100, 150, 200, 250, 300]
scene_count = st.selectbox(
    "ဘယ်နှစ် Scene ထုတ်ချင်ပါသလဲ?", scene_options, index=2
)  # မူလအနေဖြင့် 30 ကို ရွေးပေးထားသည်

col1, col2 = st.columns(2)

with col1:
  generate_btn = st.button("🚀 ဇာတ်လမ်းအသစ် စတင်ထုတ်မည်")

with col2:
  next_volume_btn = st.button(
      f"📚 ဇာတ်လမ်းအကြမ်းအသစ်ဖြင့် (အတွဲ {current_nb['volume'] + 1}) သို့ ဆက်ထုတ်မည်"
  )

if generate_btn or next_volume_btn:
  if not api_key:
    st.error("ကျေးဇူးပြု၍ ဘယ်ဘက်ခြမ်းတွင် Gemini API Key ထည့်ပါ")
  elif not story_input:
    st.error("ကျေးဇူးပြု၍ ဇာတ်လမ်းအကြမ်း (သို့) အချက်အလက် အရင်ထည့်ပါ")
  else:
    try:
      genai.configure(api_key=api_key)
      model = genai.GenerativeModel("gemini-3.8-flash")

      if next_volume_btn:
        current_nb["volume"] += 1
        prompt = f"""
                သင်သည် ကျွမ်းကျင်သော ဒရာမာဇာတ်ညွှန်းရေးဆရာတစ်ဦး ဖြစ်သည်။ ဤသည်မှာ '{selected_notebook}' ၏ **အတွဲ ({current_nb['volume']})** ဖြစ်ပါသည်။
                ယခင်အတွဲများမှ ဇာတ်ကောင် Character များ၊ ကာရိုက်တာများနှင့် ဇာတ်အိမ်ပုံစံ လုံးဝမပျက်စေဘဲ၊ ယခုပေးထားသော ဇာတ်လမ်းအကြမ်းအသစ်နှင့် ချိတ်ဆက်ကာ တိကျစွာ **Scene {scene_count} ခန်း** ပါဝင်သော ဇာတ်ညွှန်းကို အပြည့်အစုံ ဆက်လက်ရေးသားပေးပါ။
                
                ယခင်ဇာတ်လမ်း မှတ်တမ်းအကျဉ်း:
                {current_nb['content'][-4000:]} 
                
                ယခု အတွဲ ({current_nb['volume']}) အတွက် အသစ်ဖြည့်စွက်လိုသော ဇာတ်လမ်းအကြမ်းနှင့် အချက်အလက်များ:
                {story_input}
                
                တောင်းဆိုထားသည့်အတိုင်း Scene ၁ မှ {scene_count} ထိ အသေးစိတ် ဇာတ်ကွက်များနှင့် ဇာတ်ကောင်ပြောမယ့် စာသားများကို အစအဆုံး အပြည့်အစုံ ရေးသားပေးပါ။
                """
        action_text = f"အတွဲ ({current_nb['volume']}) အတွက် Scene {scene_count} ခန်းကို ဆက်လက်ရေးသားနေပါပြီ..."
      else:
        prompt = f"""
                သင်သည် ကျွမ်းကျင်သော ဇာတ်ညွှန်းရေးဆရာတစ်ဦး ဖြစ်သည်။ အောက်ပါ ဇာတ်လမ်းအနှစ်ချုပ်ကို အခြေခံ၍ ကာရိုက်တာစုံလင်စွာဖြင့် အသေးစိတ် ဖန်တီးပေးပါ။
                ထွက်ရှိလာမည့် Scene စုစုပေါင်း အရေအတွက်မှာ တိကျစွာ **{scene_count} ခန်း** ရှိရမည်။
                
                1. **Story Structure & Characters (ဇာတ်လမ်းဖွဲ့စည်းပုံနှင့် ဇာတ်ကောင်များ)**
                2. **Detailed Scenes (Scene ၁ မှ {scene_count} ထိ အသေးစိတ် ဇာတ်ကွက်များ၊ ဇာတ်ကောင်ပြောမယ့် စာသားများ)**
                
                ဇာတ်လမ်းအနှစ်ချုပ်:
                {story_input}
                """
        action_text = f"ဇာတ်လမ်း Scene {scene_count} ခန်းကို ဖန်တီးနေပါပြီ..."
        current_nb["content"] = ""  # အသစ်စလျှင် အဟောင်းရှင်းမည်

      with st.spinner(action_text):
        response = model.generate_content(prompt)
        st.success(
            f"✅ {selected_notebook} - အတွဲ ({current_nb['volume']})"
            f" (Scene {scene_count} ခန်း) အောင်မြင်စွာ ထွက်ရှိလာပါပြီ!"
        )

        # ဇာတ်လမ်းအသစ်ကို Notebook ထဲသို့ သိမ်းဆည်းခြင်း
        new_section = (
            f"\n\n=== 🎬 {selected_notebook} - အတွဲ"
            f" ({current_nb['volume']}) [Scene စုစုပေါင်း: {scene_count}] ===\n"
            + response.text
        )
        current_nb["content"] += new_section

    except Exception as e:
      st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သွားပါသည်: {e}")

# ယခင်ထုတ်ထားသော ဇာတ်လမ်းများကို Notebook ထဲတွင် အမြဲတမ်း ပြန်လည်ကြည့်ရှုနိုင်ရန်
if current_nb["content"]:
  st.markdown("---")
  st.subheader(f"📜 {selected_notebook} - ဇာတ်လမ်းမှတ်တမ်း အပြည့်အစုံ")
  st.markdown(current_nb["content"])
