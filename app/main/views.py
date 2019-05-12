from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    abort,
    redirect,
    url_for,
    current_app,
)
from .models import Post
from app.database import db
from .forms import PostCreateForm


bp = Blueprint('main', __name__, url_prefix ='/main')


def log_error(*args, **kwargs):
    current_app.logger.error(*args, **kwargs)


@bp.route('/', methods=['GET', 'POST'])
def index():
    form = PostCreateForm()
    if form.validate_on_submit():
        post = Post(name=form.name.data, content=form.content.data)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))
    posts = Post.query.all()
    return render_template('main/index.html', form=form, posts=posts)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    post = Post.query.get_or_404(id)
    form = PostCreateForm(name=post.name, content=post.content)
    if form.validate_on_submit():
        post.name = form.name.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post is now edited!')
        return redirect(url_for('main.index'))    
    return render_template('main/edit.html', form=form)


@bp.route('/delete/<int:id>', methods=['GET', 'POST'])    
def delete(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Your post is now deleted!')
    return redirect(url_for('main.index'))
