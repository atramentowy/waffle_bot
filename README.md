# Waffle-bot [![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

Simple disord bot that can play music from youtube and soundcloud without queue

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Commands
  
- play <url>
- stop
- pause
- resume
- join
- leave
- ping
- hello

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

## Authors

- [@restricted](https://github.com/restricted7331)
