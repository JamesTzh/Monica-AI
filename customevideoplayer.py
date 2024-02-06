from kivy.app import App
from kivy.uix.video import Video
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from openai import OpenAI
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import textwrap


def AI(user_input):
    video_apikey = 'MzZkYTE0MGUwNmIwNGEwMGE5ZWUxOTlhMmY1ODIwNmQtMTcwNzE4MTMwOA=='
    client = OpenAI(
        api_key= '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'
    )

    user_input = user_input
    #input("prompt (-1 to quit)")

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content" : "You are a scriptwriter for a reporter that can only write up to 20 words",
            },
            {
                "role" : "user",
                "content" : user_input,
            }
        ],
        model = 'gpt-3.5-turbo',
    )
    gpt_reply = chat_completion.choices[0].message.content
    print(gpt_reply)

    payload = {
        "background": "https://img.freepik.com/free-vector/realistic-news-studio-background_23-2149985612.jpg",
        "ratio": "16:9",
        "test": False,
        "caption_open": False,
        "version": "v1alpha",
        "clips": [
            {
                "avatar_id": "Monica_inshirt_20220819",
                "avatar_style": "normal",
                "input_text": gpt_reply,
                "scale": 1,
                "voice_id": "131a436c47064f708210df6628ef8f32",
                "talking_photo_style": "normal"
            }
        ]
    }
    headers_make = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": video_apikey,
    }

    url = 'https://api.heygen.com/v1/video.generate'
    response_make = requests.post(url, json=payload, headers=headers_make)
    print(response_make.text)
    data_make = response_make.json()
    print(str(data_make['data']['video_id']))

    if(str(data_make['message']) == 'Success'):

        vid_get_url = 'https://api.heygen.com/v1/video_status.get?video_id=' + str(data_make['data']['video_id'])

        headers_retriv = {
            "accept": "application/json",
            "x-api-key": video_apikey,
        }

        status = ''
        count = 0
        generation = True

        while(status != 'completed'):
            response_ret = requests.get(vid_get_url, headers = headers_retriv)
            data_ret = response_ret.json()

            print(response_ret.text)
            status = str(data_ret['data']['status'])
            vid_url = str(data_ret['data']['video_url'])
            print('url = ' + vid_url)
            print('Status = ' + status)
            
            if (status != 'completed'):
                print("Timer = " + str(count*3))
                if count > 100:
                    print("Failed")
                    generation = False
                    break
                time.sleep(5)
            elif(status == 'failed'):
                generation = False
                print('Failed')
                break

            count += 1

        if(generation):
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(vid_url)
            time.sleep(3)
            driver.quit
            return([str(data_make['data']['video_id']),gpt_reply])
    else:
        return None
    
    return None

Builder.load_file('whatever.kv')

class MyGridLayout(Widget):
    def press(self):
        name = self.ids.name_input.text

        #Update Label
        self.ids.script1.text = self.ids.script2.text
        self.ids.script2.text = self.ids.script3.text
        self.ids.script3.text = self.ids.script4.text
        self.ids.script4.text = self.ids.script5.text
        self.ids.script5.text = name

        self.ids.name_input.text = ""

        #valid_vid = ["6dbc5a63bfba42f2bec552cc73dc4581",'Singapore: Vibrant city-state in Southeast Asia. Boasts modern skyline, diverse culture, efficient transport, and strict governance.']
        valid_vid = AI(name)
        if(valid_vid != None):
            self.ids.video.source = 'C:/Users/James/Downloads/'+ valid_vid[0] + '.mp4'
            script = textwrap.wrap(valid_vid[1],70)
            script_size = len(script)

            for i in range(0,script_size):
                self.ids.script1.text = self.ids.script2.text
                self.ids.script2.text = self.ids.script3.text
                self.ids.script3.text = self.ids.script4.text
                self.ids.script4.text = self.ids.script5.text
                self.ids.script5.text = script[i]

            self.ids.video.state = 'play'
        else:
            self.ids.script1.text = self.ids.script2.text
            self.ids.script2.text = self.ids.script3.text
            self.ids.script3.text = self.ids.script4.text
            self.ids.script4.text = self.ids.script5.text
            self.ids.script5.text = 'Generation Failed'

class AwesomeApp(App):
    def build(self):
        return MyGridLayout()
    
if __name__ == '__main__':
    AwesomeApp().run()