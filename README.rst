Python-OTRS : Python wrapper to OTRS SOAP API
=============================================

Let you access the OTRS API a pythonic-way.

Features
--------

-  Implements fully communication with the ``GenericTicketConnectorSOAP`` and ``GenericFAQConnectorSOAP``
   provided as webservice example by OTRS;
-  Dynamic fields and attachments are supported;
-  Authentication is handled programmatically, per-request or per-session;
-  Calls are wrapped in OTRSClient methods;
-  OTRS XML objects are mapped to Python-style objects.

To be done
----------

-  Test for python3 compatibility and make resulting changes;
-  Improve and extend ``tests.py``.

Install
-------

::

    pip install python-otrs

Ticket and Session Operations
-----------------------------

First make sure you installed the ``GenericTicketConnectorSOAP`` webservice,
see `official documentation`_. The file GenericTicketConnectorSOAP.yml can be downloaded
online as the basis for this service.

Note: in older versions of OTRS, GenericTicketConnectorSOAP was called GenericTicketConnector

::

    from otrs.ticket.template import GenericTicketConnectorSOAP
    from otrs.client import GenericInterfaceClient
    from otrs.ticket.objects import Ticket, Article, DynamicField, Attachment

    server_uri = r'https://otrs.example.net'
    webservice_name = 'GenericTicketConnectorSOAP'
    client = GenericInterfaceClient(server_uri, tc=GenericTicketConnectorSOAP(webservice_name))

Then authenticate, you have three choices :

::

    # user session
    client.tc.SessionCreate(user_login='login', password='password')

    # customer_user session
    client.tc.SessionCreate(customer_user_login='login' , password='password')

    # save user in memory
    client.register_credentials(user='login', password='password')

Play !

Create a ticket :

::

    import mimetypes
    import base64

    t = Ticket(State='new', Priority='3 normal', Queue='Support',
               Title='Problem test', CustomerUser='foo@example.fr',
               Type='Divers')
    a = Article(Subject='UnitTest', Body='bla', Charset='UTF8',
                MimeType='text/plain')
    df1 = DynamicField(Name='TestName1', Value='TestValue1')
    df2 = DynamicField(Name='TestName2', Value='TestValue2')
    att_path = r'C:\Temp\image001.png'
    mimetype = mimetypes.guess_type(att_path)[0]
    att_file = open(att_path , 'rb')
    att_content = base64.b64encode(af1.read())
    att1 = Attachment(Content=att_content,
                      ContentType=mimetype, Filename="image001.png")
    att_file.close()

    t_id, t_number = client.tc.TicketCreate(t, a, [df1, df2], [att1])

Update an article :

::

    # changes the title of the ticket
    t_upd = Ticket(Title='Updated ticket')
    client.tc.TicketUpdate(t_id, t_upd)

    # appends a new article (attachments optional)
    new_article = Article(Subject='More info', Body='blabla', Charset='UTF8',
                          MimeType='text/plain')
    client.tc.TicketUpdate(article=new_article, attachments=None)

Search for tickets :

::

    # returns all the tickets of customer 42
    tickets = client.tc.TicketSearch(CustomerID=42)

    # returns all tickets in queue Support
    # for which Dynamic Field 'Project' starts with 'Pizza':
    df2 = DynamicField(Name='Project', Value='Pizza%', Operator="Like")
    client.tc.TicketSearch(Queues='Support', dynamic_fields=[df_search])

Retrieve a ticket :

::

    ticket = client.tc.TicketGet(138, get_articles=True, get_dynamic_fields=True, get_attachments=True)
    article = ticket.articles()[0]
    article.save_attachments(r'C:\temp')

Many options are possible with requests, you can use all the options
available in `official documentation`_.

.. _official documentation: http://otrs.github.io/doc/manual/admin/4.0/en/html/genericinterface.html#generic-ticket-connector

Public FAQ Operations
---------------------

First, make sure you have installed the open-source FAQ add-on module into your OTRS system and added the
GenericFAQConnectorSOAP web service by installing the GenericFAQConnector.yml file.

