from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo


def uniqueUsernameCheck(form, field):
    import routes
    routes.cur.execute('SELECT Username FROM User WHERE username=%s', [field.data])
    matchingUsername = routes.cur.fetchone()
    if (matchingUsername is not None):
        raise ValidationError("Username is already registered")


def uniqueEmailCheck(form, field):
    import routes
    routes.cur.execute('SELECT Email FROM User WHERE email=%s', [field.data])
    matchingEmail = routes.cur.fetchone()
    if (matchingEmail is not None):
        raise ValidationError("Email is already registered")


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired("Please enter an registered email.")])
    password = PasswordField('Password',  validators=[DataRequired("Please enter a valid password.")])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    user = StringField('Username', validators=[DataRequired("Please enter a user name."), uniqueUsernameCheck])
    email = StringField('Email',  validators=[DataRequired("Please enter an email."),
        Email("Please enter a valid email"), uniqueEmailCheck])
    password = PasswordField('Password',  validators=[DataRequired("Please enter a password."),
        Length(min=8, max = -1, message="Password must be at least 8 characters"),
        EqualTo('confirmPassword', "Passwords must match")])
    confirmPassword = PasswordField('Confirm Password',  validators=[DataRequired("Please confirm your password.")])
    type = SelectField('User Type', choices=[('OWNER', 'Owner'), ('VISITOR', 'Visitor')],
                       validators=[DataRequired("Please enter a valid user type.")])
    submit = SubmitField('Register')

class AddPropertyForm(FlaskForm):
    propertyName = StringField('Name', validators=[DataRequired("Must enter a unique property name")])
    streetAddress = StringField('Street', validators=[DataRequired("Must enter a street address")])
    city = StringField('City', validators=[DataRequired("Must enter a valid city")])
    zip = StringField('Zip', validators=[DataRequired("Must enter a valid zip code")])
    acres = StringField('Acres', validators=[DataRequired("Must enter a valid size")])
    public = SelectField('Public', choices=[('YES', 'Yes'), ('NO', 'No')],validators=[DataRequired()])
    commercial = SelectField('Comm', choices=[('YES', 'Yes'), ('NO', 'No')], validators=[DataRequired()])
    propertyType = SelectField('Type',
                               choices=[('FARM', 'Farm'), ('GARDEN', 'Garden'), ('ORCHARD', 'Orchard')],
                               validators=[DataRequired()])
    animal = SelectField('Animal')
    crop = SelectField('Crop')
    vegetable = SelectField('Vegetable')
    flower = SelectField('Flower')
    fruit = SelectField('Fruit')
    nut = SelectField('Nut')
    submit = SubmitField('Add Property')
    stringDummy = StringField('')
    selectDummy = SelectField('', choices=[('', '')])

class ManagePropertyForm(FlaskForm):
    # edit property information
    propertyName = StringField('Name')
    streetAddress = StringField('Address')
    city = StringField('City')
    zip = StringField('Zip')
    acres = StringField('Size')
    public = SelectField('Public', choices=[('-', '-'), ('YES', 'Yes'), ('NO', 'No')])
    commercial = SelectField('Comm', choices=[('-', '-'), ('YES', 'Yes'), ('NO', 'No')])

    # add new items
    animal = SelectField('Animal')
    crop = SelectField('Crop')
    vegetable = SelectField('Vegetable')
    flower = SelectField('Flower')
    fruit = SelectField('Fruit')
    nut = SelectField('Nut')

    # delete items
    deleteName = SelectField('Name')

    # request item approval
    requestName = StringField('Name')
    requestType = SelectField('Type')

    # delete property
    deleteProperty = SelectField('Delete', choices=[('-', '-'), ('YES', 'Yes'), ('NO', 'No')])

    submit = SubmitField('Submit')