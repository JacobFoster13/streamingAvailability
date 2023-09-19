#!/usr/bin/env python3
import requests
import json

# API URLs and keys
rapid_url = "https://streaming-availability.p.rapidapi.com/v2/search/basic"
tmdb_url = "https://api.themoviedb.org/3/"
tmdb_key = "4c91baf92d4358186cbbf860be1673b1"
rapid_key1 = "2688effd4bmsh75075645cde2f87p1fd60cjsn8267dc44dbd2"
rapid_key2 = "7ed3c5729amsh09dbe30e297d0a8p1169b5jsnb6980bbeb47e"

# python dictionary to hold information from API to put in JSON
data = {"data":{
    "movies":[],
    "shows":[],
    "actors":[]
}}

# ensure non-duplicate actors
actor_ids = []

def create_json():

    # ----------
    # MOVIES - RAPID
    # ----------
    cursor = ''
    for num in range(25):
        # API arguments
        querystring = {"country":"us",
            "services":"netflix,disney,hulu",
            "show_type":"movie",
            "cursor": cursor,
            "output_language":"en",
            "language":"en"}

        headers = {
            "X-RapidAPI-Key": rapid_key2,
            "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"
        }

        # GET request to API
        response = requests.request("GET", rapid_url, headers=headers, params=querystring, timeout=120)
        rapid_res = json.loads(response.text)

        # API request results
        results = rapid_res['result']

        # iterate through results
        for i in range(len(results)):
            # create new instance of Movie for each movie returned
            new_movie= {
                "actors": []
            }
            m = results[i]
            movie_id = m['tmdbId']
            # get image link from response
            image_link = ''
            try:
                image_link = m['backdropURLs']['300']
            except:
                for i in range(800):
                    try:
                        image_link = m['backdropURLs'][str(i)]
                    except:
                        continue
            finally:
                if image_link == '':
                    image_link = 'N/A'
            # fill new instance of movie with info from API
            try:
                new_movie['id']=int(movie_id)
                new_movie['title']=m['title']
                new_movie['description']=m['overview'][:1500]
                new_movie['shortDescription']=m['overview'][:100]
                new_movie['length']=m['runtime']
                new_movie['year']=m['year']
                new_movie['language']=m['originalLanguage']
                new_movie['score']=str(float(m['imdbRating'])/10)+"/10"
                new_movie['ageRec']=m['advisedMinimumAudienceAge']
                new_movie['genre']=m['genres'][0]['name']
                new_movie['service']=list(m['streamingInfo']['us'].keys())[0]
                new_movie['link']=m['streamingInfo']['us'][list(m['streamingInfo']['us'].keys())[0]][0]['link']
                new_movie['image']=image_link
            except:
                continue
            
            # add movie to JSON dictionary
            data['data']['movies'].append(new_movie)

            # query TMDB API for cast of current movie
            query = "movie/" + str(movie_id) + "/credits?api_key=" + tmdb_key
            response = requests.request("GET", tmdb_url+query, timeout=120)
            tmdb_res = json.loads(response.text)['cast']

            # limit actors by first five in cast -- check if actor has already been added to JSON dictionary
            for actor in tmdb_res[:5]:
                if actor['id'] in actor_ids:
                    for a in data['data']['actors']:
                        if a['id'] == actor['id']:
                            new_movie['actors'].append(a['id'])
                            a['movies'].append(new_movie['id'])
                    continue
                # if actor does not already exist -- create a new instance for the JSON dictionary
                else:
                    actor_ids.append(actor['id'])
                    new_actor = {
                        "movies": [],
                        "shows": []
                    }
                    # use actor ID to query TMDB API to get actor information and images
                    query = "person/" + str(actor['id']) + "?api_key=" + tmdb_key
                    response = requests.request("GET", tmdb_url+query, timeout=120)
                    tmdb_res = json.loads(response.text)

                    img_query = "person/" + str(actor['id']) + "/images?api_key=" + tmdb_key
                    img_response = requests.request("GET", tmdb_url+img_query, timeout=120)
                    img_res = json.loads(img_response.text)['profiles']

                    # get image for actor
                    if img_res != []:
                        img_path = img_res[0]['file_path']
                        img_link = "https://image.tmdb.org/t/p/w185" + img_path
                    else:
                        img_link = ''

                    # get gender for actor
                    if tmdb_res['gender'] == 1:
                        gender = "Female"
                    elif tmdb_res['gender'] == 2:
                        gender = "Male"
                    else:
                        gender = "Other"
                    
                    # create new instance of Actor for each actor in the cast
                    try:
                        new_actor['id'] = actor['id']
                        new_actor['name'] = tmdb_res['name']
                        new_actor['birthday'] = tmdb_res['birthday']
                        new_actor['gender'] = gender
                        new_actor['birthPlace'] = tmdb_res['place_of_birth'] 
                        new_actor['bio'] = tmdb_res['biography']
                        new_actor['shortBio'] = tmdb_res['biography'][:100]
                        new_actor['movies'].append(new_movie['id'])
                        new_actor['image'] = img_link
                    except:
                        continue
                    
                    # add actor to JSON dictionary
                    data['data']['actors'].append(new_actor)

                    # add actor to cast of movie
                    new_movie['actors'].append(new_actor['id'])

        # go to next page of API
        cursor = rapid_res['nextCursor']
        if cursor == '':
            print("reached end of movies")
            break
        if num % 5 == 0:
            print(num, "pages done for movies")

    print("movies are done")

    # ----------
    # SERIES - RAPID
    # ----------
    cursor = ''
    for num in range(25):
        # API arguments
        querystring = {"country":"us",
            "services":"netflix,disney,hulu",
            "show_type":"series",
            "cursor": cursor,
            "output_language":"en"}

        headers = {
            "X-RapidAPI-Key": rapid_key2,
            "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"
        }

        # get request to API for shows
        response = requests.request("GET", rapid_url, headers=headers, params=querystring, timeout=120)
        rapid_res = json.loads(response.text)
        # API request results
        results = rapid_res['result']

        for i in range(len(results)):
            # create new instance of Show for each show returned
            new_show = {
                "actors": []
            }
            s = results[i]
            series_id = s['tmdbId']
            # get show image
            image_link = ''
            try:
                image_link = s['backdropURLs']['300']
            except:
                for i in range(800):
                    try:
                        image_link = s['backdropURLs'][str(i)]
                    except:
                        continue
            finally:
                if image_link == '':
                    image_link = 'N/A'
            # fill the new instance of show in the JSON dictionary
            try:
                new_show['id'] = int(s['tmdbId'])
                new_show['title'] = s['title']
                new_show['description'] = s['overview'][:1500]
                new_show['shortDescription'] = s['overview'][:100]
                new_show['score'] = str(float(s['imdbRating'])/10)+"/10"
                new_show['episodes'] = s['episodeCount']
                new_show['seasons'] = s['seasonCount']
                new_show['year'] = s['firstAirYear']
                new_show['language'] = s['originalLanguage']
                new_show['lastYear'] = s['lastAirYear']
                new_show['ageRec'] = s['advisedMinimumAudienceAge']
                new_show['genre'] = s['genres'][0]['name']
                new_show['service'] = list(s['streamingInfo']['us'].keys())[0]
                new_show['link'] = s['streamingInfo']['us'][list(s['streamingInfo']['us'].keys())[0]][0]['link']
                new_show['image'] = image_link
            except:
                continue
            
            # append shows to the JSON dictionary
            data['data']['shows'].append(new_show)

            # query TMDB API for cast of current show
            query = "tv/" + str(series_id) + "/credits?api_key=" + tmdb_key
            response = requests.request("GET", tmdb_url+query, timeout=120)
            try:
                tmdb_res = json.loads(response.text)['cast']
            except:
                continue

            # limit actors by first five cast members
            for actor in tmdb_res[:5]:
                # check if actor already exists
                if actor['id'] in actor_ids:
                    for a in data['data']['actors']:
                        if a['id'] == actor['id']:
                            a['shows'].append(new_show['id'])
                            new_show['actors'].append(a['id'])
                    continue
                else:
                    # create new instance of an actor for the JSON dictionary
                    actor_ids.append(actor['id'])
                    new_actor = {
                        "movies": [],
                        "shows": []
                    }
                    # query the TMDB API for actor information and images using ID
                    query = "person/" + str(actor['id']) + "?api_key=" + tmdb_key
                    response = requests.request("GET", tmdb_url+query, timeout=120)
                    tmdb_res = json.loads(response.text)

                    img_query = "person/" + str(actor['id']) + "/images?api_key=" + tmdb_key
                    img_response = requests.request("GET", tmdb_url+img_query, timeout=120)
                    img_res = json.loads(img_response.text)['profiles']

                    # get image of actor
                    if img_res != []:
                        img_path = img_res[0]['file_path']
                        img_link = "https://image.tmdb.org/t/p/w185" + img_path
                    else:
                        img_link = ''

                    # get gender of actor
                    if tmdb_res['gender'] == 1:
                        gender = "Female"
                    elif tmdb_res['gender'] == 2:
                        gender = "Male"
                    else:
                        gender = "Other"

                    try:
                        # create new instance of Actor for each actor in the cast
                        new_actor['id'] = actor['id']
                        new_actor['name'] = tmdb_res['name']
                        new_actor['birthday'] = tmdb_res['birthday']
                        new_actor['gender'] = gender
                        new_actor['birthPlace'] = tmdb_res['place_of_birth'] 
                        new_actor['bio'] = tmdb_res['biography']
                        new_actor['shortBio'] = tmdb_res['biography'][:100]
                        new_actor['shows'].append(new_show['id'])
                        new_actor['image'] = img_link
                    except:
                        continue

                    # append actor to JSON dictionary                   
                    data['data']['actors'].append(new_actor)

                    new_show['actors'].append(new_actor['id'])

        # go to next page of the API
        cursor = rapid_res['nextCursor']
        if cursor == '':
            print('reached end of shows')
            break
        if num % 5 == 0:
            print(num, "pages done for shows")

    print("shows are done")

    # proof file has completed running
    with open("prod_db.json", "w") as fp:
        json.dump(data, fp, indent=4)

    # TESTING
    # with open("test.json", "w") as fp:
    #     json.dump(data, fp, indent=4)
    print("Done: JSON")

create_json()
