"""OTRS :: ticket:: template."""
from otrs.client import WebService
from otrs.session.operations import SessionCreate
from otrs.ticket.operations import TicketCreate
from otrs.ticket.operations import TicketGet
from otrs.ticket.operations import TicketSearch
from otrs.ticket.operations import TicketUpdate


def GenericTicketConnectorSOAP(webservice_name='GenericTicketConnectorSOAP'):
    """Return a GenericTicketConnectorSOAP Webservice object.

    @returns a WebService object with the GenericTicketConnectorSOAP operations
    """
    return WebService(webservice_name, 'http://www.otrs.org/TicketConnector',
                      SessionCreate=SessionCreate(),
                      TicketCreate=TicketCreate(),
                      TicketGet=TicketGet(), TicketSearch=TicketSearch(),
                      TicketUpdate=TicketUpdate())
