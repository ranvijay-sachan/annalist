"""
Annalist vocabulary record
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
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

class RecordVocab(EntityData):

    _entitytype     = ANNAL.CURIE.Vocabulary
    _entitytypeid   = "_vocab"
    _entityview     = layout.COLL_VOCAB_VIEW
    _entitypath     = layout.COLL_VOCAB_PATH
    _entityaltpath  = layout.SITE_VOCAB_PATH
    _entityfile     = layout.VOCAB_META_FILE
    _entityref      = layout.META_VOCAB_REF

    def __init__(self, parent, vocab_id, altparent=None):
        """
        Initialize a new RecordVocab object, without metadata (yet).

        parent      is the parent entity from which the view is descended.
        vocab_id    the local identifier for the vocabulary; also used as namespace prefix.
        altparent   is a site object to search for this new entity,
                    allowing site-wide RecordVocab values to be found.
        """
        super(RecordVocab, self).__init__(parent, vocab_id, altparent)
        log.debug("RecordVocab %s: dir %s, alt %s"%(vocab_id, self._entitydir, self._entityaltdir))
        return

# End.