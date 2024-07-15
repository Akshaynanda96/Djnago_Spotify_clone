from django.shortcuts import render , redirect ,HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User ,auth
from django.contrib.auth import authenticate, login , logout 
from django.contrib.auth.decorators import login_required
import requests
from bs4 import BeautifulSoup as bs
import re


def Globe_searching(request):
    
    if request.method == 'POST':
        g_search = request.POST.get('G_search')
        url = "https://spotify-scraper.p.rapidapi.com/v1/search"
        
        querystring = {"term":g_search,"type":"track"}
        headers = {
            "x-rapidapi-key": "6204ee6c27msh65aabf12a79d25fp11829bjsn1dff8c84d185",
            "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200 :
            data =  response.json()
            all_tracks = []
            
            total_count = data['tracks']['totalCount']
            
            for song in data['tracks']['items']:
                song_name = song['name']
                song_id  = song['id']
                song_artist = song['artists'][0]['name']
                song_cover = song['album']['cover'][2]['url']
                song_duration = song['durationText']
                search = song_name + ' ' + song_artist
                all_data = {
                    'song_name':song_name,
                    'song_id':song_id,
                    'song_artist':song_artist,
                    'song_cover' : song_cover,
                    'song_duration':song_duration,
                    'search':search
                }

                all_tracks.append(all_data)
        
            context = {
                'total_count':total_count,
                "all_tracks":all_tracks
            }
        
    return render(request , 'search.html', context)
        


def get_track_image(track_id, track_name):
    
    url = 'https://open.spotify.com/track/'+track_id
    r = requests.get(url)
    soup = bs(r.content)
    image_links_html = soup.find('img', {'alt': track_name})
    if image_links_html:
        image_links = image_links_html['srcset']
    else:
        image_links = ''

    match = re.search(r'https:\/\/i\.scdn\.co\/image\/[a-zA-Z0-9]+ 640w', image_links)

    if match:
        url_640w = match.group().rstrip(' 640w')
    else:
        url_640w = ''

    return url_640w

def top_artist():

    url = "https://spotify-scraper.p.rapidapi.com/v1/home"
    headers = {
        "x-rapidapi-key": "6204ee6c27msh65aabf12a79d25fp11829bjsn1dff8c84d185",
        "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        artist_info = []
        
        if 'sections' in response_data:
            
            related_artists = response_data['sections']['items'][0]['contents']['items']

            for artist in related_artists:
                name = artist.get('name', 'Unknown Artist')  
                artist_id = artist.get('id', 'NON ID')  
                visuals = artist.get('visuals', {})
                avatar_url = visuals.get('avatar', [{}])[0].get('url', 'NON url') 
                
                artist_info.append((name, artist_id, avatar_url))
        
        return artist_info
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

def home_tracks( ):

    url = "https://spotify-scraper.p.rapidapi.com/v1/playlist/contents"
    querystring = {"playlistId":"37i9dQZF1DWWQRwui0ExPn"}
    headers = {
        "x-rapidapi-key": "6204ee6c27msh65aabf12a79d25fp11829bjsn1dff8c84d185",
        "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200 :
        data  = response.json()
        title_info = []
        for song in data['contents']['items']:
            track_id = song['id']
            track_name = song['name']
            track_image = song['album']['cover'][2]['url']
            artist_name = song['artists'][0]["name"]      
            search = track_name + " " + artist_name
            songs_list = {
                
                'track_id':track_id,
                'track_name':track_name,
                'track_image':track_image,
                'search':search
            }
            title_info.append(songs_list)
        return title_info
    else:
        return HttpResponse('data not found')

def profile(request , pk ):
    artist_id = pk

    url = "https://spotify-scraper.p.rapidapi.com/v1/artist/overview"
    querystring = {"artistId":artist_id}
    headers = {
        "x-rapidapi-key": "6204ee6c27msh65aabf12a79d25fp11829bjsn1dff8c84d185",
        "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200 :
        data  = response.json()
        monthlyListeners = data['stats']['monthlyListeners']
        profile_cover = data['visuals']['header'][0]['url']
        Artist_name = data['name']
        top_tracks = []
        
        for tracks in data['discography']['topTracks']:    
            track_name = tracks['name']
            track_id = tracks['id']
            track_time = tracks['durationText']
            track_play_count =tracks['playCount']
            Track_artists_name = tracks['artists'][0]['name']
            search = track_name + " " + Track_artists_name
            if get_track_image(track_id , track_name):
                track_image = get_track_image(track_id , track_name )
            else :
                track_image = 'https://img.freepik.com/free-photo/ultra-detailed-nebula-abstract-wallpaper-4_1562-749.jpg'
            
            top_tracks.append((track_id, track_name, track_time, track_play_count,Track_artists_name , track_image ,search))
        
        context = {
            'monthlyListeners' :monthlyListeners,
            'profile_cover':profile_cover,
            'top_tracks':top_tracks,
            'Artist_name':Artist_name,
        }
        
        return render (request , 'profile.html', context)
    else:
        return HttpResponse(request , 'data not found')



def music_player(request , pk):

    music = pk
    url = "https://spotify-scraper.p.rapidapi.com/v1/track/download"
    querystring = {"track": music}
    headers = {
        "x-rapidapi-key": "6204ee6c27msh65aabf12a79d25fp11829bjsn1dff8c84d185",
        "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200 :
        data = response.json()
        
        track_name = data['spotifyTrack']['name']
        artist_name = data['spotifyTrack']['artists'][0]['name']
        song_time = data['spotifyTrack']['durationText']
        song_url = data['youtubeVideo']['audio'][0]['url']
        cover_image =data['spotifyTrack']['album']['cover'][2]['url']
        
        context = {
            'track_name':track_name,
            'artist_name':artist_name,
            'song_time':song_time,
            'cover_image':cover_image,
            'song_url':song_url,
        }
    
    return render (request , 'music.html' , context)


@login_required(login_url='login')
def home(request):
    artist_info = top_artist()
    top_song = home_tracks()
    if artist_info and top_song :
        artist_info = top_artist()
        top_song = home_tracks()
        first = top_song[0:6]
        second = top_song[6:12]
        three = top_song[12:18]
        
        context = {
            'artist_info':artist_info,
            'first':first,
            'second':second,
            'three':three,
        }
        return render( request , 'index.html', context)
    
    else:
        return HttpResponse('Data No fetched ')


# _____________account section________________

def login_page(request):
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user_login = auth.authenticate(username=username, password=password)
        
        if user_login: 
            auth.login(request , user_login)
            return redirect('/')
        else:
            messages.info(request, "Invalid Credentials")
            return redirect('login')
        
    return render( request , 'login.html')

@login_required(login_url='login')
def logout_page(request): 
    
    auth.logout(request)
    return redirect('login')

def signup_page(request):
    
    if request.method == 'POST':
       username = request.POST.get('username')
       email = request.POST.get('email')
       password = request.POST.get('password')
       password2 = request.POST.get('password2')
       if password == password2: 
            if User.objects.filter(email = email).exists():
                messages.info(request, "Email already Taken")
                return redirect('signup')
            elif User.objects.filter(username = username).exists():
                messages.info(request, "Username already Exists")
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username,email=email,password=password)
                user.save()
                #  auto login 
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request , user_login)
                return redirect('/')  
       else:
            messages.info(request, "Password Not Match")
            return redirect('signup')
        
    return render( request , 'signup.html')

