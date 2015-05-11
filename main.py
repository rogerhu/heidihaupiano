import cgi
import os
import wsgiref.handlers
import Cookie

from google.appengine.api import mail
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


############################
##### Global variables #####
############################


##########################
##### Object classes #####
##########################

class Person(db.Model):
  firstName = db.StringProperty()
  lastName = db.StringProperty()
  emailAddress = db.StringProperty()
  submittedDate = db.DateTimeProperty(auto_now=True)

###########################
##### Handler classes #####
###########################

def administrator(handler_method):
    allowed_emails = ["roger.hu@gmail.com", "et.trinity@gmail.com", "irvintyan@gmail.com" ]

    def check_login(self, *args):
        if self.request.method != 'GET':
            raise webapp.Error('The check_login decorator can only be used for GET '
                           'requests')
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        elif user.email() in allowed_emails:
            handler_method(self, *args)
        else:
            raise webapp.Error("You're not allowed to view these pages")

    return check_login

class MainPage(webapp.RequestHandler):
  def get(self, url):
    acceptedUrls = ["intro", "home", "bio", "concerts", "gallery", "personal", "contact", "submit_msg"]

    if url in acceptedUrls:
      render_page(self, url, { 'tab': 'N/A'})
    else:
      render_page(self, "intro", { 'tab': 'N/A'})

class SubmitPage(webapp.RequestHandler):
  def post(self):
    first = self.request.get('first')
    last = self.request.get('last')
    email = self.request.get('email')

    personRecord = Person()
    personRecord.firstName = first
    personRecord.lastName = last
    personRecord.emailAddress = email

    personRecord.put()
    self.redirect('submit_msg')

class List_Signups(webapp.RequestHandler):
    @administrator
    def get(self):
        records = Person.all()
        records.order('submittedDate')

        record_list = []

# Convert UTC datetime to US Pacific

        from pytz import timezone
        from pytz import utc
        import datetime

        pst = timezone('US/Pacific')
        utc_tz = utc

        for record in records:
          loc_dst = utc_tz.localize(record.submittedDate)
          loc_datetime_posted = loc_dst.astimezone(pst).strftime('%m/%d/%y %I:%M:%S %p')

          record_list += [{"name": " ".join([record.firstName, record.lastName]), "email": record.emailAddress, "datetime_posted": loc_datetime_posted}]

        render_page(self, 'signup_list', {
            'title' : 'Signups',
            'record_list' : record_list,
            })

###########################
##### Utility methods #####
###########################

def render_page(self, pagename, template_values):
    path = os.path.join(os.path.dirname(__file__),
      'html/' + pagename + '.html')
    self.response.out.write(template.render(path, template_values))


########################
##### Main methods #####
########################

application = webapp.WSGIApplication(
  [('/submit', SubmitPage),
   ('/list', List_Signups),
   ('/(.*)', MainPage)],
  debug=True)
