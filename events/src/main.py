import cgi
import datetime
import os
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class Event(db.Model):
  what = db.StringProperty()
  when = db.DateTimeProperty()
  date = db.StringProperty()
  time = db.StringProperty()
  where = db.StringProperty(multiline=True)
  desc = db.StringProperty(multiline=True)
  upcoming = db.BooleanProperty()

class MainPage(webapp.RequestHandler):
  def get(self):

    upcomingevents = db.GqlQuery("SELECT * FROM Event WHERE upcoming=:1 ORDER BY when ASC", True)
    for event in upcomingevents:
      event.upcoming=event.when>datetime.datetime.now()-datetime.timedelta(hours=7)
      if(not event.upcoming):
          event.put()

    pastevents = db.GqlQuery("SELECT * FROM Event WHERE upcoming = :1 ORDER BY when DESC", False)

    template_values = {
      'upcomingevents': upcomingevents,
      'pastevents': pastevents,
      }

    path = os.path.join(os.path.dirname(__file__), 'edit.html')
    self.response.out.write(template.render(path, template_values))

class AddEvent(webapp.RequestHandler):
  def post(self):
    w = datetime.datetime.strptime(self.request.get('month')+"/"+self.request.get('day')+"/"+self.request.get('year')+" "+self.request.get('hour')+":"+self.request.get('minute'), "%m/%d/%y %H:%M")
    e = Event(what=self.request.get('what'), when=w, date=w.strftime("%A, %B %d, %Y"), time=w.strftime("%I:%M%p"), where=self.request.get('where'), desc=self.request.get('desc'))
    e.upcoming=True
    e.where=e.where.replace("\n","<br />")
    e.desc=e.desc.replace("\n","<br />")
    e.put()
    self.redirect('/')

class DeleteEvent(webapp.RequestHandler):
  def post(self):
    w = self.request.get('delwithdesc')
    q = db.GqlQuery("SELECT * FROM Event WHERE what = :1", w)
    results = q.fetch(10)
    for result in results:
      result.delete()
    self.redirect('/')

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/sign', AddEvent),
                                      ('/delete', DeleteEvent)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()