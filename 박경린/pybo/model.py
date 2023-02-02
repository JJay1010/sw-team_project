from pybo.connect_db import db

class Animals(db.Model):
    animal_id = db.Column(db.Integer, primary_key=True)
    # routines = db.relationship('Routine')
    #추후에 추가
    
class Routine(db.Model):
    routine_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    animal_id = db.Column(db.Integer, nullable=False)
    # animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'))
    routine_name= db.Column(db.String(20), nullable=False)
    date= db.Column(db.String(2), nullable=False)
    