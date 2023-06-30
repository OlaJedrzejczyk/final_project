from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views import View

import requests
import random
import re

# Create your views here.


def get_popular_podcasts():
    url = "https://itunes.apple.com/pl/rss/toppodcasts/limit=100/json"
    response = requests.get(url)
    data = response.json()

    if "feed" in data and "entry" in data["feed"]:
        podcasts = []
        for podcast in data["feed"]["entry"]:
            podcast_id = podcast["id"]["label"]
            podcast_author = podcast["im:artist"]["label"]
            podcast_name = podcast["im:name"]["label"]
            podcast_image = podcast["im:image"][0]["label"]
            podcast_summary = podcast["summary"]["label"]
            podcast_genre = podcast["category"]["attributes"]["label"]

            summary_sentences = re.split(r'[.!?]',
                                         podcast_summary)
            podcast_summary = ' '.join(summary_sentences[:2]) + '.'

            podcasts.append({
                "id": podcast_id,
                "author": podcast_author,
                "name": podcast_name,
                "image": podcast_image,
                "summary": podcast_summary,
                "genre": podcast_genre
            })

        return podcasts

    else:
        print("Failed to retrieve podcasts.")
        return []


def get_all_genres():
    url = "https://itunes.apple.com/pl/rss/toppodcasts/limit=100/json"
    response = requests.get(url)
    data = response.json()

    genres = []

    if "feed" in data and "entry" in data["feed"]:
        for podcast in data["feed"]["entry"]:
            podcast_genre = podcast["category"]["attributes"]["label"]
            if podcast_genre not in genres:
                genres.append(podcast_genre)

    else:
        print("Failed to retrieve genres.")

    return genres


class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')


#klasa kategorii konieczna do formularza
class GenreFormView(View):
    def get(self, request):
        all_genres = get_all_genres()
        return render(request, 'form.html', {'genres': all_genres})

    def post(self, request):
        selected_genre_name = request.POST.get('genre')
        all_genres = get_all_genres()

        if selected_genre_name in all_genres:
            selected_genre = selected_genre_name
            podcasts = get_popular_podcasts()
            selected_podcasts = [podcast for podcast in podcasts if podcast["genre"] == selected_genre]

            if len(selected_podcasts) == 0:
                message = "No podcasts found in the selected category."
                return render(request, 'result.html', {'message': message})
            else:
                if len(selected_podcasts) >= 10:
                    selected_podcasts = random.sample(selected_podcasts, 10)

                return render(request, 'result.html', {'podcasts': selected_podcasts})
        else:
            message = "Invalid genre name."
            return render(request, 'result.html', {'message': message})


class ResultView(View):
    def get(self, request):
        return redirect('home')


def signup(request):

    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exists! Please try other username")

        if User.objects.filter(email=email):
            messages.error(request, "Email already registered")

        if len(username) > 10:
            messages.error(request, "Username must be under 10 characters")

        if pass1 != pass2:
            messages.error(request, "Passwords don't match")

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-numeric")

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname

        myuser.save()

        messages.success(request, "Your account has been successfully created, now you can log in")

        return redirect('signin')

    return render(request, "signup.html")


def signin(request):
    all_genres = get_all_genres()
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            # fname = user.first_name
            return render(request, "form.html", {'genres': all_genres})
        else:
            messages.error(request, "Wrong details")
            return redirect('signin')

    return render(request, "signin.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('home')


@login_required
def profile(request):
    return render(request, 'profile.html')