from config import Config
import unittest
from app.database import db
from app import create_app
from app.models import Post, User
import json
from flask_login import current_user


class UserPostModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        u1 = User(username="john", email="john@mail.com")
        u1.set_password('123')
        u2 = User(username="bob", email="bob@mail.com")
        u2.set_password('321')
        db.session.add_all([u1, u2])
        db.session.commit()
        p1 = Post(name="name 1", content="content 1", user_id=u1.id)
        p2 = Post(name="name 2", content="content 2", user_id=u2.id)
        db.session.add_all([p1, p2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='boss')
        u.set_password('12345')
        self.assertFalse(u.check_password('54321'))
        self.assertTrue(u.check_password('12345'))

    def test_user(self):
        users = User.query.all()
        self.assertEqual(len(users), 2)
        u1 = User.query.filter_by(id=1).first()
        u2 = User.query.filter_by(id=2).first()
        self.assertEqual(u1.id, 1)
        self.assertEqual(u2.id, 2)
        self.assertNotEqual(u1.id, 2)
        self.assertEqual(u1.username, 'john')
        self.assertEqual(u2.username, 'bob')
        self.assertEqual(u1.email, "john@mail.com")
        self.assertEqual(u2.email, "bob@mail.com")
        self.assertTrue(u1.check_password('123'))        
        self.assertTrue(u2.check_password('321'))
        self.assertFalse(u1.check_password('321'))
        self.assertFalse(u2.check_password('123'))

    def test_post(self):
        posts = Post.query.all()
        self.assertEqual(len(posts), 2)
        p1 = Post.query.filter_by(id=1).first()
        p2 = Post.query.filter_by(id=2).first()
        self.assertEqual(p1.id, 1)
        self.assertEqual(p2.id, 2)
        self.assertNotEqual(p1.id, 2)
        self.assertEqual(p1.name, 'name 1')
        self.assertEqual(p2.name, 'name 2')
        self.assertEqual(p1.content, "content 1")
        self.assertEqual(p2.content, "content 2")
        self.assertEqual(p1.user_id, 1)
        self.assertEqual(p2.user_id, 2)
        self.assertNotEqual(p2.user_id, 1)


class UserPostCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        u1 = User(username="john", email="john@mail.com")
        u1.set_password('123')
        u2 = User(username="bob", email="bob@mail.com")
        u2.set_password('321')
        db.session.add_all([u1, u2])
        db.session.commit()
        p1 = Post(name="name 1", content="content 1", user_id=u1.id)
        p2 = Post(name="name 2", content="content 2", user_id=u2.id)
        db.session.add_all([p1, p2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_index_without_login(self):
        response = self.client.get(path='/main/', content_type='text/html')
        self.assertEqual(response.status_code, 200)
        data = response.get_data()
        self.assertIn('Flask test project', str(data))
        self.assertIn('post id: 1 user id: 1 time UTC:', str(data))
        self.assertIn('post id: 2 user id: 2 time UTC:', str(data))
        self.assertIn('name 1', str(data))
        self.assertIn('name 2', str(data))
        self.assertIn('content 1', str(data))
        self.assertIn('content 2', str(data))
        self.assertIn('Login', str(data))
        self.assertNotIn('Logout', str(data))

    def test_login_logout(self):      
        with self.client as c:
            username = 'bob'
            password = '321'
            submit = "Sign In"
            # получаем страницу с form в которой есть csrf_token
            response_get = c.get(path='/auth/login', content_type='text/html')
            data = str(response_get.data)
            # получаем csrf_token
            start = data.find('name="csrf_token"') + 39 
            stop = start + 91           
            csrf_token = data[start:stop]
            # логинимся с ошибочным username
            response_post = c.post(
                              path='/auth/login',
                              data={"username": "bad_username", "password": password, "submit": submit, 'csrf_token': csrf_token},
                              follow_redirects=True
            )
            data = response_post.data
            self.assertEqual(response_post.status_code, 200)
            self.assertIn('Invalid username or password', str(data))
            self.assertNotIn('Logout', str(data))  
            self.assertIn('Login', str(data))
            # логинимся с ошибочным password
            response_post = c.post(
                              path='/auth/login',
                              data={"username": username, "password": "bad_password", "submit": submit, 'csrf_token': csrf_token},
                              follow_redirects=True
            )
            data = response_post.data
            self.assertEqual(response_post.status_code, 200)
            self.assertIn('Invalid username or password', str(data))
            self.assertNotIn('Logout', str(data))  
            self.assertIn('Login', str(data))
            # логинимся с верными данными
            response_post = c.post(
                              path='/auth/login',
                              data={"username": username, "password": password, "submit": submit, 'csrf_token': csrf_token},
                              follow_redirects=True
            )
            self.assertEqual(response_post.status_code, 200)
            self.assertEqual(current_user.username, username)
            data = response_post.data
            self.assertIn('Logout', str(data))  
            self.assertNotIn('Login', str(data))          
            self.assertIn('post id: 1 user id: 1 time UTC:', str(data))
            self.assertIn('post id: 2 user id: 2 time UTC:', str(data))
            self.assertIn('name 1', str(data))
            self.assertIn('name 2', str(data))
            self.assertIn('content 1', str(data))
            self.assertIn('content 2', str(data))
            self.assertIn('Edited post', str(data))
            self.assertIn('Delete post', str(data))
            # logout
            response_logout = c.get(path='/auth/logout', content_type='text/html', follow_redirects=True)
            self.assertEqual(response_logout.status_code, 200)
            data = response_logout.data
            self.assertNotIn('Logout', str(data))  
            self.assertIn('Login', str(data))          
            self.assertNotIn('Edited post', str(data))
            self.assertNotIn('Delete post', str(data))         

    def test_register(self):      
        with self.client as c:
            username = 'boss'
            password = '789'
            password2 = password
            submit = 'Register'
            email = 'boss@boss.com'
            # получаем страницу с form в которой есть csrf_token
            response_register_get = c.get(path='/auth/register', content_type='text/html')            
            data = str(response_register_get.data)
            self.assertIn('<h1>Register</h1>', data)
            # получаем csrf_token
            start = data.find('name="csrf_token"') + 39 
            stop = start + 91           
            csrf_token = data[start:stop]
            # регистрируем нового пользователя
            response_register_post = c.post(
                              path='/auth/register',
                              data={
                                    "username": username, 
                                    "password": password, 
                                    "password2": password2, 
                                    "submit": submit, 
                                    "csrf_token": csrf_token, 
                                    "email": email},
                              follow_redirects=True
            )
            data = response_register_post.data
            self.assertEqual(response_register_post.status_code, 200)
            self.assertIn('Congratulations, you are now a registered user!', str(data))
            # логинимся с данными только что созданного пользователя
            submit = "Sign In"
            response_login_post = c.post(
                              path="/auth/login",
                              data={"username": username, "password": password, "submit": submit, "csrf_token": csrf_token},
                              follow_redirects=True
            )
            self.assertEqual(response_login_post.status_code, 200)
            self.assertEqual(current_user.username, username)
            data = response_login_post.data
            self.assertIn('Logout', str(data))  
            self.assertNotIn('Login', str(data))          
            self.assertIn('post id: 1 user id: 1 time UTC:', str(data))
            self.assertIn('post id: 2 user id: 2 time UTC:', str(data))
            self.assertIn('name 1', str(data))
            self.assertIn('name 2', str(data))
            self.assertIn('content 1', str(data))
            self.assertIn('content 2', str(data))

   
    def test_create_post(self):      
        with self.client as c:
            username = 'bob'
            password = '321'
            submit = "Sign In"
            # получаем страницу с form в которой есть csrf_token
            response_get = c.get(path='/auth/login', content_type='text/html')
            data = str(response_get.data)
            # получаем csrf_token
            start = data.find('name="csrf_token"') + 39 
            stop = start + 91           
            csrf_token = data[start:stop]
            # проходим процедуру аутентификации
            response_post = c.post(
                              path='/auth/login',
                              data={"username": username, "password": password, "submit": submit, 'csrf_token': csrf_token},
                              follow_redirects=True
            )
            self.assertEqual(response_post.status_code, 200)
            self.assertEqual(current_user.username, username)
            data = response_post.data
            self.assertIn('Logout', str(data))
        # создаем новый пост
        name = 'bob post name'
        content = 'bob post content'
        submit = "Submit"
        response_create = self.client.post(
                                 path='/main/', 
                                 data={"name": name, "content": content, "submit": submit, 'csrf_token': csrf_token},
                                 follow_redirects=True
        )                  
        self.assertEqual(response_create.status_code, 200)
        data = str(response_create.data)
        self.assertIn('Logout, {}'.format(username), data)
        self.assertNotIn('Login', data)   
        self.assertIn('Your post is now live!', data)       
        self.assertIn('post id: 1 user id: 1 time UTC:', data)
        self.assertIn('post id: 2 user id: 2 time UTC:', data)
        self.assertIn('post id: 3 user id: 2 time UTC:', data)
        self.assertIn('name 1', data)
        self.assertIn('name 2', data)
        self.assertIn('bob post name', data)
        self.assertIn('content 1', data)
        self.assertIn('content 2', data)
        self.assertIn('bob post content', data)
        self.assertIn('Edited post', data)
        self.assertIn('Delete post', data)        
        posts = Post.query.all()
        self.assertEqual(len(posts), 3)

    def test_edit_post(self):      
        with self.client as c:
            username = 'bob'
            password = '321'
            submit = "Sign In"
            # получаем страницу с form в которой есть csrf_token
            response_get = c.get(path='/auth/login', content_type='text/html')
            data = str(response_get.data)
            # получаем csrf_token
            start = data.find('name="csrf_token"') + 39 
            stop = start + 91           
            csrf_token = data[start:stop]
            # пробуем отредактировать пост с id=2 в качестве анонимного пользователя 
            name = 'anonymous edit name 2'
            content = 'anonymous edit content 2'
            submit = "Submit"
            response_anonymous_edit = c.post(
                                     path='/main/edit/2', 
                                     data={"name": name, "content": content, "submit": submit, 'csrf_token': csrf_token},
                                     follow_redirects=True
            )                  
            self.assertEqual(response_anonymous_edit.status_code, 200)
            data = str(response_anonymous_edit.data)
            self.assertNotIn('Logout, {}'.format(username), data)
            self.assertIn('Login', data)   
            self.assertIn('Please log in to access this page.', data)       
            self.assertNotIn('name 1', data)
            self.assertNotIn('name 2', data)
            self.assertNotIn('anonymous edit name 2', data)
            self.assertNotIn('content 1', data)
            self.assertNotIn('content 2', data)
            self.assertNotIn('anonymous edit content 2', data)
            self.assertNotIn('Edited post', data)
            self.assertNotIn('Delete post', data)        
            post = Post.query.filter_by(id=2).first()
            self.assertIn('name 2', post.name)
            self.assertIn('content 2', post.content)
            self.assertNotIn(name, post.name)
            self.assertNotIn(content, post.content)
            # проходим процедуру аутентификации
            response_post = c.post(
                              path='/auth/login',
                              data={"username": username, "password": password, "submit": submit, 'csrf_token': csrf_token},
                              follow_redirects=True
            )
            self.assertEqual(response_post.status_code, 200)
            self.assertEqual(current_user.username, username)
            data = response_post.data
            self.assertIn('Logout', str(data))
        # пробуем отредактировать пост с id=1, который не принадлежит нашему аутентифицированному пользователю 
        name = 'bad edit name 1'
        content = 'bad edit content 1'
        submit = "Submit"
        response_bad_edit = self.client.post(
                                 path='/main/edit/1', 
                                 data={"name": name, "content": content, "submit": submit, 'csrf_token': csrf_token},
                                 follow_redirects=True
        )                  
        self.assertEqual(response_bad_edit.status_code, 200)
        data = str(response_bad_edit.data)
        self.assertIn('Logout, {}'.format(username), data)
        self.assertNotIn('Login', data)   
        self.assertIn('Permission error!', data)
        self.assertNotIn('Your post is now edited!', data)       
        self.assertNotIn(name, data)
        self.assertNotIn(content, data)
        post = Post.query.filter_by(id=1).first()
        self.assertNotEqual(post.name, name)
        self.assertNotEqual(post.content, content)
        self.assertEqual(post.name, "name 1")
        self.assertEqual(post.content, "content 1")
        # редактируем пост с id=2, который принадлежит нашему аутентифицированному пользователю 
        name = 'edit name 2'
        content = 'edit content 2'
        submit = "Submit"
        response_edit = self.client.post(
                                 path='/main/edit/2', 
                                 data={"name": name, "content": content, "submit": submit, 'csrf_token': csrf_token},
                                 follow_redirects=True
        )                  
        self.assertEqual(response_edit.status_code, 200)
        data = str(response_edit.data)
        self.assertIn('Logout, {}'.format(username), data)
        self.assertNotIn('Login', data)   
        self.assertIn('Your post is now edited!', data)       
        self.assertIn('post id: 1 user id: 1 time UTC:', data)
        self.assertIn('post id: 2 user id: 2 time UTC:', data)
        self.assertNotIn('post id: 3 user id: 2 time UTC:', data)
        self.assertIn('name 1', data)
        self.assertIn('edit name 2', data)
        self.assertIn('content 1', data)
        self.assertIn('edit content 2', data)
        self.assertIn('Edited post', data)
        self.assertIn('Delete post', data)        
        posts = Post.query.all()
        self.assertEqual(len(posts), 2)

    def test_delete_post(self):
        # пробуем удалить пост с id=2 в качестве неаутентифицированного пользователя
        response_anonymous_delete = self.client.get(path='/main/delete/2', follow_redirects=True)
        self.assertEqual(response_anonymous_delete.status_code, 200)
        data = str(response_anonymous_delete.data)
        self.assertIn('Login', data)
        self.assertIn('Please log in to access this page.', data)
        posts = Post.query.all()
        self.assertEqual(len(posts), 2)       
        # аутентифицируемся
        with self.client as c:
            username = 'bob'
            password = '321'
            submit = "Sign In"
            # получаем страницу с form в которой есть csrf_token
            response_get = c.get(path='/auth/login', content_type='text/html')
            data = str(response_get.data)
            # получаем csrf_token
            start = data.find('name="csrf_token"') + 39 
            stop = start + 91           
            csrf_token = data[start:stop]
            # логинимся
            response_post = c.post(
                              path='/auth/login',
                              data={"username": username, "password": password, "submit": submit, 'csrf_token': csrf_token},
                              follow_redirects=True
            )
            data = response_post.data
            self.assertEqual(response_post.status_code, 200)
            data = str(response_post.data)
            self.assertIn('Logout, {}'.format(username), data)
            self.assertNotIn('Login', data)
            self.assertIn('name 1', data)
            self.assertIn('name 2', data)
            self.assertIn('content 1', data)
            self.assertIn('content 2', data)
            self.assertIn('Edited post', data)
            self.assertIn('Delete post', data)
            # пробуем удалить пост с id=1 который не пренадлежить нашему пользователю
            response_authenticated_bad_delete = self.client.get(path='/main/delete/1', follow_redirects=True)
            self.assertEqual(response_authenticated_bad_delete.status_code, 200)
            data = str(response_authenticated_bad_delete.data)
            self.assertIn('Logout, {}'.format(username), data)
            self.assertNotIn('Login', data)
            self.assertIn('name 1', data)
            self.assertIn('name 2', data)
            self.assertIn('content 1', data)
            self.assertIn('content 2', data)
            self.assertIn('Permission error!', data)
            self.assertNotIn('Your post is now deleted!', data)
            posts = Post.query.all()
            self.assertEqual(len(posts), 2)
            # удаляем пост с id=2 который принадлежит нашему пользователю
            response_authenticated_delete = self.client.get(path='/main/delete/2', follow_redirects=True)
            self.assertEqual(response_authenticated_delete.status_code, 200)
            data = str(response_authenticated_delete.data)
            self.assertIn('Logout, {}'.format(username), data)
            self.assertNotIn('Login', data)
            self.assertIn('name 1', data)
            self.assertNotIn('name 2', data)
            self.assertIn('content 1', data)
            self.assertNotIn('content 2', data)
            self.assertIn('Your post is now deleted!', data)
            posts = Post.query.all()
            self.assertEqual(len(posts), 1)



class ApiPostCase(unittest.TestCase):     
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
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

