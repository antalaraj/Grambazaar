import streamlit as st
from PIL import Image
import google.generativeai as genai
import pyperclip
import pyttsx3
from deep_translator import GoogleTranslator

# Initialize session states
if 'copied' not in st.session_state:
    st.session_state.copied = {}
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = None

# Language configuration
LANGUAGES = {
    'English': 'en',
    'हिंदी (Hindi)': 'hi',
    'ગુજરાતી (Gujarati)': 'gu'
}

def text_to_speech(text):
    try:
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate - 20)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        st.error(f"Error in text-to-speech: {str(e)}")

def copy_to_clipboard(text, section):
    try:
        pyperclip.copy(text)
        st.session_state.copied[section] = True
    except Exception as e:
        st.error(f"Failed to copy: {str(e)}")

def translate_text(text, target_lang):
    try:
        if target_lang == 'en':
            return text
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return text

def get_translated_text(key, lang_code):
    translations = {
        'title': {
            'en': "📝 BrandSetu AI",
            'hi': "📝 ब्रांडसेटू एआई",
            'gu': "📝 બ્રાન્ડસેતુ એઆઇ"
        },
        'upload_text': {
            'en': "Upload any product image and get AI-generated insights.",
            'hi': "किसी भी उत्पाद की छवि अपलोड करें और एआई द्वारा उत्पन्न जानकारी प्राप्त करें।",
            'gu': "કોઈપણ ઉત્પાદનની છબી અપલોડ કરો અને એઆઇ-જનિત જાણકારી મેળવો."
        },
        'generate_btn': {
            'en': "Generate Product Details",
            'hi': "उत्पाद विवरण उत्पन्न करें",
            'gu': "ઉત્પાદનની વિગતો જનરેટ કરો"
        },
        'analyzing': {
            'en': "Analyzing product... Please wait...",
            'hi': "उत्पाद का विश्लेषण किया जा रहा है... कृपया प्रतीक्षा करें...",
            'gu': "ઉત્પાદનનું વિશ્લેષણ કરી રહ્યા છીએ... કૃપયા કરી રાહ જુઓ..."
        },
        'copied_msg': {
            'en': "Copied to clipboard!",
            'hi': "क्लिपबोर्ड पर कॉपी किया गया!",
            'gu': "ક્લિપબોર્ડ પર કોપી કર્યું!"
        },
        'upload_prompt': {
            'en': "Please upload an image and click 'Generate Product Details' to begin.",
            'hi': "आरंभ करने के लिए कृपया एक छवि अपलोड करें और 'उत्पाद विवरण उत्पन्न करें' पर क्लिक करें।",
            'gu': "શરૂ કરવા માટે કૃપા કરીને એક છબી અપલોડ કરો અને 'ઉત્પાદન વિગતો જનરેટ કરો' પર ક્લિક કરો."
        }
    }
    return translations.get(key, {}).get(lang_code, key)

# Configure Gemini API
genai.configure(api_key="put-your-api-here")

# Language selector
st.sidebar.title("🌐 Language / भाषा / ભાષા")
selected_language = st.sidebar.selectbox("", list(LANGUAGES.keys()))
st.session_state.language = LANGUAGES[selected_language]

# Main UI
st.title(get_translated_text('title', st.session_state.language))
st.write(get_translated_text('upload_text', st.session_state.language))

uploaded_image = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Image", width=350)

    if st.button(get_translated_text('generate_btn', st.session_state.language)):
        with st.spinner(get_translated_text('analyzing', st.session_state.language)):
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                prompt = """
                You are an expert in product identification, handicrafts, handmade goods,
                fashion, accessories, home décor, local art, and marketplace trends.

                Based on the product image I've uploaded, please provide:

                1. Product Description (10-15 lines)
                   - What the product appears to be
                   - Possible materials and craftsmanship
                   - Potential uses and features
                   - Any distinctive characteristics

                2. Estimated Price (INR)
                   - Price range based on similar products in the market
                   - Factors affecting the price

                3. Place of Origin & Community
                   - Likely region of origin
                   - Artisan community that might create this
                   - Cultural significance if any

                4. Instagram/Facebook Caption + Hashtags
                   - An engaging caption (1-2 sentences)
                   - 10-15 relevant hashtags
                """
                
                response = model.generate_content([prompt, image])
                st.session_state.generated_content = response.text
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please check your API key and try again.")

# Display generated content
if st.session_state.generated_content:
    full_response = st.session_state.generated_content
    
    # Split response into sections
    sections = {}
    current_section = None
    
    for line in full_response.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if "1. Product Description" in line:
            current_section = "Product Description"
            sections[current_section] = ""
            continue
        elif "2. Estimated Price" in line:
            current_section = "Estimated Price"
            sections[current_section] = ""
            continue
        elif "3. Place of Origin" in line:
            current_section = "Place of Origin & Community"
            sections[current_section] = ""
            continue
        elif "4. Instagram/Facebook" in line:
            current_section = "Instagram/Facebook Caption"
            sections[current_section] = ""
            continue
            
        if current_section:
            sections[current_section] += line + "\n"
    
    # Display each section
    for section, content in sections.items():
        if content.strip():
            # Translate content if needed
            if st.session_state.language != 'en':
                content = translate_text(content, st.session_state.language)
            
            # Create columns for section header and buttons
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.subheader(translate_text(section, st.session_state.language))
            with col2:
                button_key = f"copy_{section.replace(' ', '_').lower()}"
                if st.button("📋", key=button_key, help=get_translated_text('copy_btn', st.session_state.language)):
                    copy_to_clipboard(content, section)
            with col3:
                speaker_key = f"speak_{section.replace(' ', '_').lower()}"
                if st.button("🔊", key=speaker_key):
                    text_to_speech(f"{section}. {content}")
            
            if st.session_state.copied.get(section, False):
                st.success(get_translated_text('copied_msg', st.session_state.language))
                st.session_state.copied[section] = False
            
            # Display content
            st.markdown(f"""
            <div class="section-container">
                <div style="margin-top: 10px;">
                    <pre style="white-space: pre-wrap; background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 0;">{content}</pre>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info(get_translated_text('upload_prompt', st.session_state.language))

# Add custom CSS
st.markdown("""
    <style>
    .section-container {
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 15px;
    }
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .success-message {
        color: #4CAF50;
        font-size: 0.9em;
        margin-left: 10px;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)
