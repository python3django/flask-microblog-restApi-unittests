from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostCreateForm(FlaskForm):
    name = StringField(
                        'Name',
                        [DataRequired(message="This field is required")],
                        description="Name of the entity"
    )
    content = TextAreaField(
                        'Content',
                        [DataRequired(message="This field is required")],
                        description="Content of the entity"
    )
    submit = SubmitField('Submit')
