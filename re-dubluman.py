from demucs import pretrained
import torchaudio
import torch
import streamlit as st
from demucs.apply import apply_model

# Load the Demucs model
model = pretrained.get_model('htdemucs')

# Define the extract_sounds function to extract sources separately
def extract_sounds(audio_path):
    """
    Extract the sources (vocals and other elements) separately from the audio file.

    Parameters:
    - audio_path (str): Path to the audio file.

    Returns:
    - vocals (Tensor): The separated vocal track.
    - other_elements (list of Tensors): The separated other audio elements (instruments, etc.).
    - sample_rate (int): The sample rate of the audio.
    """
    # Load the audio file
    waveform, sample_rate = torchaudio.load(audio_path, normalize=True)

    # Extract the sources and identify vocals
    with torch.no_grad():
        # Use the apply_model function to separate the sources
        sources = apply_model(model, waveform.unsqueeze(0))  # Add batch dimension

    # Separate the vocals and other elements
    vocals = sources[0, -1]  # The last element is considered the vocal source
    other_elements = sources[0, :-1]  # All other elements are considered "other elements"

    return vocals, other_elements, sample_rate

# Define the function to apply gain
def apply_gain(waveform, gain_db):
    """
    Apply gain to the waveform.

    Parameters:
    - waveform (Tensor): The audio waveform.
    - gain_db (float): The gain in dB to apply.

    Returns:
    - Tensor: The waveform after applying the gain.
    """
    # Convert the gain from dB to a linear scale
    gain = torch.pow(10.0, torch.tensor(gain_db, dtype=torch.float32) / 20.0)
    return waveform * gain

# Define the function to combine the sources after applying gain
def combine_sources(vocals, other_elements, sample_rate):
    """
    Combine the vocals and other elements into a single waveform.

    Parameters:
    - vocals (Tensor): The vocal track.
    - other_elements (list of Tensor): The other audio elements (instruments, etc.).
    - sample_rate (int): The sample rate of the audio.

    Returns:
    - Tensor: The combined waveform.
    """
    # Combine all elements
    max_length = max(vocals.size(1), *[elem.size(1) for elem in other_elements])
    vocals = torch.nn.functional.pad(vocals, (0, max_length - vocals.size(1)))

    combined = vocals  # Start with the vocals
    for elem in other_elements:
        elem = torch.nn.functional.pad(elem, (0, max_length - elem.size(1)))  # Pad to match length
        combined += elem  # Add the element to the mix

    return combined.squeeze(0)  # Ensure it's 2D (channels, samples)

# Function to save the combined audio to a file
def save_combined_audio(combined_waveform, sample_rate, output_path):
    """
    Save the combined audio to a file.

    Parameters:
    - combined_waveform (Tensor): The combined audio waveform.
    - sample_rate (int): The sample rate of the audio.
    - output_path (str): The path to save the combined audio.
    """
    # Ensure combined_waveform is 2D (channels, samples)
    if combined_waveform.ndimension() > 2:
        combined_waveform = combined_waveform.squeeze(0)  # Remove any extra batch dimensions if present
    # Save the audio
    torchaudio.save(output_path, combined_waveform, sample_rate)

# Streamlit UI
st.title("Re-Dublüman")

# File uploader for the user to upload an audio file
uploaded_audio = st.file_uploader("Choose an audio file", type=["mp3", "wav"])

if uploaded_audio is not None:
    vocal_gain_db = st.slider("Vocal Gain (dB)", -12, 12, 12)
    other_gain_db = st.slider("Other Elements Gain (dB)", -12, 12, -12)

    # Process the audio and adjust the gain
    with open("temp_audio_file.wav", "wb") as f:
        f.write(uploaded_audio.read())

    # Extract sources using the updated Demucs method
    vocals, other_elements, sample_rate = extract_sounds("temp_audio_file.wav")

    # Apply the gain adjustments
    vocals = apply_gain(vocals, vocal_gain_db)  # Apply vocal gain ONLY to the vocals
    other_elements = [apply_gain(elem, other_gain_db) for elem in other_elements]  # Apply other_gain_db to all non-vocal elements

    # Combine the sources back together
    combined_waveform = combine_sources(vocals, other_elements, sample_rate)

    # Save the combined audio
    output_path = "combined_output.wav"
    save_combined_audio(combined_waveform, sample_rate, output_path)

    # Provide a link to download the output file
    st.audio(output_path)
    st.download_button("Download the combined audio", output_path)
