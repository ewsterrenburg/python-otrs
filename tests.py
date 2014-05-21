from unittest import TestCase
import os
import xml.etree.ElementTree as etree

from otrs.client import GenericTicketConnector
from otrs.objects import Ticket

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

        def test_ticket_search(self):
            t_list = self.c.ticket_search(CustomerID=9)
            self.assertIsInstance(t_list, list)
            self.assertIn(32, t_list)

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

