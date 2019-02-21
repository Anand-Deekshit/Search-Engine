from django.shortcuts import render,redirect
from .check import Check



# Create your views here.
def home(request):
    return render(request,"Search/home.html")

def input_word(request):
    phrase = request.POST['key'];
    Check(phrase)
    urlsDict = Check.urlsDict
    urls = Check.sortUrls(urlsDict)
    print("---------------------------------------")
    print(urls)
    if len(urls)>0:
        return render(request,"Search/found.html", {'urls':urls})
    else:
        return render(request,"Search/notfound.html")
    