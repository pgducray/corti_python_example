"""
Corti API Streamlit Interface

This application provides a user-friendly interface for:
- Audio transcription with advanced options
- Medical fact extraction from text
"""

import streamlit as st
import sys
import os
from datetime import datetime
import json
import pandas as pd

# Add parent directory to path to import src package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.corti_transcript_client import CortiTranscriptClient
from src.corti_fact_extraction_client import CortiFactExtractionClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Corti API Interface",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🏥 Corti API Interface</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar - Configuration and Info
with st.sidebar:
    st.header("⚙️ Configuration")

    # Check credentials
    tenant_name = os.getenv("CORTI_TENANT_NAME")
    client_id = os.getenv("CORTI_CLIENT_ID")
    client_secret = os.getenv("CORTI_CLIENT_SECRET")
    environment = os.getenv("CORTI_ENVIRONMENT", "eu")

    if all([tenant_name, client_id, client_secret]):
        st.success("✅ API Credentials Configured")
        st.info(f"**Tenant:** {tenant_name}")
        st.info(f"**Environment:** {environment}")
    else:
        st.error("❌ API Credentials Missing")
        st.warning("Please configure your `.env` file with Corti credentials.")

    st.markdown("---")
    st.header("📊 Data Folders")
    st.info("**Samples:** `data/samples/`")
    st.info("**Transcripts:** `data/transcripts/`")
    st.info("**Facts:** `data/facts/`")

    st.markdown("---")
    st.header("ℹ️ About")
    st.markdown("""
    This interface provides access to:
    - **Transcription**: Convert audio to text
    - **Fact Extraction**: Extract medical facts from text

    Built with Streamlit and Corti API.
    """)

# Main content - Tabs
tab1, tab2, tab3 = st.tabs(["🎙️ Transcription", "🔬 Fact Extraction", "📂 Results Browser"])

