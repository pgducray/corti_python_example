#!/usr/bin/env python3
"""
Simple test script for Corti transcription API.
Demonstrates uploading a single audio file and getting the transcript.
"""

from corti_transcript_client import CortiTranscriptClient
from dotenv import load_dotenv
import json
import os

load_dotenv()

print("=" * 70)
print("🎙️  CORTI SINGLE-FILE TRANSCRIPTION TEST")
print("=" * 70)

# Initialize client
client = CortiTranscriptClient()

# Step 1: Authenticate
print("\n1️⃣  Authenticating...")
try:
    token = client.authenticate()
    print(f"   ✅ Authenticated successfully")
except Exception as e:
    print(f"   ❌ Authentication failed: {e}")
    exit(1)

# Step 2: Create interaction
print("\n2️⃣  Creating interaction...")
try:
    interaction = client.create_interaction()
    interaction_id = interaction.get('interactionId') or interaction.get('id')
    print(f"   ✅ Interaction ID: {interaction_id}")
except Exception as e:
    print(f"   ❌ Failed to create interaction: {e}")
    exit(1)

# Step 3: Upload audio file
print("\n3️⃣  Uploading audio file...")
audio_folder_name = 'Sample'
audio_file_name = "Patient Consultation with MI.mp3"
audio_path = os.path.join(os.path.dirname(__file__), audio_folder_name, audio_file_name)

if not os.path.exists(audio_path):
    print(f"   ⚠️  File not found, trying alternative...")
    audio_path = os.path.join(os.path.dirname(__file__), "Sample", "TalkCPR- A real patient and doctor interaction filmed.mp3")

try:
    file_size = os.path.getsize(audio_path) / (1024 * 1024)  # MB
    print(f"   📁 File: {os.path.basename(audio_path)} ({file_size:.1f} MB)")

    with open(audio_path, 'rb') as f:
        upload = client.upload_recording(f, interaction_id)

    recording_id = upload.get('recordingId') or upload.get('id')
    print(f"   ✅ Recording ID: {recording_id}")
except Exception as e:
    print(f"   ❌ Upload failed: {e}")
    try:
        client.delete_interaction(interaction_id)
    except:
        pass
    exit(1)

# Step 4: Create transcript with options
print("\n4️⃣  Creating transcript...")
print("   📋 Options: Diarization enabled, Multi-channel, English")

try:
    transcript_response = client.create_transcript(
        interaction_id=interaction_id,
        recording_id=recording_id,
        primary_language="en",
        is_dictation=False,
        is_multichannel=True,
        diarize=True,
        participants=[{"channel": 1, "role": "doctor"}]
    )

    transcript_id = transcript_response.get('transcriptId') or transcript_response.get('id')
    print(f"   ✅ Transcript ID: {transcript_id}")
except Exception as e:
    print(f"   ❌ Failed to create transcript: {e}")
    if hasattr(e, 'response'):
        try:
            print(f"   Response: {e.response.json()}")
        except:
            print(f"   Response: {e.response.text}")
    # Clean up
    try:
        client.delete_recording(interaction_id, recording_id)
        client.delete_interaction(interaction_id)
    except:
        pass
    exit(1)

# Step 5: Wait for processing
print("\n5️⃣  Waiting for transcription to complete...")
print("   ⏳ This may take a few minutes...")

try:
    transcript = client.wait_for_transcript(
        interaction_id=interaction_id,
        transcript_id=transcript_id,
        max_wait_seconds=300,
        poll_interval=5
    )

except TimeoutError as e:
    print(f"   ⏱️  {e}")
    print("   💡 Transcript is still processing. You can check status later.")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 6 : Save transcript text to file
print("\n6️⃣  Saving transcript to file...")

print(f"   📂 Saving full transcript text of {audio_path} to 'transcripts_text' folder...")
file_name = f"{audio_folder_name}_{audio_file_name}_full_transcript.txt"
client.save_transcription_text(transcript=transcript, file_name=file_name)


# Step 7: Clean up
print("\n7️⃣  Cleaning up resources...")
try:
    client.delete_transcript(interaction_id, transcript_id)
    client.delete_recording(interaction_id, recording_id)
    client.delete_interaction(interaction_id)
    print(f"   ✅ All resources deleted")
except Exception as e:
    print(f"   ⚠️  Cleanup warning: {e}")

print("\n" + "=" * 70)
print("✅ TEST COMPLETED!")
print("=" * 70)
