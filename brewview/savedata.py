
from google.appengine.ext import ndb

DEFAULT_BEER_NAME = 'default_beer'

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
    temp = ndb.(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


 class BeerTemps(webapp2.RequestHandler):
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        beer_name = self.request.get('beer', DEFAULT_BEER_NAME)
        temp = Temp(parent=beer_key(beer_name))
        temp.temp = self.request.get('temp')
        temp.put()
        self.response.write("<html><body>OK</body></html>");

    def get(self):
    	self.response.write('<html><body>')
    	beer_name = self.request.get('beer_name', DEFAULT_BEER_NAME)

    	# Ancestor Queries, as shown here, are strongly consistent
        # with the High Replication Datastore. Queries that span
        # entity groups are eventually consistent. If we omitted the
        # ancestor from this query there would be a slight chance that
        # Greeting that had just been written would not show up in a
        # query.
        temp_query = Temp.query(
            ancestor=beer_key(beer_name)).order(-Temp.date)
        temps = temp_query.fetch(10)
        for temp in temps:
        	 self.response.write("temp: " % temp.temp % "<br/>")
    	self.response.write('</body></html>')



