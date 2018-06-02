from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect


class EntryForm(forms.Form):

    genre_choices = [
        ('ambient', 'Ambient'),
        ('chill', 'Chill'),
        ('club', 'Club'),
        ('country', 'Country'),
        ('dance', 'Dance'),
        ('deep-house', 'Deep-House'),
        ('dubstep', 'Dubstep'),
        ('edm', 'Edm'),
        ('hip-hop', 'Hip-Hop'),
        ('house', 'House'),
        ('party', 'Party'),
        ('pop', 'Pop'),
        ('rock', 'Rock'),
        ('sleep', 'Sleep'),
        ('study', 'Study'),
        ('summer', 'Summer'),
        ('work-out', 'Work-Out')
    ]

    artist = forms.CharField(label='Enter an artist*',
                             max_length=100,
                             required=True
                             )
    genre = forms.CharField(label='Choose a genre or two',
                            max_length=100,
                            required=False,
                            widget=forms.SelectMultiple(choices=genre_choices)
                            )
    title = forms.CharField(label='Give it a title',
                            max_length=25,
                            required=False
                            )
    tracks = forms.IntegerField(label='How many tracks?',
                                max_value=15,
                                required=False
                                )


def entry(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():

            return HttpResponseRedirect('result.html')
    else:
        form = EntryForm()

    return render(request, 'entryform.html', {'form': form})