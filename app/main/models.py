from app.database import db


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), nullable=False, unique=True)
    content = db.Column(db.String(5000), nullable=False)

    def __str__(self):
        return self.name


