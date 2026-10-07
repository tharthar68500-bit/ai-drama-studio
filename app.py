import os
import json
import time
import re
import streamlit as st
from gtts import gTTS
from google import genai
from google.genai import types

# =========================================================
# PAGE
# =========================================================
st.set_page_config(
    page_title="AI Drama Studio",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 AI Drama / Story Studio")
st.caption(
    "Story → Character → Episode → Scene → Dialogue → Voice → Video"
)

# =========================================================
# DATA
# =========================================================
DATA_FILE = "drama_data.json"
OUTPUT_DIR = "generated_media"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return {
        "notebooks": {
            "ဇာတ်လမ်းအသစ် (Notebook 1)": {
                "volume": 1,
                "characters": [],
                "episodes": {}
            }
        }
    }

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.data, f, ensure_ascii=False, indent=2)

if "data" not in st.session_state:
    st.session_state.data = load_data()

# =========================================================
# HELPERS
# =========================================================
def get_client(api_key):
    return genai.Client(api_key=api_key)

def safe_filename(text):
    text = re.sub(r"[^\w\u1000-\u109F\u4e00-\u9fff -]", "", text)
    text = text.strip().replace(" ", "_")
    return text[:60] or "scene"

def extract_json(text):
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

    start = text.find("{")
    end = text.rfind("}")

    if start >= 0 and end >= 0:
        return json.loads(text[start:end + 1])

    start = text.find("[")
    end = text.rfind("]")

    if start >= 0 and end >= 0:
        return json.loads(text[start:end + 1])

    raise ValueError("AI response ထဲမှာ JSON မတွေ့ပါ")

