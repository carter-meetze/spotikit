from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from datetime import datetime


class EntryForm(forms.Form):

    SelectDateWidget = forms.SelectDateWidget
    start_year = datetime.today().year - 85
    current_year = datetime.today().year
    years = [i for i in range(start_year, current_year)]
    birthday = forms.DateField(widget=SelectDateWidget(empty_label="Nothing", years=years))


def Ventry(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():

            return HttpResponseRedirect('vibifi_data.html')
    else:
        form = EntryForm()

    return render(request, 'vibifi_entryform.html', {'form': form})
