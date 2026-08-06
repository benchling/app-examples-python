curl -X POST \
  'https://celleste-biotest.benchling.com/oauth/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=client_credentials' \
  -d 'client_id=YOUR_CLIENT_ID' \
  -d 'client_secret=YOUR_CLIENT_SECRET'

curl -X POST \
  'https://celleste-biotest.benchling.com/api/v2/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=client_credentials' \
  -d 'client_id=YOUR_CLIENT_ID' \
  -d 'client_secret=YOUR_CLIENT_SECRET'

curl -X 'POST' \
  'https://celleste-biotest.benchling.com/api/v2/app-sessions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer API-KEY' \
  -d '{
    "appId": "app_oJ71aUtNif8fQpYe",
    "messages": [],
    "name": "test_session",
    "timeoutSeconds": 2592000
	}'
