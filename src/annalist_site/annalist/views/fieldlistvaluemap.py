"""
Annalist class for processing a list of field mappings for conversion between
entity values context values and form data.

A FieldListValueMap is an object that can be inserted into an entity view value
mapping table to process the corresponding list of fields.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

# import collections

from django.conf                        import settings

from annalist.fields.render_utils       import bound_field

from annalist.views.fielddescription    import FieldDescription
from annalist.views.fieldvaluemap       import FieldValueMap
from annalist.views.repeatdescription   import RepeatDescription
from annalist.views.repeatvaluesmap     import RepeatValuesMap
from annalist.views.subgroupvaluemap    import SubgroupValueMap

class FieldListValueMap(object):
    """
    Define an entry to be added to an entity view value mapping table,
    corresponding to a list of field descriptions.

    NOTE: select fields are handled by having a special field 'options' passed
    in the default value supplied, which is picked out and handled specially
    in the bound_field class.

    coll    is the collection object holding the field definitions
    fields  list of field descritpions from a view definition.

    NOTE: The form rendering template iterates over the context field values to be 
    added to the form display.  The constructor for this object appends the current
    field to a list of field value mappings in context field 'fields'.
    """

    def __init__(self, coll, fields=[]):
        self.fd = []
        self.fs = []
        for f in fields:
            # log.info("\n********\nFieldListValueMap: field %r\n*********"%(f))
            if 'annal:field_id' in f:
                field_context = FieldDescription(coll, f)
                log.debug("FieldListValueMap: field_id %s, field_name %s"%
                    (field_context['field_id'], field_context['field_name'])
                    )
                self.fd.append(field_context.get_structure_description())
                self.fs.append(FieldValueMap(f=field_context))
            elif 'annal:repeat_id' in f:
                repeat_context  = RepeatDescription(f)  # For repeat controls, button labels, etc.
                repeatfieldsmap = FieldListValueMap(coll, fields=f['annal:repeat'])
                repeatvaluesmap = RepeatValuesMap(repeat=repeat_context, fields=repeatfieldsmap)
                # log.info("\n********\nRepeatValuesMap: repeat_id %s, %r"%(f['annal:repeat_id'], repeatvaluesmap))
                self.fd.append(repeatvaluesmap.get_structure_description())
                self.fs.append(repeatvaluesmap)
            else:
                assert False, "Unknown/unsupported field values:"+repr(f)
        return

    def __repr__(self):
        return (
            "FieldListValueMap.fs: %r\n"%(self.fs)
            )

    def map_entity_to_context(self, entityvals, extras=None):
        listcontext = []
        for f in self.fs:
            fv = f.map_entity_to_context(entityvals, extras=extras)
            listcontext.append(fv)
        return { 'fields': listcontext }

    def map_form_to_entity(self, formvals):
        vals = {}
        for f in self.fs:
            vals.update(f.map_form_to_entity(formvals))
        return vals

    def map_form_to_entity_repeated_items(self, formvals, prefix):
        """
        Extra helper method used when mapping repeated field items to repeated entity values.
        The field names extracted are constructed using the supplied prefix string.

        Returns None if a prefixed value does not exist, which may be used as a loop
        termination condition.
        """
        vals = {}
        for f in self.fs:
            v = f.map_form_to_entity_repeated_item(formvals, prefix)
            if v is None: return v
            vals.update(v)
        return vals

    def get_structure_description(self):
        """
        Helper function returns list of field description information
        """
        return { 'field_list': self.fd }

# End.
