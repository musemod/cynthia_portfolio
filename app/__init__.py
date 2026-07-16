# __init__.py

import os
import re
from flask import Flask, render_template, request
from dotenv import load_dotenv
from playhouse.shortcuts import model_to_dict

from app.db import mydb
from app.models import TimelinePost


from app.portfolio_data import SOCIAL_LINKS, ABOUT_TEXT, HERO_DATA, TECH_PROJECTS, WEBSITE_URL, EDUCATION, HOBBIES_PODCAST, HOBBIES_ART, HOBBIES_MUSIC, WORK_EXPERIENCES, LOCATIONS

load_dotenv()
app = Flask(__name__)
# Note: currently using flat pattern (app created at module level).
# Should refactor to application factory pattern (create_app() + config.py)
# in future weeks when we have multiple environments (dev/test/prod) and Docker.


# adds nav links to every template
@app.context_processor
def inject_nav():
    return dict(nav_pages=[
        {"label": "Home", "endpoint": "index"},
        {"label": "Hobbies", "endpoint": "hobbies"},
        {"label": "Travel", "endpoint": "travel"},
        {"label": "Timeline", "endpoint": "timeline"},
    ],
    url=os.getenv("URL") # reads from .env — will be localhost:5000 locally,
                         # real domain in production when MLH deploys in future weeks
    )

@app.route('/')
def index():
    return render_template(
        'index.html',
        title="Cynthia Lee Wong",
        social_links=SOCIAL_LINKS,
        about_text=ABOUT_TEXT,
        hero_data=HERO_DATA,
        website_url=WEBSITE_URL,
        work_experiences=WORK_EXPERIENCES,
        education=EDUCATION,
        tech_projects=TECH_PROJECTS
    )

@app.route('/hobbies')
def hobbies():
    return render_template('hobbies.html', title="Hobbies", hobbies_podcast=HOBBIES_PODCAST, hobbies_art=HOBBIES_ART, hobbies_music=HOBBIES_MUSIC)

@app.route('/travel')
def travel():
    return render_template('travel.html', title="Travel Map", locations=LOCATIONS)

@app.route('/timeline')
def timeline():
    return render_template('timeline.html', title="Timeline")

# regex email pattern
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

@app.route('/api/timeline_post', methods=['POST'])
def post_time_line_post():
    name = (request.form.get('name') or '').strip()
    email = (request.form.get('email') or '').strip()
    content = (request.form.get('content') or '').strip()

    if not name or not email or not content:
        return {'error': 'name, email, and content are all required'}, 400

    if not EMAIL_PATTERN.match(email):
        return {'error': 'email must be a valid email address'}, 400

    timeline_post = TimelinePost.create(name=name, email=email, content=content)

    return model_to_dict(timeline_post), 201
    

@app.route('/api/timeline_post', methods=['GET'])
def get_time_line_post():
    return {
        'timeline_posts': [
            model_to_dict(p)
            for p in 
            TimelinePost.select().order_by(TimelinePost.created_at.desc())
        ]
    }

@app.route('/api/timeline_post/<int:id>', methods=['DELETE'])
def delete_time_line_post(id):
    post = TimelinePost.get_or_none(TimelinePost.id == id)
    if post is None:
        return {'error': f'No post found with id {id}'}, 404

    post.delete_instance()
    return {'deleted_id': id}, 200




def init_db():
    mydb.connect()
    mydb.create_tables([TimelinePost])
    


init_db()

if __name__ == '__main__':
    app.run(debug=True)