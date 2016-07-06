Python-OTRS : Python wrapper to OTRS SOAP API
=============================================

Let you access the OTRS API a pythonic-way.

Features
--------

-  Implements fully communication with the ``GenericTicketConnector``
   provided as webservice example by OTRS;
-  dynamic fields and attachments are supported;
-  authentication is handled programmatically, per-request or per-session;
-  calls are wrapped in OTRSClient methods;
-  OTRS XML objects are mapped to Python-style objects see
   objects.Article and objects.Ticket.

To be done
----------

-  Test for python3 compatibility and make resulting changes;
-  improve and extend ``tests.py``;

Install
-------

::

    pip install python-otrs

Using
-----

First make sure you installed the ``GenericTicketConnectorSOAP`` webservice,
see `official documentation`_.

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
    client.register_credentials(user='login', 'password')

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
    new_article = Article(Subject='Moar info', Body='blabla', Charset='UTF8',
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
