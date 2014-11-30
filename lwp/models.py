
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))
    su = db.Boolean()

    def __init__(self, name, username, password):
        self.username = username
        self.password = password
        self.name = name
        self.su = False

    def __repr__(self):
        return '<User %r>' % self.username
