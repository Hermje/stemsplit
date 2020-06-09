from django.shortcuts import render
from django.http import HttpResponse
from separate.forms import YoutubeLinkForm
from spleeter.separator import Separator
from spleeter.audio.adapter import get_default_audio_adapter
import youtube_dl
import os
import zipfile

# Create your views here.
def index(request):
    form = YoutubeLinkForm()

    if request.method == "POST":
        separator = Separator('spleeter:4stems')
        form = YoutubeLinkForm(request.POST)

        if form.is_valid():
            link = form.cleaned_data['link']

            ydl_opts = {
                'outtmpl':'download',
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }],
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])

            separator.separate_to_file('wav', 'result')

            zipf = zipfile.ZipFile('stems.zip', 'w', zipfile.ZIP_DEFLATED)
            for root, dirs, files in os.walk('result/wav'):
                for file in files:
                    zipf.write(os.path.join(root, file))
            zipf.close()

            with open('stems.zip', 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/zip")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename('stems.zip')
                return response

    context = {
        'form' : form,
    }

    return render(request, 'separate/index.html', context)
