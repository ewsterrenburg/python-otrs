"""OTRS :: ticket:: template."""
from otrs.ticket.operations import TicketCreate, TicketGet
from otrs.ticket.operations import TicketSearch, TicketUpdate
from otrs.session.operations import SessionCreate
from otrs.client import WebService


def GenericTicketConnectorSOAP(webservice_name='GenericTicketConnectorSOAP'):
    """Return a GenericTicketConnectorSOAP Webservice object.

    @returns a WebService object with the GenericTicketConnectorSOAP operations
    """
    return WebService(webservice_name, 'http://www.otrs.org/TicketConnector',
                      SessionCreate=SessionCreate(),
                      TicketCreate=TicketCreate(),
                      TicketGet=TicketGet(), TicketSearch=TicketSearch(),
                      TicketUpdate=TicketUpdate())
