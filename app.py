import keys 
import requests
#from auth import sp 

AUTH_URL = 'https://accounts.spotify.com/api/token'

# POST
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': keys.CLIENT_ID,
    'client_secret': keys.CLIENT_SECRET,
})

# convert the response to JSON
auth_response_data = auth_response.json()
print(auth_response_data)

# save the access token
access_token = auth_response_data['access_token']


headers_old = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

headers = {'Authorization': 'Bearer BQC1irlDYxzgKVau5u0wtPBuHUM1eHs-etTz09KNNbzRGENY-jyTXQJ_L0c-CtVxgnxtiZ-j4UQatHelferqs12XsQnFrjLWRWW-Cu4tgJwetE3TTWeHpV7TJ9TAN9Hx5FeWoSAbNMt9gchUuBLR_5dhvZ-Cidi9bzyCujvOslKjmneH_M7IE0zqeBNAeYf8pv9lmSizynUYCy8ZMHD9H3paLxgPQy4EKTez1qMxhrQifg'}

print("old", headers_old)
print("new", headers)

BASE_URL = 'https://api.spotify.com/v1/'

r = requests.get(BASE_URL + 'me/top/tracks', headers=headers)
print(r)