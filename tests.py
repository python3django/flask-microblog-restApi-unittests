from config import Config
import unittest
from flask import current_app
from app.database import db
from app import create_app
from app.main.models import Post
import json


class ApiPostCase(unittest.TestCase):     
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        p1 = Post(name="name 1", content="content 1")
        p2 = Post(name="name 2", content="content 2")
        db.session.add_all([p1, p2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_all_posts(self):
        response = self.client.get(path='/api/posts', content_type='application/json')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'name 1')
        self.assertEqual(data[0]['content'], 'content 1')
        self.assertEqual(data[1]['name'], 'name 2')
        self.assertEqual(data[1]['content'], 'content 2')
        self.assertNotEqual(data[0]['name'], 'name 2')

    def test_get_single_post(self):
        response = self.client.get(path='/api/posts/2', content_type='application/json')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", data)
        self.assertEqual(data['id'], 2)
        self.assertEqual(data['name'], 'name 2')
        self.assertEqual(data['content'], 'content 2')
        self.assertNotEqual(data['name'], 'name 1')

    def test_create_post(self):
        data = {'name': 'name 3', 'content': 'content 3'}
        response_post = self.client.post(path='/api/posts', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response_post.status_code, 201)
        response_get = self.client.get(path='/api/posts/3', content_type='application/json')
        data = response_get.get_json()
        self.assertEqual(response_get.status_code, 200)
        self.assertIn("name", data)
        self.assertEqual(data['id'], 3)
        self.assertEqual(data['name'], 'name 3')
        self.assertEqual(data['content'], 'content 3')
        self.assertNotEqual(data['name'], 'name 1')

    def test_update_post(self):
        data = {'name': 'updated name 2', 'content': 'updated content 2'}
        response_put = self.client.put(path='/api/posts/2', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response_put.status_code, 201)
        response_get_all = self.client.get(path='/api/posts', content_type='application/json')
        self.assertEqual(len(response_get_all.get_json()), 2)
        self.assertNotEqual(len(response_get_all.get_json()), 3)
        response_get_single = self.client.get(path='/api/posts/2', content_type='application/json')
        data = response_get_single.get_json()
        self.assertEqual(response_get_single.status_code, 200)
        self.assertIn("name", data)
        self.assertEqual(data['id'], 2)
        self.assertEqual(data['name'], 'updated name 2')
        self.assertEqual(data['content'], 'updated content 2')
        self.assertNotEqual(data['name'], 'name 2')

    def test_delete_post(self):
        response_delete = self.client.delete(path='/api/posts/2', content_type='application/json')        
        self.assertEqual(response_delete.status_code, 202)        
        self.assertEqual(len(response_delete.get_json()), 1)
        data_delete = response_delete.get_json()
        self.assertEqual(data_delete[0]['id'], 1)
        self.assertEqual(data_delete[0]['name'], 'name 1')
        self.assertEqual(data_delete[0]['content'], 'content 1')
        self.assertNotEqual(data_delete[0]['name'], 'name 2')
        response_get_all = self.client.get(path='/api/posts', content_type='application/json')
        self.assertEqual(len(response_get_all.get_json()), 1)
        self.assertNotEqual(len(response_get_all.get_json()), 2)
        data_get_all = response_get_all.get_json()
        self.assertEqual(data_get_all[0]['id'], 1)
        self.assertEqual(data_get_all[0]['name'], 'name 1')
        self.assertEqual(data_get_all[0]['content'], 'content 1')
        self.assertNotEqual(data_get_all[0]['name'], 'name 2')
        response_get_single = self.client.get(path='/api/posts/2', content_type='application/json')
        data = response_get_single.get_json()
        self.assertEqual(response_get_single.status_code, 404)
        self.assertNotEqual(response_get_single.status_code, 200)


if __name__ == '__main__':
    unittest.main(verbosity=2)

