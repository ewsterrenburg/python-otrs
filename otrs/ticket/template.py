from .operations import SessionCreate,TicketCreate,TicketGet,TicketSearch,TicketUpdate
from ..client import WebService

def GenericTicketConnectorSOAP(webservice_name='GenericTicketConnectorSOAP'):
    return WebService(webservice_name, 'http://www.otrs.org/TicketConnector', SessionCreate=SessionCreate(),TicketCreate=TicketCreate(),TicketGet=TicketGet(),TicketSearch=TicketSearch(),TicketUpdate=TicketUpdate())