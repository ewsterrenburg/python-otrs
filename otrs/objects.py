"""OTRS :: objects."""
from __future__ import unicode_literals
import base64
import os
import sys
import xml.etree.ElementTree as etree

class OTRSObject(object):
    """Represents an object for OTRS (mappable to an XML element)."""

    # Map : {'TagName' -> Class}
    CHILD_MAP = {}

    def __init__(self, *args, **kwargs):
        """Initialize OTRS Object."""
        self.attrs = kwargs
        self.childs = {}

    def __getattr__(self, k):
        """Get an attribute for aan OTRSObject.

        attrs are simple xml child tags (<tag>val</tag>), complex children,
        are accessible via dedicated methods.

        @returns a simple type
        """
        return autocast(self.attrs[k])

    @classmethod
    def from_xml(cls, xml_element):
        """Create an OTRS Object from xml.

        @param xml_element an etree.Element
        @returns an OTRSObject
        """
        child_tags = cls.CHILD_MAP.keys()

        if not xml_element.tag.endswith(cls.XML_NAME):
            raise ValueError(
                'xml_element should be a {} node, not {}'.format(
                    cls.XML_NAME, xml_element.tag))
        attrs = {}
        childs = []
        for t in xml_element.getchildren():
            name = extract_tagname(t)
            if name in child_tags:
                # Complex child tags
                SubClass = cls.CHILD_MAP[name]
                sub_obj = SubClass.from_xml(t)
                childs.append(sub_obj)
            else:
                # Simple child tags
                attrs[name] = t.text
        obj = cls(**attrs)

        for i in childs:
            obj.add_child(i)

        return obj

    def add_child(self, childobj):
        """Add a child object to an OTRS Object.

        @param childobj : an OTRSObject
        """
        xml_name = childobj.XML_NAME

        if xml_name in self.childs:
            self.childs[xml_name].append(childobj)
        else:
            self.childs[xml_name] = [childobj]

    def check_fields(self, fields):
        """Check that the list of fields is bound.

        @param fields rules, as list

        items n fields can be either :
         - a field name : this field is required
         - a tuple of field names : on of this fields is required
        """
        set_keys = set(self.attrs.keys())

        for i in fields:
            if isinstance(i, str):
                set_fields = set([i])
            else:
                set_fields = set(i)

            if set_keys.intersection(set_fields):
                valid = True
            else:
                valid = False

            if not valid:
                raise ValueError('{} should be filled'.format(i))

    def to_xml(self):
        """Create an XML representation of an OTRS Object.

        @returns am etree.Element
        """
        root = etree.Element(self.XML_NAME)
        for k, v in self.attrs.items():
            e = etree.Element(k)
            if isinstance(e, str):
                v = v.encode('utf-8')
            if sys.version_info[0] == 3:
                e.text = str(v)
            else:
                e.text = unicode(v)
            root.append(e)
        return root


def extract_tagname(element):
    """Return the name of the tag, without namespace.

    element.tag lib gives "{namespace}tagname", we want only "tagname"

    @param element : an etree.Element
    @returns       : a str, the name of the tag
    """
    qualified_name = element.tag
    try:
        return qualified_name.split('}')[1]
    except IndexError:
        # if it's not namespaced, then return the tag name itself
        return element.tag
        # raise ValueError('"{}" is not a tag name'.format(qualified_name))


def autocast(s):
    """Try to guess the simple type and convert the value to it.

    @param s string
    @returns the relevant type : a float, string or int
    """
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s


class Attachment(OTRSObject):
    """An OTRS attachment."""

    XML_NAME = 'Attachment'


class DynamicField(OTRSObject):
    """An OTRS dynamic field."""

    XML_NAME = 'DynamicField'


class AttachmentContainer(object):
    """For objects that can have attachments in them (ex. tickets, articles).

    They should inherit this class in addition to OTRSObject.
    """

    def attachments(self):
        """Return the dynamic fields for an object ket as a list.

        @returns a list of Attachment objects.
        """
        try:
            return self.childs['Attachment']
        except KeyError:
            return []

    def save_attachments(self, folder):
        """Save the attachments of an article to the specified folder.

        @param folder  : a str, folder to save the attachments
        """
        for a in self.attachments():
            fname = a.attrs['Filename']
            fpath = os.path.join(folder, fname)
            content = a.attrs['Content']
            fcontent = base64.b64decode(content)
            ffile = open(fpath, 'wb')
            ffile.write(fcontent)
            ffile.close()


class DynamicFieldContainer(object):
    """For objects that can have dynamic fields in them (ex. tickets, articles).

    They should inherit this class in addition to OTRSObject.
    """

    def dynamicfields(self):
        """Return the dynamic fields for an object ket as a list.

        @returns a list of DynamicField objects.
        """
        try:
            return self.childs['DynamicField']
        except KeyError:
            return []


# the two functions below are here only for backward compatibility
# with old code that imported these classes from this file
# the classes are now in tickets/objects.py


def Ticket(*args, **kwargs):
    """Return an OTRS ticket."""
    import otrs.ticket.objects
    return otrs.ticket.objects.Ticket(*args, **kwargs)


def Article(*args, **kwargs):
    """Return an OTRS article."""
    import otrs.ticket.objects
    return otrs.ticket.objects.Article(*args, **kwargs)
