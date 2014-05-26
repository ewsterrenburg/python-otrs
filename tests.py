from unittest import TestCase
import os
import xml.etree.ElementTree as etree

from otrs.client import GenericTicketConnector
from otrs.objects import Ticket, Article

REQUIRED_VARS = 'OTRS_LOGIN', 'OTRS_PASSWORD', 'OTRS_SERVER', 'OTRS_WEBSERVICE'
MISSING_VARS = []

for i in REQUIRED_VARS:
    if not i in os.environ.keys():
        MISSING_VARS.append(i)
    else:
        (locals())[i] = os.environ[i]

SAMPLE_TICKET =  """<Ticket>
            <Age>346654</Age>
            <ArchiveFlag>n</ArchiveFlag>
            <ChangeBy>2</ChangeBy>
            <Changed>2014-05-16 11:24:19</Changed>
            <CreateBy>1</CreateBy>
            <CreateTimeUnix>1400234702</CreateTimeUnix>
            <Created>2014-05-16 10:05:02</Created>
            <CustomerID>9</CustomerID>
            <CustomerUserID>foo@bar.tld</CustomerUserID>
            <EscalationResponseTime>0</EscalationResponseTime>
            <EscalationSolutionTime>0</EscalationSolutionTime>
            <EscalationTime>0</EscalationTime>
            <EscalationUpdateTime>0</EscalationUpdateTime>
            <GroupID>1</GroupID>
            <Lock>unlock</Lock>
            <LockID>1</LockID>
            <Owner>fbarman</Owner>
            <OwnerID>2</OwnerID>
            <Priority>3 normal</Priority>
            <PriorityID>3</PriorityID>
            <Queue>Support</Queue>
            <QueueID>2</QueueID>
            <RealTillTimeNotUsed>0</RealTillTimeNotUsed>
            <Responsible>admin</Responsible>
            <ResponsibleID>1</ResponsibleID>
            <SLAID/>
            <ServiceID/>
            <State>closed unsuccessful</State>
            <StateID>3</StateID>
            <StateType>closed</StateType>
            <TicketID>32</TicketID>
            <TicketNumber>515422152827</TicketNumber>
            <Title>Foofoo my title</Title>
            <Type>Divers</Type>
            <TypeID>1</TypeID>
            <UnlockTimeout>1400239459</UnlockTimeout>
            <UntilTime>0</UntilTime>
         </Ticket>
"""

