import nextcord
from nextcord.ext import commands

from pytube import YouTube
import os

class Ytdownloader(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ytmp3(self, ctx, link): # Descarga y manda un video de youtube en formato audio mp3
        yt = YouTube(link)
        song = yt.streams.filter(only_audio=True, file_extension="mp4").last()

        # Los videos se almacenan temporalmente hasta que se envían
        out_file = song.download(output_path="./tests")
        name, ext = os.path.splitext(out_file)
        new_file = name + ".mp3"
        os.rename(out_file, new_file)
        await ctx.send(file=nextcord.File(new_file))
        os.remove(new_file)

def setup(client):
    client.add_cog(Ytdownloader(client))

# Después me gustaría agreagar un cliente web para videos y archivos más pesados que los que permite discord