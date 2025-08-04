from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {'message': 'Hello World'}

@app.get('/trackers')
async def get_trackers():
    return {'trackers': ['test1', 'test2', 'test3']}

@app.get('/listings')
async def get_listings():
    return {'listings': ['listing1','listing2','listing3']}

@app.get('/alerts')
async def get_alerts():
    return {'alerts': ['alert1','alert2','alert3']}