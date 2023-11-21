import requests
import json
from hashlib import md5


def get_journey(from_location,to_location,depature,arrival=None):
    print(f'Quering get_journey with depature: {depature}, from {from_location}, to {to_location}')

    """Uses hafasClient.journeys() to find journeys from A (from) to B (to) 

    Args:
        from_location : the depature station as ID
        to_location : the arrival station as ID
        depature : depature date/time
        arrival (String, optional):  journeys arriving at this date/time Defaults to None.

    Returns:
        JSON: That containing informations about the trip
    """
    BASE_URL = 'https://v6.db.transport.rest'
    endpoint= '/journeys'
    params = {
        "from":from_location,
        "to":to_location,
        "depature": depature,
        "arrival":arrival
    }
    response = requests.get(BASE_URL+endpoint, params=params)

    # Check if the response was successful
    if response.status_code == 200:
        return response.json()
    else:
        return f'Error during calling the get_jouney function: {response.json()}'
    
def get_actual_time_and_date(n):
    endpoint = 'http://worldtimeapi.org/api/timezone/Europe/London'
    response = requests.get(endpoint)
    # Check if the response was successful
    if response.status_code == 200:
        return response.json()
    else:
        return "Error during calling the get_jouney function"
    
def _checksum(data):
    SALT = 'bdI8UVj40K5fvxwf'
    saltedData = data+SALT
    saltedDataEncoded = saltedData.encode('utf-8')
    return md5(saltedDataEncoded).hexdigest()

def get_best_prices(depature,from_location, to_location,journey_time=120000):
    print(f'Quering best_prices with depature: {depature}, from {from_location}, to {to_location}')
    """Returning the cheapest prices (Sparpreis) for a journey

    Args:
        depature : date+time
        from_location : the depature station as ID
        to_location : the depature station as ID
        journey_time (int, optional):. Defaults to 120000.

    Returns:
        string: time + price
    """
    url = "https://reiseauskunft.bahn.de/bin/mgate.exe"

    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; Pixel 3 Build/PI)",
        "Content-Type": "application/json;charset=UTF-8"
        }

    bestPriceSearchRequest = {
        "auth": {"aid": "n91dB8Z77MLdoR0K", "type": "AID"},
        "client": {"id": "DB", "name": "DB Navigator", "os": "Android 9", "res": "1080x2028", "type": "AND", "ua": "Dalvik/2.1.0 (Linux; U; Android 9; Pixel 3 Build/PI)", "v": 22080000},
        "ext": "DB.R22.04.a",
        "formatted": False,
        "lang": "eng",
        "svcReqL": [{
            "cfg": {"polyEnc": "GPA", "rtMode": "HYBRID"},
            "meth": "BestPriceSearch",
            "req": {
                "outDate": f"{depature}",
                "outTime": f"{journey_time}",
                "depLocL": [{
                    "extId": f"{from_location}",
                    "type": "S"
                }],
                "arrLocL": [
                    {
                        "extId": f"{to_location}",
                        "type": "S"
                    }],
                "getPasslist": True,
                "getPolyline": True,
                "jnyFltrL": [{
                    "mode": "BIT",
                    "type": "PROD",
                    "value": "11111111111111"
                }],
                "trfReq": {
                    "cType": "PK",
                    "jnyCl": 2,
                    "tvlrProf": [{"type": "E"}]
                }
            }
        }],
        "ver": "1.15"
    }

    bestPriceSearchRequestStr = json.dumps(bestPriceSearchRequest, ensure_ascii=False, separators=(',', ':'))
    bestPriceSearchRequestEncoded = bestPriceSearchRequestStr.encode('utf-8')

    reqChecksum = _checksum(bestPriceSearchRequestStr)

    params = {
        'checksum': reqChecksum,
    }

    response = requests.post(url, params=params, headers=headers, data=bestPriceSearchRequestEncoded)
    bestPrices = [(bestPrice['toTime'], bestPrice['bestPrice']['amount']) for bestPrice in response.json()['svcResL'][0]['res']['outDaySegL']]

    return bestPrices
