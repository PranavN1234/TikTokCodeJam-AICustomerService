from taskrouting_layer import route_task
from utils import record_audio, transcribe_audio, synthesize_audio, play_audio
from tasks.map_to_task import map_to_route
from ai_service import ai_response

def main():
    
    while True:

        print("Recording Audio....")
        record_audio('test.wav')
        print("audio recorded")
        transcribed_text = transcribe_audio('test.wav')
        print(transcribed_text)
        

        ai_answer = ai_response(transcribed_text)
        synthesize_audio(ai_answer)
        play_audio('output.mp3')
    

if __name__ == "__main__":
    main()