def generate_story(api_key, model_name, story, scene_count, language):
    client = get_client(api_key)

    existing_characters = st.session_state.current_nb.get("characters", [])

    character_text = json.dumps(
        existing_characters,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
You are an expert drama screenwriter and story continuity manager.

Create a drama episode from the user's story idea.

OUTPUT LANGUAGE:
{language}

NUMBER OF SCENES:
{scene_count}

EXISTING CHARACTER DATABASE:
{character_text}

IMPORTANT:
- Keep existing character names, personalities, ages and relationships consistent.
- If a new character appears, add them.
- Each scene must connect naturally to the previous scene.
- Dialogue must be suitable for voice generation.
- Image prompt must describe the exact characters appearing in the scene.
- Video prompt must describe camera movement, action, emotion and continuity.
- Return ONLY valid JSON.

JSON FORMAT:
{{
  "characters": [
    {{
      "name": "",
      "age": "",
      "gender": "",
      "personality": "",
      "appearance": "",
      "clothing": "",
      "relationship": ""
    }}
  ],
  "scenes": [
    {{
      "scene": 1,
      "location": "",
      "time": "",
      "characters": [],
      "action": "",
      "dialogue": [
        {{
          "character": "",
          "text": ""
        }}
      ],
      "voice_text": "",
      "image_prompt": "",
      "video_prompt": ""
    }}
  ]
}}

USER STORY:
{story}
"""

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    return extract_json(response.text)

def generate_voice(text, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    tts = gTTS(text=text, lang="my")
    tts.save(path)
    return path

def generate_video(api_key, video_model, prompt, filename, aspect_ratio):
    client = get_client(api_key)

    operation = client.models.generate_videos(
        model=video_model,
        prompt=prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio=aspect_ratio,
            resolution="720p",
            number_of_videos=1,
        ),
    )

    progress = st.empty()

    while not operation.done:
        progress.info("🎬 Video generation လုပ်နေပါသည်... စောင့်ပေးပါ...")
        time.sleep(10)
        operation = client.operations.get(operation)

    progress.empty()

    generated_video = operation.response.generated_videos[0]
    path = os.path.join(OUTPUT_DIR, filename)

    client.files.download(
        file=generated_video.video,
        destination=path,
    )

    return path

# =========================================================
# SIDEBAR - API SETTINGS
# =========================================================
st.sidebar.header("🔑 API Settings")

provider = st.sidebar.selectbox(
    "AI Provider",
    [
        "Google Gemini",
        "Custom / OpenAI-Compatible API",
    ],
)

api_key = st.sidebar.text_input(
    "API Key ထည့်ပါ",
    type="password",
    help="သင့်ကိုယ်ပိုင် API Key ကိုထည့်ပါ။ Code ထဲမရေးထားပါ။"
)

if provider == "Google Gemini":
    model_name = st.sidebar.selectbox(
        "🧠 Story Model",
        [
            "gemini-3.8-flash",
            "gemini-3.8-pro",
        ],
    )

    video_model = st.sidebar.selectbox(
        "🎬 Video Model",
        [
            "veo-3.1-generate-preview",
        ],
    )

    aspect_ratio_label = st.sidebar.selectbox(
        "📐 Video Aspect Ratio",
        [
            "16:9 — Landscape (YouTube / TV)",
            "9:16 — Portrait (TikTok / Reels / Shorts)",
        ],
        index=0,
    )
    aspect_ratio = (
        "16:9"
        if aspect_ratio_label.startswith("16:9")
        else "9:16"
    )
else:
    custom_base_url = st.sidebar.text_input(
        "Custom API Base URL",
        placeholder="https://your-api.example.com/v1",
    )

    model_name = st.sidebar.text_input(
        "Custom Model Name",
        value="your-model-name",
    )

    video_model = None

st.sidebar.info(
    "💡 API Key ကို code ထဲမထည့်ထားဘဲ ဒီနေရာကနေ ထည့်သုံးနိုင်ပါတယ်။"
)

# =========================================================
# NOTEBOOK
# =========================================================
st.sidebar.markdown("---")
st.sidebar.header("📁 Notebooks")

notebook_names = list(st.session_state.data["notebooks"].keys())

selected_notebook = st.sidebar.selectbox(
    "Notebook ရွေးပါ",
    notebook_names
)

new_notebook = st.sidebar.text_input(
    "➕ Notebook အသစ်"
)

if st.sidebar.button("Notebook ဖန်တီးမည်"):
    if new_notebook and new_notebook not in st.session_state.data["notebooks"]:
        st.session_state.data["notebooks"][new_notebook] = {
            "volume": 1,
            "characters": [],
            "episodes": {}
        }
        save_data()
        st.rerun()

st.session_state.current_nb = st.session_state.data["notebooks"][selected_notebook]
current_nb = st.session_state.current_nb

# =========================================================
# MAIN
# =========================================================
st.subheader(
    f"📖 {selected_notebook} — အတွဲ {current_nb['volume']}"
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "✍️ Story",
        "👥 Characters",
        "🎬 Scenes",
        "🎙️ Voice / Video",
    ]
)

# =========================================================
# STORY TAB
# =========================================================
with tab1:
    story_input = st.text_area(
        "✍️ ဇာတ်လမ်းအကြမ်း",
        height=220,
        placeholder=(
            "ဥပမာ - ချမ်းသာတဲ့ မိန်းကလေးတစ်ယောက်က ဆင်းရဲတဲ့ "
            "ယောကျ်ားလေးကို အစပိုင်းမှာ အထင်သေးပေမယ့်..."
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        scene_count = st.selectbox(
            "Scene အရေအတွက်",
            [5, 10, 15, 30, 50],
            index=1,
        )

    with col2:
        output_language = st.selectbox(
            "Dialogue Language",
            [
                "မြန်မာ",
                "English",
                "中文",
                "ไทย",
            ],
        )

    if st.button(
        "🚀 AI ဇာတ်လမ်း + Scene + Dialogue ထုတ်မည်",
        type="primary",
        use_container_width=True,
    ):
        if provider != "Google Gemini":
            st.warning(
                "ဒီ version ရဲ့ Story Generator ကို Google Gemini နဲ့ အရင်စမ်းပါ။ "
                "Custom/OpenAI-compatible provider ကို နောက်ထပ် adapter ထည့်နိုင်ပါတယ်။"
            )
        elif not api_key:
            st.error("Gemini API Key ထည့်ပါ။")
        elif not story_input.strip():
            st.error("ဇာတ်လမ်းအကြမ်းထည့်ပါ။")
        else:
            try:
                with st.spinner("🤖 ဇာတ်လမ်းကို တည်ဆောက်နေပါသည်..."):
                    result = generate_story(
                        api_key,
                        model_name,
                        story_input,
                        scene_count,
                        output_language,
                    )

                for character in result.get("characters", []):
                    old = next(
                        (
                            c for c in current_nb["characters"]
                            if c.get("name") == character.get("name")
                        ),
                        None,
                    )

                    if old:
                        old.update(character)
                    else:
                        current_nb["characters"].append(character)

                episode_number = current_nb["volume"]

                current_nb["episodes"][str(episode_number)] = {
                    "story_input": story_input,
                    "scenes": result.get("scenes", []),
                }

                save_data()

                st.session_state.last_result = result

                st.success(
                    f"✅ အတွဲ {episode_number} အတွက် "
                    f"{len(result.get('scenes', []))} Scenes ထုတ်ပြီးပါပြီ။"
                )

            except Exception as e:
                st.error(f"❌ AI Error: {e}")

    # Episode next
    if st.button("📚 အတွဲအသစ်သို့ ဆက်မည်"):
        current_nb["volume"] += 1
        save_data()
        st.success(
            f"အတွဲ {current_nb['volume']} သို့ ပြောင်းပြီးပါပြီ။"
        )
        st.rerun()

# =========================================================
# CHARACTER TAB
# =========================================================
with tab2:
    st.subheader("👥 Character Database")

    if not current_nb["characters"]:
        st.info("Character မရှိသေးပါ။ Story Generate လုပ်ပါ။")
    else:
        for i, character in enumerate(current_nb["characters"]):
            with st.expander(
                f"👤 {character.get('name', 'Unknown')}"
            ):
                st.write(f"**အသက်:** {character.get('age', '')}")
                st.write(f"**Gender:** {character.get('gender', '')}")
                st.write(f"**Personality:** {character.get('personality', '')}")
                st.write(f"**Appearance:** {character.get('appearance', '')}")
                st.write(f"**Clothing:** {character.get('clothing', '')}")
                st.write(f"**Relationship:** {character.get('relationship', '')}")

# =========================================================
# SCENE TAB
# =========================================================
with tab3:
    episode_key = str(current_nb["volume"])
    episode = current_nb["episodes"].get(episode_key)

    if not episode:
        st.info("အရင်ဆုံး Story Generate လုပ်ပါ။")
    else:
        st.subheader(
            f"🎬 Episode {episode_key} — {len(episode['scenes'])} Scenes"
        )

        for scene in episode["scenes"]:
            scene_no = scene.get("scene", "?")

            with st.expander(
                f"🎬 Scene {scene_no}",
                expanded=False,
            ):
                st.write("📍 **Location:**", scene.get("location", ""))
                st.write("🕐 **Time:**", scene.get("time", ""))
                st.write("🎭 **Action:**", scene.get("action", ""))

                st.markdown("### 💬 Dialogue")

                for d in scene.get("dialogue", []):
                    st.markdown(
                        f"**{d.get('character', '')}:** "
                        f"{d.get('text', '')}"
                    )

                st.markdown("### 🖼️ Image Prompt")
                st.code(
                    scene.get("image_prompt", ""),
                    language="text",
                )

                st.markdown("### 🎥 Video Prompt")
                st.code(
                    scene.get("video_prompt", ""),
                    language="text",
                )

                st.markdown("### 🎙️ Voice Text")
                st.code(
                    scene.get("voice_text", ""),
                    language="text",
                )

# =========================================================
# VOICE / VIDEO TAB
# =========================================================
with tab4:
    episode_key = str(current_nb["volume"])
    episode = current_nb["episodes"].get(episode_key)

    if not episode:
        st.info("အရင်ဆုံး Scene တွေ Generate လုပ်ပါ။")
    else:
        st.subheader("🎙️ Voice / 🎬 Video")

        scene_numbers = [
            s.get("scene")
            for s in episode["scenes"]
        ]

        selected_scene = st.selectbox(
            "Scene ရွေးပါ",
            scene_numbers,
        )

        scene = next(
            s for s in episode["scenes"]
            if s.get("scene") == selected_scene
        )

        st.markdown("### 🎙️ Voice Text")
        voice_text = scene.get("voice_text", "")

        edited_voice = st.text_area(
            "အသံထွက်မယ့်စာသား",
            value=voice_text,
            height=150,
        )

        if st.button(
            "🔊 ဒီ Scene အတွက် MP3 ထုတ်မည်",
            use_container_width=True,
        ):
            if not edited_voice.strip():
                st.error("Voice Text မရှိပါ။")
            else:
                try:
                    filename = (
                        f"episode_{current_nb['volume']}"
                        f"_scene_{selected_scene}_voice.mp3"
                    )

                    with st.spinner("🎙️ Voice ဖန်တီးနေပါသည်..."):
                        audio_path = generate_voice(
                            edited_voice,
                            filename,
                        )

                    st.success("✅ MP3 ထွက်ပါပြီ။")
                    st.audio(audio_path, format="audio/mp3")

                except Exception as e:
                    st.error(f"❌ Voice Error: {e}")

        st.markdown("---")
        st.markdown("### 🎬 Gemini Veo Video")

        video_prompt = st.text_area(
            "Video Prompt",
            value=scene.get("video_prompt", ""),
            height=180,
        )

        st.caption(
            "Veo သည် long-running generation ဖြစ်နိုင်သောကြောင့် "
            "video ထုတ်နေစဉ် စောင့်ရပါမည်။"
        )

        if st.button(
            "🎬 Gemini Veo နဲ့ Video ထုတ်မည်",
            type="primary",
            use_container_width=True,
        ):
            if provider != "Google Gemini":
                st.error("Gemini Video အတွက် Google Gemini Provider ကို ရွေးပါ။")
            elif not api_key:
                st.error("Gemini API Key ထည့်ပါ။")
            elif not video_prompt.strip():
                st.error("Video Prompt မရှိပါ။")
            else:
                try:
                    filename = (
                        f"episode_{current_nb['volume']}"
                        f"_scene_{selected_scene}.mp4"
                    )

                    video_path = generate_video(
                        api_key,
                        video_model,
                        video_prompt,
                        filename,
                        aspect_ratio,
                    )

                    st.success(f"✅ {aspect_ratio} Video အောင်မြင်စွာ ထွက်ပါပြီ။")
                    st.video(video_path)

                except Exception as e:
                    st.error(
                        "❌ Video Error ဖြစ်ပါသည်။ "
                        "API key, model access, quota/billing "
                        "နှင့် Gemini Video availability ကို စစ်ပါ။\n\n"
                        f"{e}"
                    )

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.info(
    "💡 အခု version မှာ Story → Character → Scene → Dialogue → "
    "Voice → Gemini Veo Video ကို တစ်နေရာတည်းထားပေးထားပါတယ်။ "
    "Video generation သည် API quota/billing နှင့် model availability "
    "ပေါ်မူတည်နိုင်ပါတယ်။"
)
