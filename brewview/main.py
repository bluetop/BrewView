#!/usr/bin/env python
#

import webapp2
import datetime
import time
import json
from google.appengine.ext import ndb
DEFAULT_BEER_NAME = 'default_beer'

SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)
def to_dict(model):
    output = {}
    for key, prop in model.properties().iteritems():
        value = getattr(model, key)
        if value is None or isinstance(value, SIMPLE_TYPES):
            output[key] = value
        elif isinstance(value, datetime.date):
            # Convert date/datetime to MILLISECONDS-since-epoch (JS "new Date()").
            ms = time.mktime(value.utctimetuple()) * 1000
            ms += getattr(value, 'microseconds', 0) / 1000
            output[key] = int(ms)
        elif isinstance(value, db.GeoPt):
            output[key] = {'lat': value.lat, 'lon': value.lon}
        elif isinstance(value, db.Model):
            output[key] = to_dict(value)
        else:
            raise ValueError('cannot encode ' + repr(prop))
    return json.dumps(output)

# We set a parent key on the 'Temps' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent.  However, the write rate should be limited to
# ~1/second.
def beer_key(beer_name=DEFAULT_BEER_NAME):
    """Constructs a Datastore key for a beer entity.

    We use beer_name as the key.
    """
    return ndb.Key('Beer', beer_name)


class Temp(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    beerTemperature = ndb.FloatProperty(indexed=False)
    chillerTemperature = ndb.FloatProperty(indexed=False)
    ambientTemperature = ndb.FloatProperty(indexed=False)
    targetTemperature = ndb.FloatProperty(indexed=False)
    status = ndb.TextProperty(indexed=False)
    name = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)


class BeerTemps(webapp2.RequestHandler):
    def post(self):
        beer_name = self.request.get('name', DEFAULT_BEER_NAME)
        temp = Temp(parent=beer_key(beer_name))
        temp.beerTemperature = float(self.request.get('beer',0))
        temp.chillerTemperature = float(self.request.get('chiller',0))
        temp.ambientTemperature = float(self.request.get('ambient',0))
        temp.targetTemperature  = float(self.request.get('target',0))
        temp.status = self.request.get('state','Unknown')
        temp.name = beer_name

        temp.put()
        self.response.write("<html><body>" + beer_name + "</body></html>");

    def get(self):
        #TODO change to return the 'current' beer only if the beer name is not given
    	beer_name = self.request.get('beer-name', DEFAULT_BEER_NAME)
        self.response.headers['Content-Type'] = 'application/json' 

    	# Ancestor Queries, as shown here, are strongly consistent
        # with the High Replication Datastore. Queries that span
        # entity groups are eventually consistent. If we omitted the
        # ancestor from this query there would be a slight chance that
        # Greeting that had just been written would not show up in a
        # query.
        temp_query = Temp.query(ancestor=beer_key(beer_name)).order(-Temp.date)
        temps = temp_query.fetch(2000000)
        self.response.write('[')
        count = 0;
        for temp in temps:
            if (temp.beerTemperature is None):
                continue
            #self.response.write('<blockquote>%s</blockquote>' % to_dict(temp))
            count = count +1
            self.response.write("{\"beer\":" + str(temp.beerTemperature) + ", ")
            self.response.write("\"chiller\":" + str(temp.chillerTemperature) + ", ")
            self.response.write("\"ambient\":" + str(temp.ambientTemperature) + ", ")
            self.response.write("\"status\":\"" + str(temp.status) + "\", ")
            ms = time.mktime(temp.date.utctimetuple()) * 1000
            ms += getattr(temp.date, 'microseconds', 0) / 1000
            self.response.write("\"date\":" + str(int(ms)) + ", ")
            self.response.write("\"target\":" + str(temp.targetTemperature) + "},\n")
    	self.response.write("{\"end\":" + str(count) + "}]")



class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/beer', BeerTemps),
], debug=True)
