from django.shortcuts import HttpResponse, render, redirect
from django import forms
import markdown2
from . import util

import random


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, entry_name):
    entry = util.get_entry(entry_name)

    if not entry:
        return render(request, "encyclopedia/404.html")
    return render(request, "encyclopedia/entry.html", {
        "title": entry_name,
        "content": markdown2.markdown(entry)
    })


def search(request):
    query = request.GET['q']

    entry = util.get_entry(query)
    if (entry):
        return redirect(f'/wiki/{query}')

    entries = util.list_entries()
    matched_entries = list()

    for entry in entries:
        if entry.lower().find(query.lower()) != -1:
            matched_entries.append(entry)

    return render(request, 'encyclopedia/search.html', {
        'query': query,
        'results': matched_entries
    })


class NewPageForm(forms.Form):
    title = forms.CharField(label="Entry title")
    content = forms.CharField(widget=forms.Textarea)


def new_page(request):
    if request.method == "GET":
        return render(request, 'encyclopedia/new_page.html', {
            "form": NewPageForm()
        })

    elif request.method == "POST":
        form = NewPageForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']

            existing_entry = util.get_entry(title)

            if (existing_entry):
                return render(request, 'encyclopedia/new_page.html', {
                    "form": NewPageForm(),
                    "error": "Entry already exists"
                })

            util.save_entry(title, content)
            return redirect(f"/wiki/{title}")


class EditEntryForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)


def edit_entry(request, entry_name):

    entry = util.get_entry(entry_name)

    if request.method == "GET":
        return render(request, 'encyclopedia/edit_entry.html', {
            "title": entry_name,
            "form": EditEntryForm(initial={'content': entry})
        })

    if request.method == "POST":
        form = EditEntryForm(request.POST)

        if form.is_valid():
            content = form.cleaned_data['content']

            util.save_entry(entry_name, content)
            return redirect(f"/wiki/{entry_name}")


def random_page(request):
    entries = util.list_entries()

    entry = random.choice(entries)

    return redirect(f"/wiki/{entry}")