::

    from otrs.ticket.template import GenericTicketConnectorSOAP
    from otrs.faq.template import GenericFAQConnectorSOAP
    from otrs.client import GenericInterfaceClient

    client = GenericInterfaceClient('https://otrs.mycompany.com', tc=GenericTicketConnectorSOAP('GenericTicketConnectorSOAP'), fc=GenericFAQConnectorSOAP('GenericFAQConnectorSOAP'))

    # first, establish session with the TicketConnector
    client.tc.SessionCreate(user_login='someotrsuser', password='p4ssw0rd')

List FAQ Languages:

::

    langlist = client.fc.LanguageList()
    for language in langlist:
        print language.ID, language.Name

List FAQ Categories that have Public FAQ items in them:

::

    catlist = client.fc.PublicCategoryList()
    for category in catlist:
        print category.ID, category.Name

Retrieve a pubblic FAQ article by ID
(note: FAQ Item ID is not the same as the item number!)

::

    # retrieves FAQ item ID #190 with attachment contents included
    myfaqitem = client.fc.PublicFAQGet(190, get_attachments=True)
    # print the FAQ's Problem field
    print myfaqitem.Field2
	# saves attachments to folder ./tempattach
    myfaqitem.save_attachments('./tempattach')

Search for an FAQ article
	
::

    #find all FAQ articles with Windows in title:
	results = client.fc.PublicFAQSearch(Title='*Windows*')
	for faqitemid in results:
	    print "Found FAQ item ID containing Windows: " + str(faqitemid)
	
	
Custom Web Service Connectors
-----------------------------

For the FAQ operations above, note that we still needed the Ticket connector to provide access
to the SessionCreate method. However, if your application only needs to work with FAQ articles
and not tickets, you may wish to create a custom web service in OTRS that not only includes
the four FAQ operations but also includes the SessionCreate operation to allow you to establish
a session. This is very easy to accommodate in python-otrs.

First, in OTRS, do the following:

1. In OTRS Admin->Web Services, add a new web service without using a .yml file. Name it something
   like 'ImprovedFAQConnectorSOAP'. 
2. In the settings for the web service, set the transport to HTTP::SOAP
3. Click Save
4. Click the 'Configure' button that has appeared next to HTTP::SOAP
5. Set the namespace name to whatever you want (ex. http://www.otrs.org/FAQConnector).
6. Enter the maximum message length you want (normally 10000000)
7. Save the changes and go back to the main web service configuration screen.
8. Add the operations you want to your custom webservice. For instance, for our improved FAQConnector,
   you might add the four FAQ Operations and also the SessionCreate operation.
9. Save your webservice

Now that we have a web service in OTRS, we can use our custom web service in python-otrs. To do this,
first create a 'template' for your new ImprovedFAQConnectorSOAP. Specify the namespace name assigned
in step 5 above as the second parameter to the WebService() call.

::

    from otrs.faq.operations import LanguageList,PublicCategoryList,PublicFAQGet,PublicFAQSearch
    from otrs.session.operations import SessionCreate
    from otrs.client import WebService

    def ImprovedFAQConnectorSOAP(webservice_name='ImprovedFAQConnectorSOAP'):
        return WebService(webservice_name, 'http://www.otrs.org/FAQConnector', SessionCreate=SessionCreate(), LanguageList=LanguageList(),PublicCategoryList=PublicCategoryList(),PublicFAQGet=PublicFAQGet(),PublicFAQSearch=PublicFAQSearch())

Now, use your improved FAQ connector:

::

    from otrs.client import GenericInterfaceClient

    client = GenericInterfaceClient('https://otrs.mycompany.com', impfaqc=ImprovedFAQConnectorSOAP('ImprovedFAQConnectorSOAP'))

    # first, establish session
    client.impfaqc.SessionCreate(user_login='someotrsuser', password='p4ssw0rd')
	
	# get an FAQ item:
	client.impfaqc.PublicFAQGet(190)