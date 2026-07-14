import unittest

from peewee import SqliteDatabase

from app.models import TimelinePost


MODELS = [TimelinePost]

# Use a fresh temporary database for each test.
test_db = SqliteDatabase(":memory:")


class TestTimelinePost(unittest.TestCase):
    def setUp(self):
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
        test_db.connect()
        test_db.create_tables(MODELS)

    def tearDown(self):
        test_db.drop_tables(MODELS)
        test_db.close()

    def test_timeline_post(self):
        first_post = TimelinePost.create(
            name="John Doe",
            email="john@example.com",
            content="Hello world, I'm John!",
        )
        self.assertEqual(first_post.id, 1)

        second_post = TimelinePost.create(
            name="Jane Doe",
            email="jane@example.com",
            content="Hello world, I'm Jane!",
        )
        self.assertEqual(second_post.id, 2)

        posts = list(TimelinePost.select().order_by(TimelinePost.id))

        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0].name, "John Doe")
        self.assertEqual(posts[0].email, "john@example.com")
        self.assertEqual(posts[0].content, "Hello world, I'm John!")
        self.assertEqual(posts[1].name, "Jane Doe")
        self.assertEqual(posts[1].email, "jane@example.com")
        self.assertEqual(posts[1].content, "Hello world, I'm Jane!")
