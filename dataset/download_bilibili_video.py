import requests
import re
import json
import os
from moviepy import VideoFileClip, AudioFileClip

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Referer': 'https://www.bilibili.com/'
}

def get_video_info(bvid):
    """获取视频信息，包括标题、视频URL、音频URL"""
    # 获取视频页面源码
    video_page_url = f'https://www.bilibili.com/video/{bvid}'
    response = requests.get(video_page_url, headers=headers)
    html_content = response.text
    
    # 提取视频标题
    title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content)
    if title_match:
        title = re.sub(r'[\\/:*?"<>|]', '', title_match.group(1).strip())  # 清理文件名非法字符
    else:
        title = bvid  # 如果提取标题失败，使用bvid作为文件名
    
    # 提取视频信息JSON数据
    playinfo_match = re.search(r'<script>window\.__playinfo__=(.*?)</script>', html_content)
    if not playinfo_match:
        raise Exception("无法提取视频信息，请检查BVID或Cookie设置")
    
    playinfo = json.loads(playinfo_match.group(1))
    
    # 获取视频和音频URL[1,3](@ref)
    try:
        # 从dash格式获取最高质量的视频和音频
        video_url = playinfo['data']['dash']['video'][0]['baseUrl']
        audio_url = playinfo['data']['dash']['audio'][0]['baseUrl']
    except KeyError:
        # 如果dash格式不可用，尝试durl格式（较低质量）
        video_url = playinfo['data']['durl'][0]['url']
        audio_url = None  # durl格式可能不包含单独音频
    
    return title, video_url, audio_url

def download_file(url, filename, file_type="视频"):
    """下载文件并显示进度"""
    headers_download = headers.copy()
    headers_download['Referer'] = 'https://www.bilibili.com/'
    
    response = requests.get(url, headers=headers_download, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    print(f"开始下载{file_type}...")
    with open(filename, 'wb') as f:
        if total_size == 0:
            f.write(response.content)
        else:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    # 显示下载进度
                    progress = (downloaded / total_size) * 100
                    print(f"\r{file_type}下载进度: {progress:.1f}%", end='', flush=True)
    print(f"\n{file_type}下载完成: {filename}")

def merge_av(video_path, audio_path, output_path):
    """合并视频和音频"""
    print("开始合并视频和音频...")
    try:
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)
        
        # 确保音频和视频长度一致[9,11](@ref)
        min_duration = min(video.duration, audio.duration)
        # video = video.subclip(0, min_duration)
        # audio = audio.subclip(0, min_duration)
        video = video.subclipped(0, min_duration)
        audio = audio.subclipped(0, min_duration)
        
        # final = video.set_audio(audio)
        final_video = video.with_audio(audio)
        final_video.write_videofile(output_path, codec='libx264', audio_codec='aac', logger=None)
        print(f"合并完成: {output_path}")
    except Exception as e:
        print(f"合并过程中出现错误: {e}")
        raise
    finally:
        # 确保关闭剪辑释放资源
        try:
            video.close()
            audio.close()
            final_video.close()
        except:
            pass

def main(bvid):
    """主函数"""
    try:
        print(f"开始处理B站视频: {bvid}")
        
        # 获取视频信息
        title, video_url, audio_url = get_video_info(bvid)
        print(f"视频标题: {title}")
        
        # 创建下载目录
        download_dir = "downloads"
        os.makedirs(download_dir, exist_ok=True)
        
        # 下载视频
        video_filename = os.path.join(download_dir, f"{title}_video.mp4")
        download_file(video_url, video_filename, "视频")
        
        # 下载音频（如果可用）
        if audio_url:
            audio_filename = os.path.join(download_dir, f"{title}_audio.m4a")
            download_file(audio_url, audio_filename, "音频")
        else:
            print("警告: 无法获取音频流，可能只能下载较低质量的视频")
            # 如果没有单独音频，直接使用视频文件
            output_filename = os.path.join(download_dir, f"{title}.mp4")
            os.rename(video_filename, output_filename)
            print(f"视频已保存为: {output_filename}")
            return
        
        # 合并视频和音频
        output_filename = os.path.join(download_dir, f"{title}.mp4")
        merge_av(video_filename, audio_filename, output_filename)
        
        # 清理临时文件
        os.remove(video_filename)
        os.remove(audio_filename)
        print("临时文件已清理")
        
        print(f"视频处理完成: {output_filename}")
        
    except Exception as e:
        print(f"处理过程中出现错误: {e}")

# 使用示例
if __name__ == "__main__":
    # 替换为你要下载的B站视频BV号
    bvid = "BV1se41117WP"  # 示例BV号
    main(bvid)