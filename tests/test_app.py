# tests/test_app.py

import os
import sys
import unittest

# Must be set BEFORE `from app import ...` runs, since app/db.py reads
# os.getenv("TESTING") once at import time to decide which database to bind
# TimelinePost to (in-memory SQLite here, instead of real MySQL).
os.environ["TESTING"] = "true"

# Ensure the project root (parent of this tests/ folder) is on sys.path, so
# `from app import ...` works whether you run this via `pytest`,
# `python -m unittest`, or `python tests/test_app.py` directly.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from app.db import mydb
from app.models import TimelinePost

# inject_nav() in __init__.py, not as a module-level constant. Hardcoding the expected labels here instead of importing them.
NAV_LABELS = ["Home", "Hobbies", "Travel", "Timeline"]


class AppTestCase(unittest.TestCase):

    # app.test_client() is stateless wiring -- it doesn't touch the database
    # or hold any row data, so it's safe (and slightly cheaper) to create it
    # once for every test in this class rather than rebuilding it per test.
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    # Database state IS mutable and test-specific: one test's POST (e.g.
    # "John Doe") must never leak into the next test's assumption that the
    # table starts empty. So table creation + clearing rows happens fresh
    # before every single test.
    def setUp(self):
        mydb.connect(reuse_if_open=True)
        mydb.create_tables([TimelinePost], safe=True)
        TimelinePost.delete().execute()

    def tearDown(self):
        mydb.drop_tables([TimelinePost], safe=True)
        mydb.close()

    # Helper, not auto-run in setUp: not every test here wants the same
    # starting posts -- test_get_posts_empty specifically needs the table
    # to start empty. Tests opt in by calling this explicitly when they DO
    # want seeded data. Only appropriate for tests that need existing rows
    # as setup -- NOT for tests that are actually verifying the POST route
    # creates rows correctly (those must go through self.client.post(...),
    # or they'd stop testing the route).
    def _seed_john_and_jane(self, john_content="first", jane_content="second"):
        john = TimelinePost.create(name="John Doe", email="john@example.com", content=john_content)
        jane = TimelinePost.create(name="Jane Doe", email="jane@example.com", content=jane_content)
        return john, jane

    # Home page

    def test_home_loads(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        # title and <h1> both render the `title` variable the route passes in
        self.assertIn("<title>Cynthia Lee Wong</title>", html)
        self.assertIn("<h1>Cynthia Lee Wong</h1>", html)

    def test_home_has_shared_nav(self):
        response = self.client.get("/")
        html = response.get_data(as_text=True)

        for label in NAV_LABELS:
            self.assertIn(label, html)

    # Timeline page

    def test_timeline_page_loads(self):
        response = self.client.get("/timeline")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("<title>Timeline</title>", html)
        self.assertIn("<h1>Timeline</h1>", html)
        self.assertIn('id="timeline-form"', html)
        self.assertIn('id="timeline-posts"', html)
        # errors currently only surface via console.error() in the JS, not
        # a dedicated on-page element.

    # GET /api/timeline_post

    def test_get_posts_empty(self):
        # setUp clears the table before every test, so this should always
        # start from zero. This tests the 1st thing a fresh install of the
        # app sees before anyone posts anything (an empty [] should return,
        # not null or a crash).
        response = self.client.get("/api/timeline_post")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertIn("timeline_posts", data)
        self.assertEqual(data["timeline_posts"], [])

    # POST /api/timeline_post

    def test_post_success(self):
        # This test does 2 things: sends a real HTTP POST (through
        # self.client.post(...), exactly like a browser would) and checks
        # the JSON response looks right, then does a separate GET
        # afterward to confirm the post actually landed in the database.
        response = self.client.post(
            "/api/timeline_post",
            data={
                "name": "John Doe",
                "email": "john@example.com",
                "content": "Hello world, I'm John!",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.is_json)
        created_post = response.get_json()
        self.assertEqual(created_post["name"], "John Doe")
        self.assertEqual(created_post["email"], "john@example.com")
        self.assertEqual(created_post["content"], "Hello world, I'm John!")

        # Confirm it actually persisted, not just in the response.
        follow_up = self.client.get("/api/timeline_post")
        data = follow_up.get_json()
        self.assertEqual(len(data["timeline_posts"]), 1)
        self.assertEqual(data["timeline_posts"][0]["content"], "Hello world, I'm John!")

    def test_post_rejects_missing_field(self):
        response = self.client.post(
            "/api/timeline_post",
            data={"email": "john@example.com", "content": "Hello world, I'm John!"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.is_json)
        self.assertIn("error", response.get_json())

    def test_post_rejects_blank_field(self):
        # "content" is present but empty -- distinct edge case from a
        # missing key entirely.
        response = self.client.post(
            "/api/timeline_post",
            data={"name": "John Doe", "email": "john@example.com", "content": ""},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_post_rejects_whitespace_field(self):
        # A field of only spaces should be treated the same as blank/missing
        # -- requires the .strip() in the route, since plain truthiness
        # alone wouldn't catch this ("   " is truthy in Python).
        response = self.client.post(
            "/api/timeline_post",
            data={"name": "   ", "email": "john@example.com", "content": "Hello!"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_post_rejects_invalid_email(self):
        # Basic check: a valid-looking email needs at least an "@" and a
        # "." in the domain -- not full RFC-grade validation, just enough
        # to catch obvious typos/garbage input.
        response = self.client.post(
            "/api/timeline_post",
            data={"name": "John Doe", "email": "not-an-email", "content": "Hello!"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    # DELETE /api/timeline_post/<id>

    def test_delete_success(self):
        # Seeding via the helper (rather than a one-off TimelinePost.create
        # call) also lets this test confirm DELETE only removes the
        # targeted row -- Jane should still be there afterward.
        john, jane = self._seed_john_and_jane()

        response = self.client.delete(f"/api/timeline_post/{john.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"deleted_id": john.id})
        self.assertEqual(TimelinePost.select().count(), 1)
        self.assertTrue(TimelinePost.select().where(TimelinePost.id == jane.id).exists())

    def test_delete_not_found(self):
        # Edge case: deleting an id that was never created.
        response = self.client.delete("/api/timeline_post/999")

        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.get_json())

    # Generic error handling

    def test_unknown_route_404(self):
        response = self.client.get("/this-route-does-not-exist")

        self.assertEqual(response.status_code, 404)


# allows us to run this file like a normal python script in the terminal,
# i.e. "python test_app.py"
if __name__ == '__main__':
    unittest.main()