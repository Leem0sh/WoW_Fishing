import pyaudio 


p = pyaudio.PyAudio()

for i in range(p.get_device_count()):
    if p.get_device_info_by_index(i)["name"] == "CABLE Output (VB-Audio Virtual ":
        print(type(p.get_device_info_by_index(i)["index"]))
    
p.terminate()
input("click")

