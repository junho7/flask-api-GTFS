from . import db

db.metadata.reflect(bind=db.engine)

class Agency(db.Model):
    __table__ = db.Model.metadata.tables['agency']
    
class Routes(db.Model):
    __table__ = db.Model.metadata.tables['routes']
    
class Stop_times(db.Model):
    __table__ = db.Model.metadata.tables['stop_times']
    
class Calendar_dates(db.Model):
    __table__ = db.Model.metadata.tables['calendar_dates']
    
class Calendar(db.Model):
    __table__ = db.Model.metadata.tables['calendar']
    
class Shapes(db.Model):
    __table__ = db.Model.metadata.tables['shapes']
    
class Stops(db.Model):
    __table__ = db.Model.metadata.tables['stops']
    
class Trips(db.Model):
    __table__ = db.Model.metadata.tables['trips']
    