# ============================================================================
# TAB 1: TRANSCRIPTION
# ============================================================================
with tab1:
    st.header("🎙️ Audio Transcription")
    st.markdown("Upload an audio file or select from samples to generate a transcript.")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Upload Audio")

        # Audio source selection
        audio_source = st.radio("Select audio source:", ["Upload File", "Use Sample"])

        audio_file = None
        audio_filename = None

        if audio_source == "Upload File":
            uploaded_file = st.file_uploader(
                "Choose an audio file",
                type=['mp3', 'wav', 'ogg', 'flac', 'm4a'],
                help="Supported formats: MP3, WAV, OGG, FLAC, M4A"
            )
            if uploaded_file:
                audio_file = uploaded_file
                audio_filename = uploaded_file.name
        else:
            # List sample files
            sample_dir = "data/samples"
            if os.path.exists(sample_dir):
                sample_files = [f for f in os.listdir(sample_dir) if f.endswith(('.mp3', '.wav', '.ogg', '.flac', '.m4a'))]
                if sample_files:
                    selected_sample = st.selectbox("Select a sample audio file:", sample_files)
                    if selected_sample:
                        sample_path = os.path.join(sample_dir, selected_sample)
                        audio_filename = selected_sample
                        st.info(f"📁 Selected: {selected_sample}")
                else:
                    st.warning("No sample audio files found in data/samples/")
            else:
                st.warning("Sample directory not found. Please create data/samples/")

    with col2:
        st.subheader("Options")

        language = st.selectbox(
            "Language",
            ["en", "es", "fr", "de", "it", "pt", "nl", "sv", "da", "no"],
            help="Primary language of the audio"
        )

        is_multichannel = st.checkbox(
            "Multi-channel",
            value=True,
            help="Enable if audio has multiple channels"
        )

        diarize = st.checkbox(
            "Speaker Diarization",
            value=True,
            help="Identify different speakers"
        )

        is_dictation = st.checkbox(
            "Dictation Mode",
            value=False,
            help="Enable for medical dictation"
        )

        if is_multichannel and diarize:
            st.info("💡 Participants will be assigned to channel 1")

    st.markdown("---")

    # Transcription button
    if st.button("🚀 Start Transcription", type="primary", disabled=not audio_filename):
        if not all([tenant_name, client_id, client_secret]):
            st.error("❌ API credentials not configured. Please set up your .env file.")
        else:
            with st.spinner("Processing transcription... This may take a few minutes."):
                try:
                    # Initialize client
                    client = CortiTranscriptClient()

                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # Step 1: Create interaction
                    status_text.text("1/5 Creating interaction...")
                    progress_bar.progress(20)
                    interaction = client.create_interaction()
                    interaction_id = interaction.get('interactionId') or interaction.get('id')

                    # Step 2: Upload recording
                    status_text.text("2/5 Uploading audio file...")
                    progress_bar.progress(40)

                    if audio_source == "Upload File" and audio_file:
                        upload = client.upload_recording(audio_file, interaction_id)
                    else:
                        # Upload from sample directory
                        with open(os.path.join(sample_dir, audio_filename), 'rb') as f:
                            upload = client.upload_recording(f, interaction_id)

                    recording_id = upload.get('recordingId') or upload.get('id')

                    # Step 3: Create transcript
                    status_text.text("3/5 Creating transcript...")
                    progress_bar.progress(60)

                    participants = [{"channel": 1, "role": "doctor"}] if is_multichannel else None

                    transcript_response = client.create_transcript(
                        interaction_id=interaction_id,
                        recording_id=recording_id,
                        primary_language=language,
                        is_dictation=is_dictation,
                        is_multichannel=is_multichannel,
                        diarize=diarize,
                        participants=participants
                    )

                    transcript_id = transcript_response.get('transcriptId') or transcript_response.get('id')

                    # Step 4: Wait for completion
                    status_text.text("4/5 Waiting for transcription to complete...")
                    progress_bar.progress(80)

                    transcript = client.wait_for_transcript(
                        interaction_id=interaction_id,
                        transcript_id=transcript_id,
                        max_wait_seconds=300,
                        poll_interval=3
                    )

                    # Step 5: Save results
                    status_text.text("5/5 Saving results...")
                    progress_bar.progress(100)

                    # Save to data/transcripts
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_name = os.path.splitext(audio_filename)[0]
                    output_filename = f"{base_name}_{timestamp}.txt"
                    output_path = os.path.join("data/transcripts", output_filename)

                    os.makedirs("data/transcripts", exist_ok=True)

                    # Extract text from transcript
                    transcript_text = ""
                    if 'transcripts' in transcript:
                        for entry in transcript['transcripts']:
                            if 'text' in entry:
                                transcript_text += entry['text'] + "\n"
                    elif 'text' in transcript:
                        transcript_text = transcript['text']

                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(transcript_text)

                    # Cleanup
                    try:
                        client.delete_transcript(interaction_id, transcript_id)
                        client.delete_recording(interaction_id, recording_id)
                        client.delete_interaction(interaction_id)
                    except:
                        pass

                    status_text.empty()
                    progress_bar.empty()

                    # Display results
                    st.success("✅ Transcription completed successfully!")

                    st.subheader("📄 Transcript")
                    st.text_area("Result:", transcript_text, height=300)

                    st.download_button(
                        label="💾 Download Transcript",
                        data=transcript_text,
                        file_name=output_filename,
                        mime="text/plain"
                    )

                    st.info(f"💾 Saved to: {output_path}")

                except Exception as e:
                    st.error(f"❌ Transcription failed: {str(e)}")
                    st.exception(e)

