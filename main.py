#!/usr/bin/env python3

from flask import render_template, request, redirect, url_for, session
from actors import actorsList
import json
from models import app, db, Actor, Show, Movie
from create_db import fill_db
from sqlalchemy import asc, desc, or_, and_, any_
import secrets

# opening page
@app.route('/')
def index():
    return render_template('splash.html')

@app.route('/test')
def test():
    return render_template('searchBar.html')

# about page
@app.route('/AboutUs')
def about():
    return render_template('about.html')

# actors page
@app.route('/actors', methods=['GET'])
def actors():
    # pagination arguments
    page = request.args.get('page', 1, type=int)
    per_page = 30
    # get arguments from request
    search = request.args.get('search')
    services = request.args.getlist('service')
    # get all actors from DB ordered by their ID
    query = db.session.query(Actor).order_by(Actor.id)
    if search:
        # filter to find actors similar to user query
        query = query.filter(Actor.name.like(f'%{search}%'))
    # filter by services
    if len(services) == 1:
        query = query.filter(Actor.movies.any(Movie.service == services[0]))
        actor_list = query.paginate(page=page, per_page=per_page)
        return render_template('actorsFl.html', actors = actor_list)
    filtered = []
    for service in services:
        filtered.append(Actor.movies.any(Movie.service == service))
    if filtered:
        query = query.filter(or_(*filtered))
    # finalize actor_list and pass to front end
    actor_list = query.paginate(page=page, per_page=per_page)
    return render_template('actorsFl.html', actors = actor_list)

# actor search function between pages
@app.route('/actor_search?actor=<string:actor>', methods=['GET'])
def actor_search(actor):
    # pagination arguments
    page = request.args.get('page', 1, type=int)
    per_page = 30
    # get user request
    query = db.session.query(Actor).filter(Actor.name.like(f'%{actor}%'))
    # return the actor(s) that match the users request from non Actors page
    actor_list = query.paginate(page=page, per_page=per_page)
    return render_template('actorsFl.html', actors=actor_list)
   
# same idea as actors page and search funtions
@app.route('/movies', methods=['GET'])
def movies():
    page = request.args.get('page', 1, type=int)
    per_page = 30
    search = request.args.get('search')
    services = request.args.getlist('service')
    query = db.session.query(Movie)
    if search:
        query = query.filter(Movie.title.like(f"%{search}%"))
    if len(services) == 1:
        query = query.filter_by(service=services[0])
        movies_list = query.paginate(page=page, per_page=per_page)
        return render_template('movies_new.html', movies= movies_list)
    filtered = []
    for service in services:
        filtered.append(Movie.service == service)
    if filtered:
        query = query.filter(or_(*filtered))

    movies_list = query.paginate(page=page, per_page=per_page)
    return render_template('movies_new.html', movies= movies_list)

@app.route('/movie_search?movie=<string:movie>', methods=['GET'])
def movie_search(movie):
    page = request.args.get('page', 1, type=int)
    per_page = 30
    query = db.session.query(Movie).filter(Movie.title.like(f'%{movie}%'))
    movie_list = query.paginate(page=page, per_page=per_page)
    return render_template("movies_new.html", movies=movie_list)
    
@app.route('/tvshows', methods=['GET'])
def tvshows():
    page = request.args.get('page', 1, type=int)
    per_page = 30
    search = request.args.get('search')
    services = request.args.getlist('service')
    query = db.session.query(Show)
    if search:
        print(f'found search: {search}')
        query = query.filter(Show.title.like(f"%{search}%"))
    if len(services) == 1:
        query = query.filter_by(service=services[0])
        shows = query.paginate(page=page, per_page=per_page)
        return render_template('tvshowsFL.html', shows=shows)
    filtered = []

    for service in services:
        print(f'hit services: {service}')
        filtered.append(Show.service == service)
    if filtered:
        query = query.filter(or_(*filtered))
    shows = query.paginate(page=page, per_page=per_page)

    return render_template('tvshowsFL.html', shows=shows)

@app.route('/show_search?show=<string:show>', methods=['GET'])
def show_search(show):
    page = request.args.get('page', 1, type=int)
    per_page = 30
    query = db.session.query(Show).filter(Show.title.like(f'%{show}%'))
    show_list = query.paginate(page=page, per_page=per_page)
    return render_template("tvshowsFL.html", shows=show_list)

