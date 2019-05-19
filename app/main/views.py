from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for,
)
from app.database import db
from .forms import PostCreateForm
from app.models import Post
from flask_login import current_user, login_required
from sqlalchemy import desc


bp = Blueprint('main', __name__, url_prefix='/main')


@bp.route('/', methods=['GET', 'POST'])
def index():
    form = PostCreateForm()
    if form.validate_on_submit():
        post = Post(
                    user_id=current_user.id,
                    name=form.name.data,
                    content=form.content.data
        )
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))
    posts = Post.query.order_by(desc(Post.timestamp)).all()
    return render_template('main/index.html', form=form, posts=posts)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    form = PostCreateForm(
                    name=post.name,
                    content=post.content
    )
    if form.validate_on_submit():
        if current_user.id == post.user_id:
            post.name = form.name.data
            post.content = form.content.data
            db.session.commit()
            flash('Your post is now edited!')
        else:
            flash('Permission error!')
        return redirect(url_for('main.index'))
    return render_template('main/edit.html', form=form)


@bp.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    if current_user.id == post.user_id:
        db.session.delete(post)
        db.session.commit()
        flash('Your post is now deleted!')
    else:
        flash('Permission error!')
    return redirect(url_for('main.index'))