# ============================================================================
# TAB 2: FACT EXTRACTION
# ============================================================================
with tab2:
    st.header("🔬 Medical Fact Extraction")
    st.markdown("Extract structured medical facts from clinical text.")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Input Text")

        # Text source selection
        text_source = st.radio("Select text source:", ["Upload File", "Paste Text", "Use Sample"])

        medical_text = ""
        text_filename = None

        if text_source == "Upload File":
            uploaded_text_file = st.file_uploader(
                "Choose a text file",
                type=['txt', 'md'],
                help="Upload a medical text file"
            )
            if uploaded_text_file:
                medical_text = uploaded_text_file.read().decode('utf-8')
                text_filename = uploaded_text_file.name
                st.text_area("File content preview:", medical_text[:500] + "...", height=150, disabled=True)

        elif text_source == "Paste Text":
            medical_text = st.text_area(
                "Paste medical text here:",
                height=300,
                placeholder="Enter or paste clinical notes, referral letters, consultation notes, etc."
            )
            if medical_text:
                text_filename = "pasted_text"

        else:  # Use Sample
            sample_dir = "data/samples"
            if os.path.exists(sample_dir):
                sample_files = [f for f in os.listdir(sample_dir) if f.endswith(('.txt', '.md'))]
                if sample_files:
                    selected_sample = st.selectbox("Select a sample text file:", sample_files)
                    if selected_sample:
                        sample_path = os.path.join(sample_dir, selected_sample)
                        with open(sample_path, 'r', encoding='utf-8') as f:
                            medical_text = f.read()
                        text_filename = selected_sample
                        st.text_area("Sample content:", medical_text[:500] + "...", height=150, disabled=True)
                else:
                    st.warning("No sample text files found in data/samples/")
            else:
                st.warning("Sample directory not found.")

    with col2:
        st.subheader("Options")

        output_language = st.selectbox(
            "Output Language",
            ["en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "it-IT", "pt-PT"],
            help="Language for extracted facts"
        )

        save_format = st.radio(
            "Save Format",
            ["json", "txt"],
            help="Format for saving results"
        )

        st.info(f"📊 Input length: {len(medical_text)} characters")

    st.markdown("---")

    # Extract button
    if st.button("🚀 Extract Facts", type="primary", disabled=not medical_text):
        if not all([tenant_name, client_id, client_secret]):
            st.error("❌ API credentials not configured. Please set up your .env file.")
        else:
            with st.spinner("Extracting facts... Please wait."):
                try:
                    # Initialize client
                    client = CortiFactExtractionClient()

                    # Extract facts
                    result = client.extract_facts(medical_text, output_language=output_language)

                    # Save results
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_name = os.path.splitext(text_filename)[0] if text_filename else "fact_extraction"
                    output_filename = f"{base_name}_{timestamp}"

                    saved_path = client.save_facts(result, output_filename, save_format)

                    # Display results
                    st.success("✅ Fact extraction completed successfully!")

                    # Credits info
                    if 'usageInfo' in result:
                        credits = result['usageInfo'].get('creditsConsumed', 'N/A')
                        st.metric("💰 Credits Consumed", credits)

                    # Display facts
                    if 'facts' in result and result['facts']:
                        facts = result['facts']
                        st.subheader(f"📋 Extracted Facts ({len(facts)} total)")

                        # Check if facts are structured (dict with group, text, value)
                        if facts and isinstance(facts[0], dict) and 'group' in facts[0]:
                            # Create DataFrame for structured facts
                            df = pd.DataFrame(facts)

                            # Add fact number column
                            df.insert(0, '#', range(1, len(df) + 1))

                            # Select only relevant columns (exclude 'value' as it duplicates 'text')
                            column_order = ['#']
                            if 'group' in df.columns:
                                column_order.append('group')
                            if 'text' in df.columns:
                                column_order.append('text')

                            # Add any remaining columns except 'value'
                            for col in df.columns:
                                if col not in column_order and col != 'value':
                                    column_order.append(col)

                            df = df[column_order]

                            # Rename columns for better display
                            column_names = {
                                'group': 'Category',
                                'text': 'Fact'
                            }
                            df = df.rename(columns=column_names)

                            # Display as interactive table
                            st.dataframe(
                                df,
                                width='stretch',
                                hide_index=True,
                                height=400
                            )

                            # Summary by category
                            if 'Category' in df.columns:
                                st.markdown("---")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Total Facts", len(facts))
                                with col2:
                                    st.metric("Categories", df['Category'].nunique())

                                # Show category breakdown
                                with st.expander("📊 Facts by Category"):
                                    category_counts = df['Category'].value_counts()
                                    for category, count in category_counts.items():
                                        st.write(f"**{category}**: {count} fact(s)")
                        else:
                            # Display unstructured facts in expandable sections
                            for i, fact in enumerate(facts, 1):
                                with st.expander(f"Fact {i}", expanded=(i <= 5)):
                                    st.write(fact)

                        # Download button
                        if save_format == "json":
                            download_data = json.dumps(result, indent=2)
                            mime_type = "application/json"
                        else:
                            download_data = "\n\n".join([f"{i}. {fact}" for i, fact in enumerate(facts, 1)])
                            mime_type = "text/plain"

                        st.download_button(
                            label=f"💾 Download Facts ({save_format.upper()})",
                            data=download_data,
                            file_name=f"{output_filename}.{save_format}",
                            mime=mime_type
                        )

                        st.info(f"💾 Saved to: {saved_path}")
                    else:
                        st.warning("⚠️ No facts were extracted from the text.")

                except Exception as e:
                    st.error(f"❌ Fact extraction failed: {str(e)}")
                    st.exception(e)

# ============================================================================
# TAB 3: RESULTS BROWSER
# ============================================================================
with tab3:
    st.header("📂 Results Browser")
    st.markdown("Browse and download previously generated transcripts and fact extractions.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📝 Transcripts")

        transcript_dir = "data/transcripts"
        if os.path.exists(transcript_dir):
            transcript_files = sorted([f for f in os.listdir(transcript_dir) if f.endswith('.txt')], reverse=True)

            if transcript_files:
                st.info(f"Found {len(transcript_files)} transcript(s)")

                selected_transcript = st.selectbox("Select a transcript:", transcript_files)

                if selected_transcript:
                    transcript_path = os.path.join(transcript_dir, selected_transcript)

                    with open(transcript_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    st.text_area("Content:", content, height=300)

                    st.download_button(
                        label="💾 Download",
                        data=content,
                        file_name=selected_transcript,
                        mime="text/plain"
                    )

                    # File info
                    file_size = os.path.getsize(transcript_path)
                    mod_time = datetime.fromtimestamp(os.path.getmtime(transcript_path))
                    st.caption(f"Size: {file_size} bytes | Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                st.info("No transcripts found. Generate some transcripts first!")
        else:
            st.warning("Transcript directory not found.")

    with col2:
        st.subheader("🔬 Fact Extractions")

        facts_dir = "data/facts"
        if os.path.exists(facts_dir):
            fact_files = sorted([f for f in os.listdir(facts_dir) if f.endswith(('.json', '.txt'))], reverse=True)

            if fact_files:
                st.info(f"Found {len(fact_files)} fact extraction(s)")

                selected_fact = st.selectbox("Select a fact extraction:", fact_files)

                if selected_fact:
                    fact_path = os.path.join(facts_dir, selected_fact)

                    with open(fact_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Display based on format
                    if selected_fact.endswith('.json'):
                        try:
                            json_data = json.loads(content)

                            # Check if it has facts array and display as table
                            if 'facts' in json_data and json_data['facts']:
                                facts = json_data['facts']

                                # Check if facts are structured
                                if isinstance(facts[0], dict) and 'group' in facts[0]:
                                    df = pd.DataFrame(facts)

                                    # Add fact number
                                    df.insert(0, '#', range(1, len(df) + 1))

                                    # Select columns (exclude 'value')
                                    column_order = ['#']
                                    if 'group' in df.columns:
                                        column_order.append('group')
                                    if 'text' in df.columns:
                                        column_order.append('text')

                                    for col in df.columns:
                                        if col not in column_order and col != 'value':
                                            column_order.append(col)

                                    df = df[column_order]

                                    # Rename columns
                                    df = df.rename(columns={'group': 'Category', 'text': 'Fact'})

                                    # Display table
                                    st.dataframe(
                                        df,
                                        width='stretch',
                                        hide_index=True,
                                        height=400
                                    )

                                    # Show metadata if available
                                    if 'usageInfo' in json_data:
                                        st.caption(f"💰 Credits: {json_data['usageInfo'].get('creditsConsumed', 'N/A')}")
                                else:
                                    # Unstructured facts - show numbered list
                                    for i, fact in enumerate(facts, 1):
                                        st.write(f"{i}. {fact}")
                            else:
                                # Fallback to JSON view
                                st.json(json_data)
                        except Exception as e:
                            st.error(f"Error parsing JSON: {e}")
                            st.text_area("Content:", content, height=300)
                    else:
                        st.text_area("Content:", content, height=300)

                    st.download_button(
                        label="💾 Download",
                        data=content,
                        file_name=selected_fact,
                        mime="application/json" if selected_fact.endswith('.json') else "text/plain"
                    )

                    # File info
                    file_size = os.path.getsize(fact_path)
                    mod_time = datetime.fromtimestamp(os.path.getmtime(fact_path))
                    st.caption(f"Size: {file_size} bytes | Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                st.info("No fact extractions found. Extract some facts first!")
        else:
            st.warning("Facts directory not found.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Powered by <strong>Corti API</strong> | Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
