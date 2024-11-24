# Waffle-bot

Simple python bot that can play music on voice channels from youtube and other websites

## Commands
  
- join        (joins voice channel)
- leave       (leaves voice channel)
- add <url>   (adds url to queue)
- rm <index>  (removes url from queue by its index)
- clear       (clears queue)
- queue       (shows queued urls)
- play <url>  (plays song from url)
- skip        (skips currently played song)
- pause       (pauses player)
- resume      (resumes player)
- search      (searches for song title)
- ping        (checks ping)
- coinflip    (flips a coin)

Some commands can be used in shorter form (?p ?play are the same thing)

## Setup
### Windows
#### Python 3.8 or higher is required

Clone the project and go to the project directory

```bash
  git clone https://github.com/restricted7331/Waffle-bot/
  cd Waffle-bot
```

Install yt_dl and discord.py 1.7.3

```bash
  pip install yt_dlp 
  pip install discord.py == 1.7.3
  pip install discord.py[voice]
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

Create config.json file first variable should be prefix, second token
```
{
  "prefix": "?",
  "token": ""
}
```

### Run

```bash
  python main.py
```

<a target="_blank" href="https://icons8.com/icon/xnXs0CGoBO17/waffle">Waffle</a> icon by <a target="_blank" href="https://icons8.com">Icons8</a>