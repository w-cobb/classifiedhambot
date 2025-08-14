from fastapi import Depends, Response, FastAPI, status
from dotenv import load_dotenv
import psycopg
import logging
import os

load_dotenv()
user = os.getenv("DBUSER")
password = os.getenv("DBPASSWORD")
dbname = os.getenv("DBNAME")
dbhost = os.getenv("DBHOST")
dbport = os.getenv("DBPORT")

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(filename="api.log", encoding="utf-8", 
                    format="%(asctime)s %(levelname)-8s: %(message)s", 
                    datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)

print(f'Attempting to connect to host: {dbhost}')
conn_string = f"dbname={dbname} user={user} password={password} host={dbhost} port={dbport}"

app = FastAPI()

async def get_db_conn():
    async with await psycopg.AsyncConnection.connect(conn_string) as conn:
        yield conn

@app.get("/")
async def root():
    return {'message': 'Hello World'}

# ------------------ #
# Trackers API Calls #
# ------------------ #

# Get all trackers for a specific user
# Usage:    GET /trackers/?uname=<username>
@app.get('/trackers', status_code=status.HTTP_200_OK)
async def get_trackers(uname: str | None = None, conn = Depends(get_db_conn)):
    async with conn.cursor() as cur:
        if uname != None:
            await cur.execute("select * from trackers where username = %s", (uname,))
        else:
            await cur.execute('select * from trackers')
        result = await cur.fetchall()
        return result

# Add new tracker
# Usage:    POST /trackers/?uname=<username>&iname=<item_name>
@app.post('/trackers', status_code=status.HTTP_201_CREATED)
async def add_tracker(uname: str, iname: str, response: Response, conn = Depends(get_db_conn)):
    async with conn.cursor() as cur:
        await cur.execute("insert into trackers (username, item_name) values (%s, %s) on conflict do nothing", (uname, iname))
        if cur.rowcount == 1:
            return {'message': "Successfully added new tracker."}
        else:
            response.status_code = status.HTTP_409_CONFLICT
            return {'message': "A tracker already exists for that item."}
        
# Delete a tracker
# Usage:    DELETE /trackers/?uname=<username>&id=<id>
@app.delete('/trackers', status_code=status.HTTP_200_OK)
async def del_tracker(response: Response, uname: str | None = None, id: int | None = None, prune: bool | None = None, age: int | None = None,  conn = Depends(get_db_conn)):
    async with conn.cursor() as cur:
        if uname != None and id != None:
            await cur.execute('delete from trackers where username = %s and id = %s', (uname,id))
            if cur.rowcount != 0:
                return {'message': f"Successfully deleted tracker {id}"}
            else:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {'message': 'Tracker not found'}
        elif prune == True and age >= 10:
            await cur.execute('delete from trackers where to_timestamp(created_at) < now() - interval \'%s days\'', (age,))
            return {'message': f'Successfully pruned {cur.rowcount} trackers'}
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'message': "Invalid request format"}

# ------------------ #
# Listings API Calls #
# ------------------ #

# Get all listings
@app.get('/listings', status_code=status.HTTP_200_OK)
async def get_listings(conn = Depends(get_db_conn)):
    async with conn.cursor() as cur:
        await cur.execute("select * from listings")
        result = await cur.fetchall()
        return result
    
# Add a listing
# Usage:    POST /listings/?iname-<item_name>&iurl=<item_url>
@app.post('/listings', status_code=status.HTTP_201_CREATED)
async def add_listing(iname: str, iurl: str, response: Response, conn = Depends(get_db_conn)):
    async with conn.cursor() as cur:
        await cur.execute('insert into listings (item_name, item_url) values (%s, %s) on conflict do nothing', (iname, iurl))
        if cur.rowcount == 1:
            return {'message': f"Successfully added listing for {iname}."}
        else:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {'message': 'Something went wrong when adding the listing.'}
    
# Delete a listing
@app.delete('/listings/', status_code=status.HTTP_200_OK)
async def del_listing(response: Response, id: int | None = None, prune: bool | None = None, age: int | None = None, conn = Depends(get_db_conn)):
    async with conn.cursor() as cur:
        if id != None:
            cur.execute('delete from listings where id = %s', (id,))
            if cur.rowcount == 1:
                return {'message': f'Listing {id} deleted.'}
            else:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {'message': f"No listing with id {id} found."}
        elif prune == True and age != None and age >= 10:
            cur.execute('delete from listings where to_timestamp(created_at) < now() - interval \"%s days\"', (age,))
            return {'message': f'{cur.rowcount} listings deleted',}
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'message': 'Invalid request format'}
            

# ---------------- #
# Alerts API Calls #
# ---------------- #

# Get all alerts
@app.get('/alerts')
async def get_alerts(triggered: bool | None = None, conn = Depends(get_db_conn)):
    async with conn.cursor() as cur:
        if triggered != None:
            await cur.execute("select * from alerts where triggered = %s", (triggered,))
        else:
            await cur.execute("select * from alerts")
        result = await cur.fetchall()
        return result
    
# Add an alert
@app.post('/alerts', status_code=status.HTTP_201_CREATED)
async def add_alert(tid: int, lid: int, uname: str, response: Response, conn = Depends(get_db_conn)):
    async with conn.cursor() as cur:
        if tid >= 0 and lid >= 0 and uname != '':
            cur.execute('insert into alerts (tracker_id, listing_id, username) values (%s, %s, %s) on conflict do nothing', (tid, lid, uname))
            return {'message': f'Alert successfully added for Tracker: {tid}, Listing: {lid}, Username: {uname}'}
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'message': 'Invalid request format'}

# Update an alert when triggered
@app.put('/alerts', status_code=status.HTTP_200_OK)
async def update_alert(id: int, response: Response, conn = Depends(get_db_conn)):
    async with conn.cursor() as cur:
        cur.execute('update alerts set triggered = true where id = %s', (id,))
        if cur.rowcount == 1:
            return {'message': f'Updated alert {id}'}
        else:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {'message': f'Not found'}
        
# Delete alerts
@app.delete('alerts', status_code=status.HTTP_200_OK)
async def del_alert(response: Response, id: int | None = None, prune: bool | None = None, age: int | None = None, conn = Depends(get_db_conn)):
    async with conn.cursor() as cur:
        if id != None:
            cur.execute('delete from alerts where id = %s', (id,))
            if cur.rowcount == 1:
                return {'message': f'Alert {id} deleted.'}
            else:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {'message': f"No alert with id {id} found."}
        elif prune == True and age != None and age >= 10:
            cur.execute('delete from alerts where to_timestamp(created_at) < now() - interval \"%s days\"', (age))
            return {'message': f'{cur.rowcount} alerts deleted',}
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'message': 'Invalid request format'}