#!/usr/bin/env python3
import json
from models import app, db, Movie, Actor, Show

# if actors, movie, are shows exist in the DB get and store their IDs to
# prevent duplication
actor_ids = []
actor_ids_db = db.session.query(Actor.id).all()
for ids in actor_ids_db:
    actor_ids.append(ids[0])

movie_ids = []
movie_ids_db = db.session.query(Movie.id).all()
for ids in movie_ids_db:
    movie_ids.append(ids[0])

show_ids = []
show_ids_db = db.session.query(Show.id).all()
for ids in show_ids_db:
    show_ids.append(ids[0])

def fill_db():
    # read in the DB JSON file
    with open('prod_db.json') as fp:
        data = json.load(fp)
        fp.close()

    # get the each list from the data
    movies = data['data']['movies']
    shows = data['data']['shows']
    actors = data['data']['actors']

    # iterate through all movies and instantiate new object to add to DB
    for m in movies:
        if m['id'] not in movie_ids:
            # track all movies that have been created
            movie_ids.append(m['id'])
            newMovie = Movie(
                id=m['id'], 
                title=m['title'], 
                description=m['description'],
                shortDescription=m['shortDescription'],
                length=m['length'],
                year=m['year'],
                language=m['language'],
                score=m['score'],
                ageRec=m['ageRec'],
                genre=m['genre'],
                service=m['service'],
                link=m['link'],
                image=m['image']
            )

            # add movie to database
            db.session.add(newMovie)
            db.session.commit()

            # iterate through cast
            for a_id in m['actors']:
                if a_id not in actor_ids:
                    # track all actors already created
                    actor_ids.append(a_id)
                    for a in actors:
                        if a['id'] == a_id:
                            actor = a
                            break
                    
                    # instantiate new actor object
                    newActor = Actor(
                        id=actor['id'],
                        name=actor['name'],
                        birthday=actor['birthday'],
                        gender=actor['gender'],
                        birthPlace=actor['birthPlace'],
                        bio=actor['bio'],
                        shortBio=actor['shortBio'],
                        image=actor['image']
                    )

                    # add actor to database
                    db.session.add(newActor)
                    db.session.commit()

                    newMovie.acts.append(newActor)

    # iterate through shows
    for s in shows:
        if s['id'] not in show_ids:
            # track all shows already created
            show_ids.append(s['id'])
            # instantiate new Show object
            newShow = Show(
                id=s['id'],
                title=s['title'],
                description=s['description'],
                shortDescription=s['shortDescription'],
                score=s['score'],
                episodes=s['episodes'],
                seasons=s['seasons'],
                year=s['year'],
                language=s['language'],
                lastYear=s['lastYear'],
                ageRec=s['ageRec'],
                genre=s['genre'],
                service=s['service'],
                link=s['link'],
                image=s['image']
            )
            
            # add show to database
            db.session.add(newShow)
            db.session.commit()

            # iterate through cast of show and do same thing as above
            for a_id in s['actors']:
                if a_id not in actor_ids:
                    actor_ids.append(a_id)
                    for a in actors:
                        if a['id'] == a_id:
                            actor = a
                            break

                    newActor = Actor(
                        id=actor['id'],
                        name=actor['name'],
                        birthday=actor['birthday'],
                        gender=actor['gender'],
                        birthPlace=actor['birthPlace'],
                        bio=actor['bio'],
                        shortBio=actor['shortBio'],
                        image=actor['image']
                    )

                    db.session.add(newActor)
                    db.session.commit()

                    newShow.acts.append(newActor)

fill_db()