# reverse sort method for models page
@app.template_filter('reverse_if')
def reverse_if(value, sort_by):
    if value == 'asc':
        return 'desc'
    else:
        return 'asc'

# models page
@app.route('/models/', defaults = {'type': 'All'},  methods=['GET', 'POST'])
@app.route('/models/<type>',  methods=['GET', 'POST'])
def models(type):

    # all models returned
    if type == "All":
        return render_template('models.html')
    
    # determine which page user wants to see
    if type == "Actor" or type == "A":
        type = Actor
        var = "A"
    elif type == "Movie" or type == "M":
        type = Movie
        var = "M"
    elif type == "Show" or type == "S":
        type = Show
        var = "S"
        
    page = request.args.get('page', 1, type=int)
    per_page = 30
    search = request.args.get('search')
    services = request.args.getlist('service')
    sort_by = request.args.get('sort_by', type=str)
    sort_order = request.args.get('sort_order', type=str)
    query = db.session.query(type)

    #distinguish sorting order
    if sort_order == 'asc':
        sort_fn = asc
    else:
        sort_fn = desc

    if search:
        if var == "A": #if we're searching actors
          query = query.filter(type.name.like(f'%{search}%'))
        else:  #movies or tv shows
            query = query.filter(type.title.like(f"%{search}%"))
    if len(services) == 1:
        if var == "A": #filtering actors
            query = query.filter(type.movies.any(Movie.service == services[0]))
        else: #tv shows or movies
            query = query.filter_by(service=services[0])
    filtered = []
    if var == "A": #filtering by actors
        for service in services:
            filtered.append(type.movies.any(Movie.service == service))
    else: #movies or tv shows
        for service in services:
            filtered.append(type.service == service)
    if filtered:
        query = query.filter(or_(*filtered))
    
    #sort the filtered data
    if sort_by:
        Qlist = query.order_by(sort_fn(sort_by)).paginate(page=page, per_page=per_page)
    
    else:
        Qlist = query.paginate(page=page, per_page=per_page)


    return render_template('models_table.html', data = Qlist, type = var, sort_by=sort_by, sort_order=str(sort_order))
 
# DEPRECATED
@app.route('/modelInstance/<type>/<id>')
def modelInstance(type, id):
    if type == "Actor" or type == "A":
        type = Actor
        var = "A"
    
    elif type == "Movie" or type == "M":
        type = Movie
        var="M"
     
    elif type == "Show" or type == "S":
        type = Show
        var="S"
    
    data = db.session.query(type).filter_by(id=id).first()
    print(data.shortDescription.type)
    return render_template('modelInstance.html', data = data, type = var)

# -----------
# API ROUTES
# -----------

# get all shows
@app.route("/api/shows", methods=['GET'])
def api_shows():
    if request.method == 'GET':
        # find show
        shows_req = db.session.query(Show).all()
        # create dictionary for jsonifying
        shows = {'shows':[]}
        # iterate and jsonify all shows
        for s in shows_req:
            cast = s.acts
            s = s.__dict__
            # fix/remove non serializable elements for JSON
            del s['_sa_instance_state']
            del s['acts']
            s['cast'] = [a.name for a in cast]
            shows['shows'].append(s)
        # return JSON response
        return json.dumps(shows, indent=4)
    else:
        return "<h1>bruh wyd</h1>"

# get show by ID
@app.route("/api/shows/<int:show_id>", methods=['GET'])
def api_show(show_id):
    if request.method == "GET":
        try:
            # query db for specific show
            req_show = db.session.query(Show).filter_by(id=show_id).one()
            # collect cast of show
            cast = req_show.acts
            # convert object to dictionary for jsonifying
            res_show = req_show.__dict__
            # fix/remove non serializable elements for JSON
            del res_show['_sa_instance_state']
            del res_show['acts']
            res_show['cast'] = [a.name for a in cast]
            # return JSON response
            return json.dumps(res_show, indent=4)
        except:
            return json.dumps({"error":"no show with id of "+str(show_id)})
    else:
        return "<h1>bruh wyd</h1>"

