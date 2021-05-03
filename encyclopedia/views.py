from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

import random

from markdown2 import markdown, Markdown

from . import util, forms

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    requested_entry = util.get_entry(title) # try to get the requested entry
    if requested_entry:
        context = {
            "entry_title": title,
            "entry_html": markdown(requested_entry), # convert file-content (from markdown to html) and pass to template
            "entry_not_found": False
        }
    else:
        context = {
            "entry_not_found": True
        }
    return render(request, "encyclopedia/entry.html", context)


def search(request):
    q = request.GET.get('q')

    # if q is identical with an existing entry: return that entry
    if util.get_entry(q): # if entry exists
        return render(request, "encyclopedia/entry.html", {
            "entry_title": q,
            "entry_html": markdown(util.get_entry(q))
        })
    else: # return the entries (if any) that have the query as a substring of the title
        return render(request, "encyclopedia/searchresults.html", {
            "query": q,
            "entries": [entry for entry in util.list_entries() if q.lower() in entry.lower()]
        })


def new_entry(request):
    if request.method == "POST":
        # save data of the form in newEntry
        newEntry = forms.NewEntryForm(request.POST)

        # check if form data is valid
        if newEntry.is_valid():
            # isolate the title and content from the 'cleaned' version of form data
            title = newEntry.cleaned_data["title"]
            content = newEntry.cleaned_data["content"]
            
            # redirect user to same page if entry already exists, and pass an error that is to be rendered
            if util.get_entry(title) is not None:
                newEntry.fields["content"].initial = util.get_entry(title)
                return render(request, "encyclopedia/newentry.html", {
                    "entry_title": title,
                    "form": newEntry,
                    "entry_is_duplicate": True
                })
            
            # save the new entry and redirect user to the page where the new entry will be rendered
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("entry", kwargs={'title': title}))
        else:
            # If the form is invalid, re-render the page with existing information.
            return render(request, "encyclopedia/newentry.html", {
                "form": newEntry,
                "entry_is_invalid": True
            })

    return render(request, "encyclopedia/newentry.html", {
        "form": forms.NewEntryForm
    })


def edit_entry(request, title):
    if request.method == "GET":
        # get file-content of the entry that is requested to be editted, and return page where that content can be editted
        form = forms.EditEntryForm()
        form.fields["content"].initial = util.get_entry(title) # pre-populate textarea with current content
        return render(request, "encyclopedia/editentry.html", {
            "entry_title": title,
            "form": form
        })
    else:
        editedEntry = forms.EditEntryForm(request.POST)
        if editedEntry.is_valid():
            util.save_entry(title, editedEntry.cleaned_data["content"])
            return HttpResponseRedirect(reverse("entry", kwargs={'title': title}))
        else:
            return render(request, "encyclopedia/editentry.html", {
                "title": title,
                "form": editedEntry
            })


def random_entry(request):
    return HttpResponseRedirect (reverse("entry", kwargs={'title': random.choice(util.list_entries())})) 
