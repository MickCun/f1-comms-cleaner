from pydub import AudioSegment
import soundfile as sf
import webrtcvad
import noisereduce as nr
from scipy.signal import butter, lfilter
import sounddevice as sd
import whisper
import os
import numpy as np

comms_log = []
segments_of_speech = []
saved_audio_segments = []

# Load the audio file and normalize the audio. 
def load_audio():
    audio = AudioSegment.from_wav("Audio/F1_Audio.wav");
    audio = audio.set_channels(1).set_frame_rate(16000);
    normalized_audio = audio.apply_gain(-audio.max_dBFS);
    normalized_audio.export("Audio/F1_AUDIO_CLEANED.wav", format="wav");

# Load the cleaned audio, and denoise it using noise reduce. 
def prepare_audio():
    print("Preparing Audio File...")
    audio, samplerate = sf.read("Audio/F1_AUDIO_CLEANED.wav");

    vad = webrtcvad.Vad(3);
    chunk_size = 0.03; 
    samples = int(chunk_size * samplerate)

    noise_sample = audio[:samplerate * 40]
    denoised = nr.reduce_noise(y=audio, y_noise=noise_sample, sr=samplerate)
    denoised = nr.reduce_noise(y=denoised, y_noise=noise_sample, sr=samplerate)

    return denoised, samplerate, vad, chunk_size, samples

denoised, samplerate, vad, chunk_size, samples = prepare_audio()

# Bandpass Filtering
def bandpass_filter(lower, higher, filter_order, sample_rate):
    nyquist = sample_rate / 2
    lower_bound = lower / nyquist
    upper_bound = higher / nyquist

    return butter(filter_order, [lower_bound, upper_bound], btype='band')

# Extremely High bandpass isolates just the speech frequencies.
def run_bandpass_filter(signal, sample_rate, lower=2500, higher=3400, filter_order=6):
    numerator, denominator = bandpass_filter(lower, higher, filter_order, sample_rate);
    return lfilter(numerator, denominator, signal)

bandpass_screened_audio = run_bandpass_filter(denoised, samplerate)

def live_process_audio(display_callback=None):
    cooldown_counter = 0
    cooldown_limit = int(2 / chunk_size)  
    in_speech = False
    segment_start = 0

    samples_per_chunk = int(samplerate * chunk_size)

    # Large model has the best transcription accuracy.
    model = whisper.load_model("medium.en")

    print("Sampling Commenced...")

    for i in range(0, len(bandpass_screened_audio), samples):
        chunk = bandpass_screened_audio[i:i + samples]
        chunk_bytes = (chunk * 32767).astype('int16').tobytes()
        timestamp = i / samplerate

        if len(chunk) != samples_per_chunk:
            continue

        if vad.is_speech(chunk_bytes, samplerate):
            if not in_speech:
                segment_start = timestamp
                in_speech = True
            cooldown_counter = 0

        else:
            if in_speech:
                cooldown_counter += 1
                # Cooldown to prevent multiple triggers
                if cooldown_counter >= cooldown_limit:
                    segment_end = timestamp
                    in_speech = False
                    cooldown_counter = 0

                    # Buffer to capture speech before and after
                    buffer_before = 1
                    buffer_after = 2
                    
                    sample_start = int(max((segment_start - buffer_before), 0) * samplerate)
                    end_sample = int(min((segment_end + buffer_after), len(denoised) / samplerate) * samplerate)

                    # Fetch the segment of audio from the cleaner audio.
                    segment_audio = denoised[sample_start:end_sample]
                    
                    comms_live_transcript = "whisper-transcription/comms_live_transcript.wav"
                    sf.write(comms_live_transcript, segment_audio, samplerate)

                    # Whisper Transcription
                    result = model.transcribe(comms_live_transcript, initial_prompt="Formula 1, Verstappen, Perez, Bottas, Ocon, Hulkenberg, Kimi, Wehrlein, wets, pit wall, inters, slicks, delta")
                    comms_log.append((segment_start, result['text'].strip()))

                    print(result['text'].strip())

                    sd.play(segment_audio, samplerate)
                    sd.wait()

                    if display_callback:
                        display_callback(f"[{segment_start:.2f}s] {result['text'].strip()}\n")

                    # For Wav file at the end.
                    segments_of_speech.append((segment_start, segment_end))
                    
                    os.remove(comms_live_transcript)

        # Time Sleep enables the race audio to appear live. 
        # time.sleep(chunk_size)

    if in_speech:
        segments_of_speech.append((segment_start, len(filtered_audio) / samplerate))

    print("|SUCCESS| Completed Transcription")

# Produce a full transcript of the audio to the current time recording. 
def produce_comms_log():
    # Produce Comms Log
    with open("Transcripts/comms_transcript.txt", "w") as f:
        for timestamp, text in comms_log:
            f.write(f"[{timestamp:.2f}s] {text}\n")

# Produce a clipped file containing all of the race comms audio.
def produce_combined_clean_wav_file():
    global saved_audio_segments
    saved_audio_segments = []
    
    for start, end in segments_of_speech:
        sample_start = int(max((start - 1), 0) * samplerate)
        sample_end = int(min((end + 2), len(denoised) / samplerate) * samplerate)
        segment = denoised[sample_start:sample_end]
        saved_audio_segments.append(segment * 4)

    if saved_audio_segments:
        combined_audio = np.concatenate(saved_audio_segments)
        sf.write("Recorded-Audio/clippedAndCleaned.wav", combined_audio, samplerate)
        print("[SUCCESS] --> Full Comms audio has been generated. ")
    else:
        print("|FAILURE| --> Failed to output comms audio.")