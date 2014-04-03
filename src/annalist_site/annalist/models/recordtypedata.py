"""
Collection of Annalist data records for a specified record type
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import os.path
import urlparse
import shutil

import logging
log = logging.getLogger(__name__)

from django.conf import settings

from annalist                   import layout
from annalist.exceptions        import Annalist_Error
from annalist.identifiers       import ANNAL
from annalist                   import util
from annalist.models.entity     import Entity
from annalist.models.entitydata import EntityData

class RecordTypeData(Entity):

    _entitytype = ANNAL.CURIE.RecordType_Data
    _entitypath = layout.COLL_TYPEDATA_PATH
    _entityfile = layout.TYPEDATA_META_FILE
    _entityref  = layout.META_TYPEDATA_REF

    def __init__(self, parent, type_id, altparent=False):
        """
        Initialize a new RecordTypeData object, without metadata.

        parent      is the parent collection from which the type data is descended.
        type_id     the local identifier (slug) for the record type
        altparent   True if values from the alternate parent are to be included in
                    RecordData entities returned.
        """
        super(RecordTypeData, self).__init__(parent, type_id, altparent=altparent)
        self._include_alt = altparent
        return

    def entities(self):
        """
        Generator enumerates and returns record types that may be stored
        """
        log.debug("RecordTypeData.entities: include_alt %r"%self._include_alt)
        for f in self._children(EntityData, include_alt=self._include_alt):
            log.debug("RecordTypeData.entities: f %s"%f)            
            e = EntityData.load(self, f)
            if e:
                yield e
        return

    def remove_entity(self, entity_id):
        t = EntityData.remove(self, entity_id)
        return t

# End.