# get all movies
# same logic as get all shows
@app.route("/api/movies", methods=['GET'])
def api_movies():
    if request.method == 'GET':
        movies_req = db.session.query(Movie).all()
        movies = {'movies':[]}
        for m in movies_req:
            cast = m.acts
            m = m.__dict__
            del m['_sa_instance_state']
            del m['acts']
            m['cast'] = [a.name for a in cast]
            movies['movies'].append(m)
        return json.dumps(movies, indent=4)
    else:
        return "<h1>bruh wyd</h1>"

# get movie by ID
# same logic as get show by ID
@app.route("/api/movies/<int:movie_id>", methods=['GET'])
def api_movie(movie_id):
    if request.method == "GET":
        try:
            req_movie = db.session.query(Movie).filter_by(id=movie_id).one()
            cast = req_movie.acts
            res_movie = req_movie.__dict__
            # fix/remove non serializable elements for JSON
            del res_movie['_sa_instance_state']
            del res_movie['acts']
            res_movie['cast'] = [a.name for a in cast]
            return json.dumps(res_movie, indent=4)
        except:
            return json.dumps({"error":"no movie with id of "+str(movie_id)})
    else:
        return "<h1>bruh wyd</h1>"

# get all actors
# same logic as get all movies and shows
@app.route("/api/actors", methods=['GET'])
def api_actors():
    if request.method == 'GET':
        actors_req = db.session.query(Actor).all()
        actors = {'actors':[]}
        for a in actors_req:
            shows = a.shows
            movies = a.movies
            a = a.__dict__
            # fix/remove non serializable elements for JSON
            del a['_sa_instance_state']
            a['shows'] = [s.title for s in shows]
            a['movies'] = [m.title for m in movies]
            a['birthday'] = str(a['birthday'])
            actors['actors'].append(a)
        return json.dumps(actors, indent=4)
    else:
        return "<h1>bruh wyd</h1>"

# get actor by ID
# same logic as get show/movie by ID
@app.route("/api/actors/<int:actor_id>", methods=['GET'])
def api_actor(actor_id):
    if request.method == "GET":
        try:
            req_actor = db.session.query(Actor).filter_by(id=actor_id).one()
            shows = req_actor.shows
            movies = req_actor.movies
            res_actor = req_actor.__dict__
            # fix/remove non serializable elements for JSON
            del res_actor['_sa_instance_state']
            res_actor['shows'] = [s.title for s in shows]
            res_actor['movies'] = [m.title for m in movies]
            res_actor['birthday'] = str(res_actor['birthday'])
            return json.dumps(res_actor, indent=4)
        except:
            return json.dumps({"error":"no actor with id of "+str(actor_id)})
    else:
        return "<h1>bruh wyd</h1>"

# get movies and shows offered by specific service
@app.route('/api/services/<string:name>', methods=['GET'])
def api_service(name):
    if request.method == 'GET':
        res = {
            'shows':[],
            'movies':[]
        }

        # get all shows and movies under a service
        shows = db.session.query(Show).filter_by(service=name.lower()).all()
        movies = db.session.query(Movie).filter_by(service=name.lower()).all()

        # jsonify the shows and movies
        for m in movies:
            cast = m.acts
            m = m.__dict__
            # fix/remove non serializable elements for JSON
            del m['_sa_instance_state']
            del m['acts']
            m['cast'] = [a.name for a in cast]
            res['movies'].append(m)

        for s in shows:
            cast = s.acts
            s = s.__dict__
            # fix/remove non serializable elements for JSON
            del s['_sa_instance_state']
            del s['acts']
            s['cast'] = [a.name for a in cast]
            res['shows'].append(s)

        return json.dumps(res, indent=4)
    else:
        return "<h1>bruh wyd</h1>"

# for all services
@app.route('/api/services', methods=['GET'])
def api_services():
    services = set()
    res = {"services" : []}
    # gather all services
    show_services = db.session.query(Show.service).distinct().all()
    movie_services = db.session.query(Movie.service).distinct().all()
    
    # add services to the set to ensure no duplicates
    for i in show_services:
        services.add(i[0])

    for i in movie_services:
        services.add(i[0])

    # convert set to list and add to dictionary for JSON response
    res['services'] = list(services)

    return(json.dumps(res, indent=4))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
    