import json
import requests
import pandas as pd
import os
from dotenv import load_dotenv

### TODO ###
# add exception handling
# create GUI, web app, or website
# QOL changes
### TODO ###

def get_playlist_tracks(playlist_url):
    # Indices of the URI in the playlist link
    playlist_id = playlist_url[len(
        'https://open.spotify.com/playlist/'):len('https://open.spotify.com/playlist/') + 22]

    ''' getting track uris '''
    playlist = requests.get(BASE_URL + 'playlists/' + playlist_id +
                            '/tracks', headers=headers)  # Gets the url and requests data
    playlist = playlist.json()
    # Takes in only the tracks of a playlist
    playlist_tracks = playlist.get('items')

    playlist_track_uri = [track.get('track').get(
        'uri')[14:] for track in playlist_tracks]  # List of uris

    return get_music_data(playlist_track_uri)


def get_album_tracks(album_url):

    # Indices of the URI in the playlist link
    album_id = album_url[len('https://open.spotify.com/album/')                         
                        :len('https://open.spotify.com/album/') + 22]

    ''' getting track uris '''
    playlist = requests.get(BASE_URL + 'albums/' +
                            album_id + '/tracks', headers=headers)
    playlist = playlist.json()
    playlist_tracks = playlist.get('items')

    playlist_track_uri = [track.get('uri')[14:]
                          for track in playlist_tracks]  # List of uris

    return get_music_data(playlist_track_uri)


''' CREATING A DATAFRAME OF THE AUDIO FEATURES OF TRACKS '''

''' 
                                <COLUMNS>
['artists', 'name', 'album', 'release_date', 'popularity', 'href',
       'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
       'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
       'type', 'id', 'uri', 'analysis_url', 'duration_ms', 'time_signature']
'''


def get_music_data(dict_uri):
    music_data = pd.DataFrame()
    name = pd.DataFrame()

    counter = 0
    for i in dict_uri:
        ''' getting track information '''
        song_info = requests.get(BASE_URL + 'tracks/' + i, headers=headers)
        song_info = song_info.json()

        data = {
            # Formatted without [] or ''
            'artists': ', '.join([song.get('name') for song in song_info.get('artists')]),
            'name': song_info.get('name'),
            'album': song_info.get('album').get('name'),
            'release_date': song_info.get('album').get('release_date'),
            'popularity': song_info.get('popularity'),
            'href': song_info.get('href'),
        }

        name = name.append(pd.DataFrame(data=data, index=[counter]))

        ''' getting track audio features '''
        song_info = requests.get(
            BASE_URL + 'audio-features/' + i, headers=headers)
        song_info = song_info.json()

        music_data = music_data.append(
            pd.DataFrame(data=song_info, index=[counter]))

        counter += 1

    ''' merging song information and audio features '''
    music_data = music_data.rename(columns={'track_href': 'href'})
    music_data = name.merge(music_data, on='href')

    return music_data


''' Takes the dataframe and prints it to csv '''


def playlist_to_csv(playlist):
    user_answer = input(
        'Type in the name of the .csv file without the extension: ')

    if not os.path.isfile(user_answer + '.csv'):
        playlist.to_csv(user_answer + '.csv', index=False,
                        header='column_names')
    else:  # else it exists so append without writing the header
        playlist.to_csv(user_answer + '.csv', index=False,
                        mode='a', header=False)

     
''' Running the script '''
def run():
    final_playlist = pd.DataFrame()
    keepRunning = True

    while (keepRunning is True):
        user_answer = input(
            'What type of playlist do you want to get data from?\n[playlist] for your own\n[album] for an album\n[track] for a single song\n[quit] to quit: ')

        if (user_answer.lower() == 'album'):
            user_answer = input('Input an album URL: ')
            try: # Exception handling if the user inputs an invalid URL 
                album_tracks = get_album_tracks(user_answer)

                ''' Checks to see if the dataframe is empty to add or append to the dataframe '''                
                if (final_playlist.empty == True):
                    final_playlist = album_tracks
                else:
                    final_playlist = final_playlist.append(album_tracks)

                ''' Checks in with user to add new tracks or create the csv '''                    
                user_answer = input('Want to add another playlist or album?(y/n) ')

                if (user_answer.lower() == 'n'):
                    keepRunning = False
                    playlist_to_csv(final_playlist)
            except TypeError:
                print("Not a valid URL.")

        elif(user_answer.lower() == 'playlist'):
            user_answer = input('Input a playlist URL: ')
            try: # Exception handling if the user inputs an invalid URL 
                playlist_tracks = get_playlist_tracks(user_answer)

                ''' Checks to see if the dataframe is empty to add or append to the dataframe '''
                if (final_playlist.empty == True):
                    final_playlist = playlist_tracks
                else:
                    final_playlist = final_playlist.append(playlist_tracks)

                ''' Checks in with user to add new tracks or create the csv '''
                ''' Checks in with user to add new tracks or create the csv '''

                user_answer = input('Want to add another playlist or album?(y/n) ')

                if (user_answer.lower() == 'n'):
                    keepRunning = False
                    playlist_to_csv(final_playlist)

            except TypeError:
                print("Not a valid URL.")

        elif(user_answer.lower() == 'track'):
            user_answer = input('Input a track URL: ')

            user_answer_uri = user_answer[(len(
                'https://open.spotify.com/track/')):(len('https://open.spotify.com/track/') + 22)] 

            try: # Exception handling if the user inputs an invalid URL 
                ''' Checks to see if the dataframe is empty to add or append to the dataframe '''
                if (final_playlist.empty == True):
                    final_playlist = get_music_data([user_answer_uri])
                else:
                    final_playlist = final_playlist.append(
                        get_music_data([user_answer_uri]))

                ''' Checks in with user to add new tracks or create the csv '''
                user_answer = input('Want to add another playlist or album?(y/n) ')

                if (user_answer.lower() == 'n'):
                    keepRunning = False
                    playlist_to_csv(final_playlist) # Creates csv file

            except TypeError:
                print("Not a valid URL.")

        elif(user_answer.lower() == 'quit'):
            keepRunning = False

''' Main method to run the program '''
if __name__ == "__main__":

    ''' setting up '''
    load_dotenv()

    # authorization URL to gain access to the Spotify API
    AUTH_URL = 'https://accounts.spotify.com/api/token'

    # POST to get Spotify access token 
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': os.getenv('CLIENT_ID'), # Spotify integration ID
        'client_secret': os.getenv('CLIENT_SECRET'), # Spotify integration secret
        "expires_in": 3600
    })

    # convert the response to JSON
    auth_response_data = auth_response.json()

    # save the access token
    access_token = auth_response_data['access_token']

    # headers to request anything in the Spotify API 
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }
    
    # base URL of all Spotify API endpoints
    BASE_URL = 'https://api.spotify.com/v1/'

    # run program
    run()
