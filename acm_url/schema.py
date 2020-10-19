from acm_url import db
from sqlalchemy.sql import func

class Url(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  vanity = db.Column(db.String(120), index=True, unique=True, nullable=False)
  url = db.Column(db.Text, nullable=False)
  created = db.Column(db.DateTime, server_default=func.now(), nullable=False)
  visit_count = db.Column(db.Integer, default=0, nullable=False)

  def __repr__(self):
    return '<URL {}>'.format(self.vanity)