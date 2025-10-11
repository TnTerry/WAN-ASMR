from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())
import requests
from tqdm import tqdm

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
'Referer': 'https://www.bilibili.com/'
}

def get_real_url(bvid):
    api_url = f'https://api.bilibili.com/x/player/playurl?bvid={bvid}&qn=112'
    response = requests.get(api_url, headers=headers)
    return response.json()['data']['durl'][0]['url']


def download_video(url, filename):
    response = requests.get(url, headers=headers, stream=True)
    total_size = int(response.headers.get('content-length', 0))

from moviepy.editor import VideoFileClip, AudioFileClip

def merge_av(video_path, audio_path, output_path):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    final = video.set_audio(audio)
    final.write_videofile(output_path, codec='libx264')

def main(bvid):
    # 获取真实地址
    video_url = get_real_url(bvid)
    audio_url = video_url.replace('/video/', '/audio/')

if __name__ == '__main__':
    main('BV1gM4y1w7Bx') # 替换成你要下载的BVID