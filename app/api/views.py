from flask import (Blueprint, request, url_for, current_app, jsonify)
from app.main.models import Post
from app.database import db
from werkzeug.http import HTTP_STATUS_CODES


bp = Blueprint('api', __name__, url_prefix ='/api')


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
                    'name': post.name,
                    'content': post.content
        })       
    return jsonify(data)


@bp.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json() or {}
    if ('name' not in data) or ('content' not in data):
        status_code = 400
        message = 'must include name and content fields'
        return bad_request(status_code, message)
    post = Post()
    post.name = data['name']
    post.content = data['content']
    db.session.add(post)
    db.session.commit()
    data = {
            'id': post.id,
            'name': post.name,
            'content': post.content
    }
    response = jsonify(data)
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_post', id=post.id)
    return response   

@bp.route('/posts/<int:id>', methods=['PUT'])
def update_post(id):
    post = Post.query.get_or_404(id)
    data = request.get_json() or {}
    if ('name' not in data) or ('content' not in data):
        status_code = 400
        message = 'must include name and content fields'
        return bad_request(status_code, message)
    post.name = data['name']
    post.content = data['content']
    db.session.commit()
    data = {
            'id': post.id,
            'name': post.name,
            'content': post.content
    }
    response = jsonify(data)
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_post', id=post.id)
    return response


@bp.route('/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    posts = Post.query.all()
    data = []
    for post in posts:       
        data.append({
                    'id': post.id,
                    'name': post.name,
                    'content': post.content
        })
    response = jsonify(data)
    response.status_code = 202
    response.headers['Location'] = url_for('api.get_posts')
    return response

