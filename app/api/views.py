from flask import (Blueprint, request, url_for, current_app, jsonify)
from app.models import Post
from app.database import db
from werkzeug.http import HTTP_STATUS_CODES
from flask_login import current_user, login_required

from flask import g
from flask_httpauth import HTTPBasicAuth
from app.models import User


bp = Blueprint('api', __name__, url_prefix ='/api')

basic_auth = HTTPBasicAuth()

@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return False
    g.current_user = user
    return user.check_password(password)


@basic_auth.error_handler
def basic_auth_error():
    return bad_request(401)


def bad_request(status_code=400, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


@bp.route('/posts/<int:id>', methods=['GET'])
def get_post(id):
    post = Post.query.get_or_404(id)
    data = {
            'id': post.id,
            'timestamp': post.timestamp,
            'user_id': post.user_id,
            'name': post.name,
            'content': post.content
    }
    return jsonify(data)


@bp.route('/posts', methods=['GET'])
def get_posts():
    data = []
    posts = Post.query.all()
    for post in posts:       
        data.append({
                    'id': post.id,
                    'timestamp': post.timestamp,
                    'user_id': post.user_id,
                    'name': post.name,
                    'content': post.content
        })       
    return jsonify(data)


@bp.route('/posts', methods=['POST'])
@basic_auth.login_required
def create_post():
    data = request.get_json() or {}
    if ('name' not in data) or ('content' not in data):
        status_code = 400
        message = 'must include name and content fields'
        return bad_request(status_code, message)
    post = Post()
    post.user_id = g.current_user.id
    post.name = data['name']
    post.content = data['content']
    db.session.add(post)
    db.session.commit()
    data = {
            'id': post.id,
            'user_id': post.user_id,
            'timestamp': post.timestamp,
            'name': post.name,
            'content': post.content
    }
    response = jsonify(data)
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_post', id=post.id)
    return response   


@bp.route('/posts/<int:id>', methods=['PUT'])
@basic_auth.login_required
def update_post(id):
    post = Post.query.get_or_404(id)
    data = request.get_json() or {}
    if ('name' not in data) or ('content' not in data):
        status_code = 400
        message = 'must include name and content fields'
        return bad_request(status_code, message)
    if post.user_id != g.current_user.id:
        status_code = 403
        message = 'Permission error!'
        return bad_request(status_code, message)
    post.name = data['name']
    post.content = data['content']
    db.session.commit()
    data = {
            'id': post.id,
            'timestamp': post.timestamp,
            'user_id': post.user_id,
            'name': post.name,
            'content': post.content
    }
    response = jsonify(data)
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_post', id=post.id)
    return response


@bp.route('/posts/<int:id>', methods=['DELETE'])
@basic_auth.login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post.user_id != g.current_user.id:
        status_code = 403
        message = 'Permission error!'
        return bad_request(status_code, message)
    db.session.delete(post)
    db.session.commit()
    posts = Post.query.all()
    data = []
    for post in posts:       
        data.append({
                     'id': post.id,
                     'timestamp': post.timestamp,
                     'user_id': post.user_id,
                     'name': post.name,
                     'content': post.content
        })
    response = jsonify(data)
    response.status_code = 202
    response.headers['Location'] = url_for('api.get_posts')
    return response