SAMPLE_TICKET_W_ARTICLES =  """<Ticket>
		<Age>863982</Age>
		<ArchiveFlag>n</ArchiveFlag>
		<Article>
                  <Age>863982</Age>
		  <AgeTimeUnix>863982</AgeTimeUnix>
		  <ArticleID>101</ArticleID>
		  <ArticleType>email-external</ArticleType>
		  <ArticleTypeID>1</ArticleTypeID>
		  <Body>
Bonjour,

Voir echange ci-dessous.

Cdlt.

		  </Body>
		  <Cc>ACME-CORP - John DOE &lt;john.doe@exemple.fr&gt;</Cc>
		  <CcRealname>ACME-CORP - John DOE</CcRealname>
		  <Changed>2014-05-16 11:24:19</Changed>
		  <Charset>utf-8</Charset>
		  <ContentCharset>utf-8</ContentCharset>
		  <ContentType>text/plain; charset=utf-8</ContentType>
		  <CreateTimeUnix>1400234702</CreateTimeUnix>
		  <Created>2014-05-16 10:05:02</Created>
		  <CreatedBy>1</CreatedBy>
		  <CustomerID>9</CustomerID>
		  <CustomerUserID>john.doe@exemple.fr</CustomerUserID>
		  <EscalationResponseTime>0</EscalationResponseTime>
		  <EscalationSolutionTime>0</EscalationSolutionTime>
		  <EscalationTime>0</EscalationTime>
		  <EscalationUpdateTime>0</EscalationUpdateTime>
		  <From>John DOE &lt;john.doe@exemple.fr&gt;</From>
		  <FromRealname>John DOE</FromRealname>
		  <InReplyTo>&lt;1586719931.242426547.1400234690351.JavaMail.zimbra@exemple.fr&gt;</InReplyTo>
		  <IncomingTime>1400234702</IncomingTime>
		  <Lock>unlock</Lock>
		  <LockID>1</LockID>
		  <MessageID>&lt;1586719931.242426547.1400234690351.JavaMail.zimbra@exemple.fr&gt;</MessageID>
		  <MimeType>text/plain</MimeType>
		  <Owner>admin</Owner>
		  <OwnerID>2</OwnerID>
		  <Priority>3 normal</Priority>
		  <PriorityID>3</PriorityID>
		  <Queue>Support</Queue>
		  <QueueID>2</QueueID>
		  <RealTillTimeNotUsed>0</RealTillTimeNotUsed>
		  <References />
		  <ReplyTo />
		  <Responsible>admin</Responsible>
		  <ResponsibleID>1</ResponsibleID>
		  <SLA />
		  <SLAID />
		  <SenderType>customer</SenderType>
		  <SenderTypeID>3</SenderTypeID>
		  <Service />
		  <ServiceID />
		  <State>closed unsuccessful</State>
		  <StateID>3</StateID>
		  <StateType>closed</StateType>
		  <Subject>Title</Subject>
		  <TicketID>32</TicketID>
		  <TicketNumber>515422152827</TicketNumber>
		  <Title>TEST msg</Title>
		  <To>support test  &lt;support-test@exemple.fr&gt; </To>
		  <ToRealname>Support test</ToRealname>
		  <Type>Divers</Type>
		  <TypeID>1</TypeID>
		  <UntilTime>0</UntilTime>
		</Article>
		<ChangeBy>2</ChangeBy>
		<Changed>2014-05-16 11:24:19</Changed>
		<CreateBy>1</CreateBy>
		<CreateTimeUnix>1400234702</CreateTimeUnix>
		<Created>2014-05-16 10:05:02
		</Created>
		<CustomerID>9
		</CustomerID>
		<CustomerUserID>john.doe@exemple.fr</CustomerUserID>
		<EscalationResponseTime>0</EscalationResponseTime>
		<EscalationSolutionTime>0</EscalationSolutionTime>
		<EscalationTime>0</EscalationTime>
		<EscalationUpdateTime>0</EscalationUpdateTime>
		<GroupID>1</GroupID>
		<Lock>unlock</Lock>
		<LockID>1</LockID>
		<Owner>admin</Owner>
		<OwnerID>2</OwnerID>
		<Priority>3 normald</Priority>
		<PriorityID>3</PriorityID>
		<Queue>Support</Queue>
		<QueueID>2</QueueID>
		<RealTillTimeNotUsed>0</RealTillTimeNotUsed>
		<Responsible>admin</Responsible>
		<ResponsibleID>1</ResponsibleID>
		<SLAID />
                <ServiceID />
		<State>closed unsuccessful</State>
		<StateID>3</StateID>
		<StateType>closed</StateType>
		<TicketID>32</TicketID>
		<TicketNumber>515422152827</TicketNumber>
		<Title>Test ticket</Title>
		<Type>Divers</Type>
		<TypeID>1</TypeID>
		<UnlockTimeout>1400239459</UnlockTimeout>
		<UntilTime>0</UntilTime>
	  </Ticket>"""

