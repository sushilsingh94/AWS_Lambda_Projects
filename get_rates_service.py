from zeep import Client

WSDLFILE = 'https://transportationha.rd.cat.com/RM/services/RateRouteGuide.wsdl'

client = Client(WSDLFILE)

class ValidLane:
    def __init__(self, carrierscac, carriername, rate, service, equipmenttype):
        self.carrierscac = carrierscac
        self.carriername = carriername
        self.rate = rate
        self.service = service
        self.equipmenttype = equipmenttype


lane = []

def get_valid_rates(origin, destination, service):
    result = client.service.getRates(1,service,"North America",1,"05/05/2018","ROAD","USA","PEORIA","IL","USA","MORTON","IL",origin,destination)
    
    for rate in result.rateRoute.RRWSRateRoute:
        tempcarrier = rate.carrierType
        templane = rate.validLaneType
        lane.append(ValidLane(tempcarrier.SCACCode, tempcarrier.carrierDescription, templane.chargeAmountInTariffCurrency, templane.serviceCode, templane.equipmentTypeCode))
        validLanes = lane[0:10]
    
    return validLanes





