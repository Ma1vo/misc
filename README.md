# Scranton-Guesser
A Python Discord bot that turns quotes from a series to screenshots.

## Usage :
/seriescommand (optional season filter) quote

### For example :
>/office quarantine

>/office S03 Jim

>/parks Pawnee

>/parks S01 Leslie

## How to run it :
- Clone this repository
- Change the token var in Scranton_Guesser.py to your Discord Bot token
- In series.json, add your own series :
  - 'queryCommand' is the command you call the Discord bot with
  - 'subsFolder' is the folder where the subtitles are located in
  - 'videoFolder' is the folder where the video files are located in
- Subtitles folder must follow this folder format :
  - SubtitleFolder/
    - S01
      - EP1.srt
      - EP2.srt
      - ...
    - S02
      - EP1.srt
      - EP2.srt
      - ...
    -...
  The season folders and the subtitle files do not need to follow any name formatting as long as their alphabetical order matches their chronological order, but the bot can only read .srt files.  

## Optional :
If you want to run this bot on your computer
- Create a copy of Scranton_Guesser.py and change the extension to .pyw (runs the script without a console)
- Create a shortcut of this file
- Copy/Paste this shortcut in the startup folder (Windows Key + R, 'shell:startup')
