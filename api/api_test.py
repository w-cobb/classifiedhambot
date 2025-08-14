from fastapi.testclient import TestClient
from urllib.parse import quote_plus
import os

os.environ["DBHOST"] = 'localhost'
os.environ['DBPORT'] = '5431'

from api import app

client = TestClient(app)

uname = 'testuser3'
iname = 'test_item_4'

def test_get_all_trackers():
    response = client.get('/trackers')
    assert response.status_code == 200
    
def test_get_all_trakers_by_user():
    response = client.get('/trackers?uname=testuser1')
    assert response.status_code == 200
    
def test_add_tracker():
    query = quote_plus(f'uname={uname}&iname={iname}', safe='&=')
    response = client.post(f'/trackers?{query}')
    assert response.status_code == 201
    
def test_add_tracker_fail():
    query = quote_plus(f'uname={uname}',safe='&=')
    response = client.post(f'/trackers?{query}')
    assert response.status_code == 422