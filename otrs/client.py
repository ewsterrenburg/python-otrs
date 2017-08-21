"""OTRS :: client."""
import abc
import codecs
from defusedxml import ElementTree as etree
try:
    import http.client as httplib
    import urllib.request as urllib2
except ImportError:
    import httplib
    import urllib2
from otrs.objects import extract_tagname
from otrs.objects import OTRSObject
from posixpath import join as urljoin
import sys
# defusedxml doesn't define these non-parsing related objects
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring

etree.Element = _ElementType = Element
etree.SubElement = SubElement
etree.tostring = tostring

# Fix Python 2.x.
try:
    UNICODE_EXISTS = bool(type(unicode))
except NameError:
    unicode = lambda s: str(s)


class OTRSError(Exception):
    """Base class for OTRS Errors."""

    def __init__(self, fd):
        """Initialize OTRS Error."""
        self.code = fd.getcode()
        self.msg = fd.read()

    def __str__(self):
        """Return error message for OTRS Error."""
        return '{} : {}'.format(self.code, self.msg)


class BadStatusLineError(Exception):
    """Base class for BadStatusLineError Errors."""

    def __init__(self, url):
        """Initialize BadStatusLineError Error."""
        self.url = url

    def __str__(self):
        """Return error message for BadStatusLine Error."""
        return '''BadStatusLine Exception when trying to reach {0}.
            Are you using the correct webservice name?'''.format(self.url)


class SOAPError(OTRSError):
    """OTRS Error originating from an incorrect SOAP request."""

    def __init__(self, tag):
        """Initialize OTRS SOAPError."""
        d = {extract_tagname(i): i.text for i in tag.getchildren()}
        self.errcode = d['ErrorCode']
        self.errmsg = d['ErrorMessage']

    def __str__(self):
        """Return error message for OTRS SOAPError."""
        return '{} ({})'.format(self.errmsg, self.errcode)


class NoCredentialsException(OTRSError):
    """OTRS Error that is returned when no credentials are provided."""

    def __init__(self):
        """Initialize OTRS NoCredentialsException."""
        pass

    def __str__(self):
        """Return error message for OTRS NoCredentialsException."""
        return 'Register credentials first with register_credentials() method'


class WrongOperatorException(OTRSError):
    """OTRS Error that is returned when a non-existent operation is called."""

    def __init__(self):
        """Initialize OTRS WrongOperatorException."""
        pass

    def __str__(self):
        """Return error message for OTRS WrongOperatorException."""
        return '''Please use one of the following operators for the
               query on a dynamic field: `Equals`, `Like`, `GreaterThan`,
               `GreaterThanEquals`, `SmallerThan`  or `SmallerThanEquals`.
               '''


def authenticated(func):
    """Decorator to add authentication parameters to a request."""
    def add_auth(self, *args, **kwargs):
        if self.session_id:
            kwargs['SessionID'] = self.session_id
        elif self.login and self.password:
            kwargs['UserLogin'] = self.login
            kwargs['Password'] = self.password
        else:
            raise NoCredentialsException()

        return func(self, *args, **kwargs)

    return add_auth


