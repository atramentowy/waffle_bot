# Waffle-bot [![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

Simple discord bot that can play music from youtube and soundcloud

## Commands
  
- join        (joins voice channel)
- leave       (leaves voice channel)
- add <url>   (adds url to queue)
- rm <index>  (removes url from queue by its index)
- clear       (clears queue)
- queue       (shows queued url's)
- play <url>  (plays music from url)
- skip        (skips played music)
- pause       (pauses player)
- resume      (resumes player)
- ping        (checks ping)
- hello       (hello command)

## Setup
### Windows:
#### Python 3.8 or higher is required

Clone the project and go to the project directory

```bash
  git clone https://github.com/restricted7331/Waffle-bot/
  cd Waffle-bot
```

Install youtube_dl and discord.py 

```bash
  pip install youtube_dl
  pip install discord.py==1.7.3
```

Install ffmpeg

- download executables https://ffmpeg.org/download.html
- extract, and move it into the root of C: drive
- run cmd as an administrator and set the env path variable for ffmpeg, you can use the following command:
```bash
  setx /m PATH "C:\ffmpeg\bin;%PATH%"
```
- restart and verify installation by running:
```bash
  ffmpeg -version
```

Enter the bot token in the config.json

## Run

```bash
  python main.py
```

## Author

- [@restricted](https://github.com/restricted7331)
