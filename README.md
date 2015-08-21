Python-OTRS : Python wrapper to OTRS SOAP API
=============================================

Let you access the OTRS API a pythonic-way.

Features
--------

- Implements fully communication with the `GenericTicketConnector` provided as
  webservice example by OTRS;
- authentication is handled programaticaly, per-request or per-session;
- calls are wrapped in OTRSClient methods;
- OTRS XML objects are mapped to Python-style objects see objects.Article and
  objects.Ticket.

Non-features
------------

- Tickets attachments


Install
-------

    ./setup.py install

Using
-----

First make sure you installed the `GenericTicketConnector` webservice, see
[official documentation](http://otrs.github.io/doc/manual/admin/3.3/en/html/genericinterface.html#generic-ticket-connector).

    from otrs.client import GenericTicketConnector
	from otrs.objects import Ticket, Article

	server_uri = https://otrs.exemple.net
	webservice_name = 'GenericTicketConnector'
    client = GenericTicketConnector(server_uri, webservice_name)

Then authenticate, you have three choices :

    # user session
	client.user_session_register('login', 'password')

	# customer_user session
	client.customer_user_session_register('login' , 'password')

	# save user in memory
    client.register_credentials(user='login', 'password')


Play !

Create a ticket :

    t = Ticket(State='new', Priority='3 normal', Queue='Support',
               Title='Problem test', CustomerUser='foo@exemple.fr',
			   Type='Divers')
    a = Article(Subject='UnitTest', Body='bla', Charset='UTF8',
	            MimeType='text/plain')
    t_id, t_number = client.ticket_create(t, a)

Append an article :

     new_article = Article(Subject='Moar info', Body='blabla', Charset='UTF8',
                           MimeType='text/plain')
	 client.update_ticket(article=new_article)

Search for tickets :

	  # returns all the tickets of customer 42
      tickets = client.ticket_search(CustomerID=42)


Many options are possible with requests, you can use all the options available
in
[official documentation](http://otrs.github.io/doc/manual/admin/3.3/en/html/genericinterface.html#generic-ticket-connector).
