
from decimal import Decimal
import requests
import base64

import os
from dotenv import load_dotenv

from sqlalchemy import Column, Date, MetaData, Numeric, create_engine, String
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base


load_dotenv()

clientId = os.environ.get('clientId')
clientSecret = os.environ.get('clientSecret')


metadata = MetaData()
Base = declarative_base(metadata=metadata)
engine = create_engine(os.environ.get('engine'))
session = Session(engine)


class OptionsInfo(Base):
    __tablename__ = 'optionsInfo'
    symbol = Column(String(256), primary_key=True)
    quoteDate = Column(String(10), primary_key=True)
    frontDelta = Column(Numeric(4,3))
    frontStrike = Column(Numeric)
    backStrike = Column(Numeric)
    spreadPrice = Column(Numeric(6,2))
    spreadWidth = Column(Numeric)
    sentiment = Column(String(30))

    def __init__(self) -> None:
        super().__init__()
        



def requestAuth():
    dataString = clientId+":"+clientSecret
    dataBytes = dataString.encode("utf-8")
    headers = {
        "Authorization" : "Basic " + str(base64.b64encode(dataBytes), "utf-8")
    }
    data = {
        "grant_type" : "client_credentials"
    }
    url = 'https://id.livevol.com/connect/token'

    authResponse = requests.post(url, data=data, headers=headers)
    return authResponse

def getHeaders(authResponse):
    return {
         "Authorization" : "Bearer " + authResponse.json()['access_token']
    }

def requestData(authResponse, symbol: str, optionType: str, quoteDate: str, expirationDate: str):
    url = 'https://api.livevol.com/v1/delayed/allaccess/market/option-and-underlying-quotes?'
    url += "symbol=" + symbol + "&"
    url += "option_type=" + optionType + "&"
    url += "date=" + quoteDate + "&"
    url += "min_expiry=" + expirationDate + "&"
    url += "max_expiry=" + expirationDate
    r = requests.get(url, headers=getHeaders(authResponse))
    return r

def processData(r, quoteDate):
    options = r.json()['options']
    closest = options[0]
    nextOne = options[1]
    for i in range(1, len(options)):
        if abs(options[i]['delta'] - 0.5) < abs(closest['delta'] - 0.5):
            closest = options[i]
            nextOne = options[i+1]

    print(closest)
    print(nextOne)
    front_delta = closest['delta']
    front_strike = closest['strike']
    back_strike = nextOne['strike']
    spread_price = closest['option_ask'] - nextOne['option_bid']
    spread_width = back_strike - front_strike
    sentiment = None
    if spread_price >= 0.51 * spread_width:
        sentiment = "Bullish"
    elif spread_price <= 0.49 * spread_width:
        sentiment = "Bearish"
    else:
        sentiment = "Neutral"

    oi = OptionsInfo()
    oi.symbol = closest['root']
    oi.quoteDate = quoteDate
    oi.frontDelta = front_delta
    oi.frontStrike = front_strike
    oi.backStrike = back_strike
    oi.spreadPrice = spread_price
    oi.spreadWidth = spread_width
    oi.sentiment = sentiment
    session.add(oi)
    session.commit()


def main():
    Base.metadata.create_all(engine, Base.metadata.tables.values(), checkfirst=True)
    authResponse = requestAuth()

    symbols = ["AAPL", "MSFT", "FB", "NFLX", "AMZN", "NVDA", "GOOGL", "KO", "PYPL",
    "MRNA", "BA", "XOM", "GS", "F", "DIS", "PFE", "WFC", "JPM", "C", "BAC", "HD",
    "CVX", "V", "GM", "COST", "CVS", "WMT", "X", "UAL", "T"]
    quoteDate = "2022-03-03"

    for symbol in symbols: 
        r = requestData(authResponse, symbol, "C", quoteDate, "2022-04-14")
        processData(r, quoteDate)

if __name__ == "__main__":
    main()