
import os
import random
import time
import json
from sqlalchemy import engine, create_engine
from flask import Flask, Response
import tweepy


app = Flask(__name__)

# For Twitter API
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')

# For GCP Cloud SQL
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
CONNECTION_NAME = os.environ.get("CONNECTION_NAME")

# Needed to avoid cross-domain issues
response_header = {
    'Access-Control-Allow-Origin': '*'
}


@app.route('/', methods = ['GET'])
def post_tweet():

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)

    db = create_engine(
        engine.url.URL(
            drivername = 'postgres+pg8000',
            username = DB_USER,
            password = DB_PASS,
            database = DB_NAME,
            query = {
                'unix_sock': '/cloudsql/{}/.s.PGSQL.5432'.format(
                    CONNECTION_NAME
                )
            }
        ),
        pool_size = 1
    )
    
    with db.connect() as conn:

        # Randomly select an unposted Tweet to post from Postgres tweets table, 
        # then write the time and url of the update to the table
        query_select = '''
        SELECT * 
        FROM tweets
        WHERE tweet_timestamp IS NULL
        ORDER BY random()
        LIMIT 1
        '''

        res = conn.execute(query_select).fetchone()

        if res is None:

            return Response(
                response = json.dumps({'text': 'No more Tweets left.'}),
                headers = response_header
            )
        
        wait_time = random.randint(1, 3)
        time.sleep(60 * wait_time)

        t = api.update_status(status = res.tweet)

        t_timestamp = time.strftime("%Y-%m-%d %H:%M:%S+00", time.gmtime())
        t_url = f"https://twitter.com/{t.user.screen_name}/status/{t.id_str}"

        query_update = f'''
        UPDATE tweets
        SET tweet_timestamp = '{t_timestamp}',
            tweet_url = '{t_url}'
        WHERE 
             id = {res.id}
        '''

        conn.execute(query_update)

    db.dispose()

    return Response(
        json.dumps({'text': f'Tweet published to {t_url}.'}),
        headers = response_header
    ) 


if __name__ == "__main__":
    app.run(
        debug = False, 
        host = '0.0.0.0', 
        port = int(os.environ.get('PORT', 8080))    
    )
