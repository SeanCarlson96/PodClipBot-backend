import whisperx

device = "cpu"
compute_type = "int8" #try changing to float16 after development
model = whisperx.load_model("medium", device, compute_type=compute_type, language='en', download_root="/tmp/whisperx")
