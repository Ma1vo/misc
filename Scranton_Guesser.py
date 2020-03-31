import discord
import os
import srt
import subprocess
import time
import random
import json

#bot settings
token = 'Discord-Token'
base_command = 'ffmpeg -hide_banner -ss 00:{}:{} -loglevel panic -copyts -i "{}/S{}/{}" -vf subtitles="{}" -s {} -vframes 1 "output.png" -y'
resolution = '640x360'
offset = 1
random_shuffle = True
delete_query = True
show_info = True

#series
series = []
with open('series.json') as f:
  data = json.load(f)
  for serie in data['series']:
      series.append(serie)

#vars
temp_msg = ' > '
client = discord.Client()
choices = []
display_choices = []
numberEmojis = ["0\N{combining enclosing keycap}","1\N{combining enclosing keycap}","2\N{combining enclosing keycap}","3\N{combining enclosing keycap}","4\N{combining enclosing keycap}","5\N{combining enclosing keycap}","6\N{combining enclosing keycap}","7\N{combining enclosing keycap}","8\N{combining enclosing keycap}","9\N{combining enclosing keycap}"]
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

def search_subs(query,querySeries,*args, **kwargs):
    querySeason = kwargs.get('season', None)
    global display_choices,choices,resolution,base_command,offset,random_shuffle
    choices = []
    results = ''
    folder = querySeries['subsFolder']
    subtitle_folder = os.fsencode(folder)
    season_index = 1
    for subtitle_season in os.listdir(subtitle_folder):
        episode_index = 1
        if querySeason == None or (querySeason != None and querySeason == subtitle_season.decode("utf-8")):
            for subtitle_episode in os.listdir(os.path.join(subtitle_folder,subtitle_season)):
                subtitle_path = os.path.join(subtitle_folder,subtitle_season,subtitle_episode)
                with open(subtitle_path, encoding="utf-8") as subtitle_file:
                    data = subtitle_file.read()
                    subtitle_generator = srt.parse(data)
                    subtitles = list(subtitle_generator)
                    for subtitle in subtitles:
                        if not random_shuffle and len(choices) == 10:
                            return [len(choices),choices]
                        if query.lower() in subtitle.content.lower().replace('\n',' ').replace('<i>',''):
                            min = str((subtitle.start.seconds % 3600) // 60).zfill(2)
                            sec = str(int(subtitle.start.seconds % 60) + offset).zfill(2)
                            season = str(season_index).zfill(2)
                            epindex = str(episode_index).zfill(2)
                            eparr = os.listdir(querySeries['videoFolder'] + 'S' + season)
                            ep = eparr[episode_index - 1]
                            command = base_command.format(min,sec,querySeries['videoFolder'],season,ep,str(subtitle_file.name)[1:],resolution)
                            subtitle_display = subtitle.content.replace('\n',' ').replace('<i>','').replace('</i>','')
                            if '}' in subtitle_display:
                                subtitle_display = subtitle_display.split('}')[1]
                            choices.append([command,subtitle_display,'S'+season,int(epindex),min,sec])
                episode_index += 1
        season_index += 1
    if len(choices) == 1:
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=None)
        output = proc.communicate()
        if output != None:
            with open('output.png', 'rb') as f:
                picture = discord.File(f,'screenshot.png')
                return [len(choices),picture,'S'+season,int(epindex),min,sec]
    else:
        return [len(choices),choices]

@client.event
async def on_ready():
    guild = client.guilds[0]
    print(f'{client.user} is connected to the guild.')

@client.event
async def on_reaction_add(reaction, user):
    if user != client.user:
        if reaction.message.content.replace('\n','').replace('\r', '') == temp_msg.replace('\n','').replace('\r', ''):
            index = int(str(reaction)[:-1])
            proc = subprocess.Popen(choices[index][0], shell=True, stdout=subprocess.PIPE, stderr=None)
            output = proc.communicate()
            channel = reaction.message.channel
            if output != None:
                if show_info:
                    await channel.send(choices[index][2] + 'E' + str(choices[index][3]) + ',' + str(choices[index][4]) + 'min' + str(choices[index][5]))
                with open('output.png', 'rb') as f:
                    picture = discord.File(f,'screenshot.png')
                    await channel.send(file=picture)

@client.event
async def on_message(message):
    global series, temp_msg, random_shuffle, delete_query, show_info
    if message.author == client.user:
        if '> ' in message.content:
            if message.content.replace('\n','').split('> ')[1] == temp_msg.replace('\n','').split('> ')[1]:
                for index in range(len(temp_msg.split('> ')) - 1):
                    await message.add_reaction(numberEmojis[index])
        return

    if '/' in message.content:
        querySeries = []
        for serie in series:
            if message.content.split(' ')[0] == serie['queryCommand']:
                querySeries = serie
                break
        if querySeries == []:
            return
        temp_msg = ''
        if 'S' in message.content.split(' ')[1]:
            search_query = message.content.split(querySeries['queryCommand'] + ' ' + message.content.split(' ')[1] + ' ')[1]
            season = 'S' + message.content.split(' ')[1][1:].zfill(2)
            result = search_subs(search_query,querySeries,season = season)
        else:
            search_query = message.content.split(querySeries['queryCommand'] + ' ')[1]
            result = search_subs(search_query,querySeries)
        if result[0] == 0:
            answer = 'No scene found.'
            await message.channel.send(answer)
            print(answer)
        elif result[0] == 1:
            if delete_query:
                await message.delete()
            if show_info:
                answer = result[2] + 'E' + str(result[3]) + ',' + str(result[4]) + 'min' + str(result[5])
                await message.channel.send(answer)
            message.channel.send(file=result[1])
            print(answer)
        else:
            if delete_query:
                await message.delete()
            msg = ''
            if random_shuffle:
                random.shuffle(result[1])
            for index,quote in enumerate(result[1]):
                added_msg = numberEmojis[index] + '> "' + quote[1] + '" (' + str(quote[2]) + 'E' + str(quote[3]) + ')\n'
                msg += added_msg
                if index == 9:
                    break
            temp_msg = msg
            await message.channel.send(msg)
            print('Found multiple scenes, retrieved the first {}.'.format(index+1))
client.run(token)
