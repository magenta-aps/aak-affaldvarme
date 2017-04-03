import zeep
from requests import Session
from suds.client import Client
from zeep.transports import Transport


def main():
    url ="https://exttest.serviceplatformen.dk/service/CVROnline/CVROnline/1"
    #client = Client(url)
    #print client

    session = Session()
    session.cert = ('./magenta_ava_2017-03.pem', './key')

    transport = Transport(session=session)

    client = zeep.Client(wsdl=url, transport=transport)
    print client

if __name__ == "__main__":
    main()