class OperationBase(object):
    """Base class for OTRS operations."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, opName=None):
        """Initialize OperationBase."""
        if opName is None:
            self.operName = type(self).__name__
        else:
            self.operName = opName  # otrs connector operation name
        self.wsObject = None    # web services object this operation belongs to

    def getWebServiceObjectAttribute(self, attribName):
        """Return attribute of the WebService object."""
        return getattr(self.wsObject, attribName)

    def getClientObjectAttribute(self, attribName):
        """Return attribute of the clientobject of the WebService object."""
        return self.wsObject.getClientObjectAttribute(attribName)

    def setClientObjectAttribute(self, attribName, attribValue):
        """Set attribute of the clientobject of the WebService object."""
        self.wsObject.setClientObjectAttribute(attribName, attribValue)

    @abc.abstractmethod
    def __call__(self):
        """."""
        return

    @property
    def endpoint(self):
        """Return endpoint of WebService object."""
        return self.getWebServiceObjectAttribute('endpoint')

    @property
    def login(self):
        """Get login attribute of the clientobject of the WebService object."""
        return self.getClientObjectAttribute('login')

    @property
    def password(self):
        """Return password attribute of the clientobject of the WebService."""
        return self.getClientObjectAttribute('password')

    @property
    def ssl_context(self):
        """Return ssl_context of the clientobject of the WebService."""
        return self.getClientObjectAttribute('ssl_context')

    @property
    def session_id(self):
        """Return session_id of the clientobject of the WebService object."""
        return self.getClientObjectAttribute('session_id')

    @session_id.setter
    def session_id(self, sessionid):
        """Set session_id of the clientobject of the WebService object."""
        self.setClientObjectAttribute('session_id', sessionid)

    @property
    def soap_envelope(self):
        """Return soap envelope for WebService object."""
        soap_envelope = '<soapenv:Envelope ' +  \
            'xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" ' + \
            'xmlns= "' + self.getWebServiceObjectAttribute('wsNamespace') + \
            '"><soapenv:Header/><soapenv:Body>{}</soapenv:Body>' + \
            '</soapenv:Envelope>'
        return soap_envelope

    def req(self, reqname, *args, **kwargs):
        """Wrapper around a SOAP request.

        @param reqname: the SOAP name of the request
        @param kwargs : to define the tags included in the request.
        @return       : the full etree.Element of the response

        keyword arguments can be either
         - simple types (they'l be converted to <name>value</name>)
         - `OTRSObject`, they will be serialized with their `.to_xml()`
         - list of  `OTRSObject`s: each  `OTRSObject`s in the list
           will be serialized with their `.to_xml()` (used for
           dynamic fields and attachments).
         - list of simple types will be converted to multiple
           <name>value</name> elements (e.g. used for search filters)
        """
        xml_req_root = etree.Element(reqname)

        for k, v in kwargs.items():
            if isinstance(v, OTRSObject):
                e = v.to_xml()
                xml_req_root.append(e)
            elif isinstance(v, (list, tuple)):
                for vv in v:
                    if isinstance(vv, OTRSObject):
                        e = vv.to_xml()
                    else:
                        e = etree.Element(k)
                        e.text = unicode(vv)
                    xml_req_root.append(e)
            else:
                e = etree.Element(k)
                e.text = unicode(v)
                xml_req_root.append(e)

        request = urllib2.Request(
            self.endpoint, self._pack_req(xml_req_root),
            {'Content-Type': 'text/xml;charset=utf-8'})

        try:
            if ((sys.version_info[0] == 3 and sys.version_info < (3, 4, 3)) or
                    (sys.version_info < (2, 7, 9))):
                fd = urllib2.urlopen(request)
            else:
                try:
                    fd = urllib2.urlopen(request, context=self.ssl_context)
                except TypeError:
                    fd = urllib2.urlopen(request)
        except httplib.BadStatusLine:
            raise BadStatusLineError(request.get_full_url())

        if fd.getcode() != 200:
            raise OTRSError(fd)
        else:
            try:
                s = fd.read()
                e = etree.fromstring(s)

                unpacked = self._unpack_resp_several(e)
                if (len(unpacked) > 0) and (unpacked[0].tag.endswith('Error')):
                    raise SOAPError(unpacked[0])
                return e
            except etree.ParseError:
                print('error parsing:')
                print('-' * 80)
                print(s)
                print('-' * 80)
                raise

    @staticmethod
    def _unpack_resp_several(element):
        """Unpack an etree element and return a list of children.

        @param element : a etree.Element
        @return        : a list of etree.Element
        """
        return element.getchildren()[0].getchildren()[0].getchildren()

    @staticmethod
    def _unpack_resp_one(element):
        """Unpack an etree element an return first child.

        @param element : a etree.Element
        @return        : a etree.Element (first child of the response)
        """
        return element.getchildren()[0].getchildren()[0].getchildren()[0]

    def _pack_req(self, element):
        """Pack an etree Element.

        @param element : a etree.Element
        @returns       : a string, wrapping element within the request tags
        """
        return self.soap_envelope.format(
            codecs.decode(etree.tostring(element), 'utf-8')).encode('utf-8')


class WebService(object):
    """Base class for OTRS Web Service."""

    def __init__(self, wsName, wsNamespace, **kwargs):
        """Initialize WebService object."""
        self.clientObject = None        # link to parent client object
        self.wsName = wsName            # name for OTRS web service
        self.wsNamespace = wsNamespace  # OTRS namespace url

        # add all variables in kwargs into the local dictionary
        self.__dict__.update(kwargs)

        # for operations, set backlinks to their associated webservice
        for arg in kwargs:
            # if attribute is type OperationBase, set backlink to WebService
            if isinstance(getattr(self, arg), OperationBase):
                getattr(self, arg).wsObject = self

        # set defaults if attributes are not present
        if not hasattr(self, 'wsRequestNameScheme'):
            self.wsRequestNameScheme = '<FunctionName>DATA</FunctionName>'
        if not hasattr(self, 'wsResponseNameScheme'):
            ns = '<FunctionNameResponse>DATA</FunctionNameResponse>'
            self.wsResponseNameScheme = ns

    def getClientObjectAttribute(self, attribName):
        """Return attribute of the clientobject of the WebService object."""
        return getattr(self.clientObject, attribName)

    def setClientObjectAttribute(self, attribName, attribValue):
        """Set attribute of the clientobject of the WebService object."""
        setattr(self.clientObject, attribName, attribValue)

    @property
    def endpoint(self):
        """Return endpoint of WebService object."""
        return urljoin(self.getClientObjectAttribute('giurl'), self.wsName)


class GenericInterfaceClient(object):
    """Client for the OTRS Generic Interface."""

    def __init__(self, server, ssl_context=None, **kwargs):
        """Initialize GenericInterfaceClient.

        @param server : the http(s) URL of the root installation of OTRS
        (e.g: https://tickets.example.net)
        """
        # add all variables in kwargs into the local dictionary
        self.__dict__.update(kwargs)

        # for webservices attached to this client object, backlink them
        # to this client object to allow access to session login/password

        for arg in kwargs:
            # set backlink for web services to this obj
            if isinstance(getattr(self, arg), WebService):
                getattr(self, arg).clientObject = self
        self.login = None
        self.password = None
        self.session_id = None
        self.ssl_context = ssl_context
        self.giurl = urljoin(
            server, 'otrs/nph-genericinterface.pl/Webservice/')

    def register_credentials(self, login, password):
        """Save the identifiers in memory.

        They will be used with each subsequent request requiring authentication
        """
        self.login = login
        self.password = password


class OldGTCClass(GenericInterfaceClient):
    """DEPRECATED - Old generic ticket connector class.

    Used for backward compatibility with previous versions. All
    methods in here are deprecated.
    """

    def session_create(self, password, user_login=None,
                       customer_user_login=None):
        """DEPRECATED - creates a session for an User or CustomerUser.

        @returns the session_id
        """
        self.tc.SessionCreate(password, user_login=user_login,
                              customer_user_login=customer_user_login)

    def user_session_register(self, user, password):
        """DEPRECATED - creates a session for an User."""
        self.session_create(password=password, user_login=user)

    def customer_user_session_register(self, user, password):
        """DEPRECATED - creates a session for a CustomerUser."""
        self.session_create(password=password, customer_user_login=user)

    @authenticated
    def ticket_create(self, ticket, article, dynamic_fields=None,
                      attachments=None, **kwargs):
        """DEPRECATED - now calls operation of GenericTicketConnectorSOAP."""
        return self.tc.TicketCreate(ticket,
                                    article,
                                    dynamic_fields=dynamic_fields,
                                    attachments=attachments,
                                    **kwargs)

    @authenticated
    def ticket_get(self, ticket_id, get_articles=False,
                   get_dynamic_fields=False, get_attachments=False,
                   *args, **kwargs):
        """DEPRECATED - now calls operation of GenericTicketConnectorSOAP."""
        return self.tc.TicketGet(ticket_id,
                                 get_articles=get_articles,
                                 get_dynamic_fields=get_dynamic_fields,
                                 get_attachments=get_attachments,
                                 *args,
                                 **kwargs)

    @authenticated
    def ticket_search(self, dynamic_fields=None, **kwargs):
        """DEPRECATED - now calls operation of GenericTicketConnectorSOAP."""
        return self.tc.TicketSearch(dynamic_fields=dynamic_fields, **kwargs)

    @authenticated
    def ticket_update(self, ticket_id=None, ticket_number=None,
                      ticket=None, article=None, dynamic_fields=None,
                      attachments=None, **kwargs):
        """DEPRECATED - now calls operation of GenericTicketConnectorSOAP."""
        return self.tc.TicketUpdate(ticket_id=ticket_id,
                                    ticket_number=ticket_number,
                                    ticket=ticket,
                                    article=article,
                                    dynamic_fields=dynamic_fields,
                                    attachments=attachments, **kwargs)


def GenericTicketConnector(server,
                           webservice_name='GenericTicketConnector',
                           ssl_context=None):
    """DEPRECATED - now calls operation of GenericTicketConnectorSOAP."""
    from otrs.session.operations import SessionCreate
    from otrs.ticket.operations import TicketCreate
    from otrs.ticket.operations import TicketGet
    from otrs.ticket.operations import TicketSearch
    from otrs.ticket.operations import TicketUpdate

    ticketconnector = WebService(
        webservice_name,
        'http://www.otrs.org/TicketConnector',
        ssl_context=ssl_context,
        SessionCreate=SessionCreate(),
        TicketCreate=TicketCreate(),
        TicketGet=TicketGet(),
        TicketSearch=TicketSearch(),
        TicketUpdate=TicketUpdate())
    return OldGTCClass(server, tc=ticketconnector)
