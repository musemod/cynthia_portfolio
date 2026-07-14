import os
import unittest

os.environ["TESTING"] = "true"

from app import app
from app.db import mydb
from app.models import TimelinePost


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        mydb.connect(reuse_if_open=True)
        mydb.create_tables([TimelinePost], safe=True)
        TimelinePost.delete().execute()

    def tearDown(self):
        mydb.drop_tables([TimelinePost], safe=True)
        mydb.close()

    def test_home(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("<title>Cynthia Lee Wong</title>", html)
        self.assertIn("Cynthia Lee Wong", html)

    def test_timeline(self):
        response = self.client.get("/api/timeline_post")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertIn("timeline_posts", data)
        self.assertEqual(len(data["timeline_posts"]), 0)

        post_response = self.client.post(
            "/api/timeline_post",
            data={
                "name": "John Doe",
                "email": "john@example.com",
                "content": "Hello world, I'm John!",
            },
        )

        self.assertEqual(post_response.status_code, 201)
        self.assertTrue(post_response.is_json)
        created_post = post_response.get_json()
        self.assertEqual(created_post["name"], "John Doe")
        self.assertEqual(created_post["email"], "john@example.com")
        self.assertEqual(created_post["content"], "Hello world, I'm John!")

        response = self.client.get("/api/timeline_post")
        data = response.get_json()
        self.assertEqual(len(data["timeline_posts"]), 1)
        self.assertEqual(data["timeline_posts"][0]["content"], "Hello world, I'm John!")

    def test_timeline_page(self):
        response = self.client.get("/timeline")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("<title>Timeline</title>", html)
        self.assertIn('id="timeline-form"', html)
        self.assertIn('id="timeline-posts"', html)

    def test_malformed_timeline_post(self):
        response = self.client.post(
            "/api/timeline_post",
            data={"email": "john@example.com", "content": "Hello world, I'm John!"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

        response = self.client.post(
            "/api/timeline_post",
            data={"name": "John Doe", "email": "john@example.com", "content": ""},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())
