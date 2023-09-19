import os
import sys
import unittest
import requests
import json
from models import db, Actor, Movie, Show

db.create_all()

class DBTestCases(unittest.TestCase):
    def test_show_insert(self):
        s = Show(id=1, title="Test Show", episodes="23", seasons="2", ageRec="17")
        db.session.add(s)
        db.session.commit()

        r = db.session.query(Show).filter_by(id=1).one()
        self.assertEqual(str(r.id), '1')
        self.assertEqual(str(r.title), 'Test Show')
        self.assertEqual(str(r.ageRec), '17')

        db.session.query(Show).filter_by(id=1).delete()
        db.session.commit()

    def test_movie_insert(self):
        m = Movie(id=1, title="Test Movie", length="123", year="2000", genre="Horror")
        db.session.add(m)
        db.session.commit()

        r = db.session.query(Movie).filter_by(id=1).one()
        self.assertEqual(str(r.id), '1')
        self.assertEqual(str(r.title), 'Test Movie')
        self.assertEqual(str(r.genre), 'Horror')

        db.session.query(Movie).filter_by(id=1).delete()
        db.session.commit()

    def test_actor_insert(self):
        a = Actor(id=1, name="Test Actor", birthday="09/13/2000", gender="Male", shortBio="Test bio")
        db.session.add(a)
        db.session.commit()

        r = db.session.query(Actor).filter_by(id=1).one()
        self.assertEqual(str(r.id), '1')
        self.assertEqual(str(r.name), 'Test Actor')
        self.assertEqual(str(r.gender), 'Male')

        db.session.query(Actor).filter_by(id=1).delete()
        db.session.commit()

    def test_actor_contents(self):
        res = db.session.query(Actor).filter_by(id=3).one()
        
        self.assertEqual(str(res.id), '3')
        self.assertEqual(str(res.name), "Harrison Ford")
        self.assertEqual(str(res.gender), "Male")

    def test_show_contents(self):
        res = db.session.query(Show).filter_by(id=82428).one()
        
        self.assertEqual(str(res.id), '82428')
        self.assertEqual(str(res.title), "All American")
        self.assertEqual(str(res.seasons), "5")

    def test_movie_contents(self):
        res = db.session.query(Movie).filter_by(id=15789).one()
        
        self.assertEqual(str(res.id), '15789')
        self.assertEqual(str(res.title), "A Goofy Movie")
        self.assertEqual(str(res.service), "apple")

    def test_rapid_api_status(self):
        url = "https://streaming-availability.p.rapidapi.com/v2/genres"

        headers = {
            "X-RapidAPI-Key": "2688effd4bmsh75075645cde2f87p1fd60cjsn8267dc44dbd2",
            "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers)
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.text)['result']
        self.assertGreater(len(res), 1)

    def test_tmdb_api_status(self):
        url = "https://api.themoviedb.org/3/person/3?api_key=4c91baf92d4358186cbbf860be1673b1"

        response = requests.request("GET", url)
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.text)
        self.assertEqual(res['name'], "Harrison Ford")

if __name__ == '__main__':
    unittest.main()