if not MISSING_VARS:
    class TestOTRSAPI(TestCase):
        def setUp(self):
            self.c = GenericTicketConnector(OTRS_SERVER, OTRS_WEBSERVICE)
            self.c.register_credentials(OTRS_LOGIN, OTRS_PASSWORD)

        def test_session_create(self):
            sessid = self.c.session_create(user_login = OTRS_LOGIN,
                                           password   = OTRS_PASSWORD)
            self.assertEqual(len(sessid), 32)

        def test_ticket_get(self):
            t = self.c.ticket_get(32)
            self.assertEqual(t.TicketID, 32)
            self.assertEqual(t.StateType, 'closed')

        def test_ticket_get_with_articles(self):
            res = self.c.ticket_get(32, get_articles=True)
            self.assertIsInstance(res, (list, tuple))
            self.assertEqual(len(res), 2)
            ticket, articles = res
            self.assertEqual(t.TicketID, 32)
            self.assertEqual(t.StateType, 'closed')
            self.assertIsInstance(articles, (list, tuple))
            self.assertIsInstance(articles[0], Article)


        def test_ticket_search(self):
            t_list = self.c.ticket_search(CustomerID=9)
            self.assertIsInstance(t_list, list)
            self.assertIn(32, t_list)

        def test_ticket_create(self):
            t = Ticket(State='new', Priority='3 normal', Queue='Support',
                       Title='Problem test', CustomerUser='foo@exemple.fr',
                       Type='Divers')
            a = Article(Subject='UnitTest', Body='bla', Charset='UTF8',
                        MimeType='text/plain')
            t_id, t_number = self.c.ticket_create(t, a)
            self.assertIsInstance(t_id, int)
            self.assertIsInstance(t_number, int)
            self.assertTrue(len(str(t_number)) >= 12)

        def test_ticket_update_attrs_by_id(self):
            t = Ticket(State='new', Priority='3 normal', Queue='Support',
                       Title='Problem test', CustomerUser='foo@exemple.fr',
                       Type='Divers')
            a = Article(Subject='UnitTest', Body='bla', Charset='UTF8',
                        MimeType='text/plain')
            t_id, t_number = self.c.ticket_create(t, a)

            t = Ticket(Title='Foubar')
            upd_tid, upd_tnumber = self.c.ticket_update(ticket_id=t_id, ticket=t)
            self.assertIsInstance(upd_tid, int)
            self.assertIsInstance(upd_tnumber, int)
            self.assertTrue(len(str(upd_tnumber)) >= 12)

            self.assertEqual(upd_tid, t_id)
            self.assertEqual(upd_tnumber, t_number)

            upd_t = self.c.ticket_get(t_id)
            self.assertEqual(upd_t.Title, 'Foubar')
            self.assertEqual(upd_t.Queue, 'Support')

        def test_ticket_update_attrs_by_number(self):
            t = Ticket(State='new', Priority='3 normal', Queue='Support',
                       Title='Problem test', CustomerUser='foo@exemple.fr',
                       Type='Divers')
            a = Article(Subject='UnitTest', Body='bla', Charset='UTF8',
                        MimeType='text/plain')
            t_id, t_number = self.c.ticket_create(t, a)

            t = Ticket(Title='Foubar')
            upd_tid, upd_tnumber = self.c.ticket_update(ticket_number=t_number,
                                                        ticket=t)
            self.assertIsInstance(upd_tid, int)
            self.assertIsInstance(upd_tnumber, int)
            self.assertTrue(len(str(upd_tnumber)) >= 12)

            self.assertEqual(upd_tid, t_id)
            self.assertEqual(upd_tnumber, t_number)

            upd_t = self.c.ticket_get(t_id)
            self.assertEqual(upd_t.Title, 'Foubar')
            self.assertEqual(upd_t.Queue, 'Support')

        def test_ticket_update_new_article(self):
            t = Ticket(State='new', Priority='3 normal', Queue='Support',
                       Title='Problem test', CustomerUser='foo@exemple.fr',
                       Type='Divers')
            a = Article(Subject='UnitTest', Body='bla', Charset='UTF8',
                        MimeType='text/plain')
            t_id, t_number = self.c.ticket_create(t, a)


else:
    print 'Set OTRS_LOGIN and OTRS_PASSWORD env vars if you want "real"'+\
        'tests against a real OTRS to be run'


class TestObjects(TestCase):
    def test_ticket(self):
        t = Ticket(TicketID=42, EscalationResponseTime='43')
        self.assertEqual(t.TicketID,42)
        self.assertEqual(t.EscalationResponseTime, 43)

    def test_ticket_from_xml(self):
        xml = etree.fromstring(SAMPLE_TICKET)
        t = Ticket.from_xml(xml)
        self.assertEqual(t.TicketID, 32)
        self.assertEqual(t.CustomerUserID, 'foo@bar.tld')

    def test_ticket_from_xml_with_articles(self):
        xml = etree.fromstring(SAMPLE_TICKET_W_ARTICLES)
        t = Ticket.from_xml(xml)
        self.assertEqual(t.TicketID, 32)
        self.assertEqual(t.CustomerUserID, 'john.doe@exemple.fr')
        articles = t.articles()
        self.assertIsInstance(articles, list)
        self.assertEqual(len(articles), 1)
        self.assertIsInstance(articles[0], Article)
        self.assertEqual(articles[0].AgeTimeUnix, 863982)


    def test_ticket_to_xml(self):
        t = Ticket(State='open', Priority='3 normal', Queue='Support')
        xml = t.to_xml()
        xml_childs = xml.getchildren()

        xml_childs_dict = {i.tag: i.text for i in xml_childs}

        self.assertEqual(xml.tag, 'Ticket')
        self.assertEqual(len(xml_childs), 3)
        self.assertEqual(xml_childs_dict['State'], 'open')
        self.assertEqual(xml_childs_dict['Priority'], '3 normal')
        self.assertEqual(xml_childs_dict['Queue'], 'Support')
