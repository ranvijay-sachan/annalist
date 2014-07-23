"""
Tests for RecordType module and view
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                        import settings
from django.db                          import models
from django.http                        import QueryDict
from django.contrib.auth.models         import User
from django.test                        import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client                 import Client

from annalist.identifiers               import RDF, RDFS, ANNAL
from annalist                           import layout
from annalist.models.site               import Site
from annalist.models.sitedata           import SiteData
from annalist.models.collection         import Collection
from annalist.models.recordtype         import RecordType

from annalist.views.recordtypedelete    import RecordTypeDeleteConfirmedView

from tests                              import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                              import init_annalist_test_site
from AnnalistTestCase                   import AnnalistTestCase
from entity_testutils                   import (
    site_dir, collection_dir,
    site_view_uri, collection_edit_uri, 
    collection_create_values,
    site_title
    )
from entity_testtypedata                import (
    recordtype_dir,
    recordtype_coll_uri, recordtype_site_uri, recordtype_uri, recordtype_edit_uri,
    recordtype_value_keys, recordtype_load_keys, 
    recordtype_create_values, recordtype_values, recordtype_read_values,
    recordtype_entity_view_context_data, 
    recordtype_entity_view_form_data, recordtype_delete_confirm_form_data
    )
from entity_testentitydata              import (
    entity_uri, entitydata_edit_uri, entitydata_list_type_uri
    )

#   -----------------------------------------------------------------------------
#
#   RecordType tests
#
#   -----------------------------------------------------------------------------

class RecordTypeTest(AnnalistTestCase):
    """
    Tests for RecordType object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.sitedata = SiteData(self.testsite)
        self.testcoll = Collection(self.testsite, "testcoll")
        return

    def tearDown(self):
        return

    def test_RecordTypeTest(self):
        self.assertEqual(Collection.__name__, "Collection", "Check Collection class name")
        return

    def test_recordtype_init(self):
        t = RecordType(self.testcoll, "testtype", self.testsite)
        u = recordtype_coll_uri(self.testsite, coll_id="testcoll", type_id="testtype")
        self.assertEqual(t._entitytype,     ANNAL.CURIE.Type)
        self.assertEqual(t._entityfile,     layout.TYPE_META_FILE)
        self.assertEqual(t._entityref,      layout.META_TYPE_REF)
        self.assertEqual(t._entityid,       "testtype")
        self.assertEqual(t._entityuri,      u)
        self.assertEqual(t._entitydir,      recordtype_dir(type_id="testtype"))
        self.assertEqual(t._values,         None)
        return

    def test_recordtype1_data(self):
        t = RecordType(self.testcoll, "type1", self.testsite)
        self.assertEqual(t.get_id(), "type1")
        self.assertEqual(t.get_type_id(), "_type")
        self.assertIn("/c/testcoll/_annalist_collection/types/type1/", t.get_uri())
        self.assertEqual(TestBaseUri + "/c/testcoll/d/_type/type1/", t.get_view_uri())
        t.set_values(recordtype_create_values(type_id="type1"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordtype_value_keys()))
        v = recordtype_values(type_id="type1")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordtype2_data(self):
        t = RecordType(self.testcoll, "type2", self.testsite)
        self.assertEqual(t.get_id(), "type2")
        self.assertEqual(t.get_type_id(), "_type")
        self.assertIn("/c/testcoll/_annalist_collection/types/type2/", t.get_uri())
        self.assertEqual(TestBaseUri + "/c/testcoll/d/_type/type2/", t.get_view_uri())
        t.set_values(recordtype_create_values(type_id="type2"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordtype_value_keys()))
        v = recordtype_values(type_id="type2")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordtype_create_load(self):
        t  = RecordType.create(self.testcoll, "type1", recordtype_create_values(type_id="type1"))
        td = RecordType.load(self.testcoll, "type1").get_values()
        v  = recordtype_read_values(type_id="type1")
        self.assertKeysMatch(td, v)
        self.assertDictionaryMatch(td, v)
        return

    def test_recordtype_default_data(self):
        t = RecordType.load(self.testcoll, "Default_type", altparent=self.testsite)
        self.assertEqual(t.get_id(), "Default_type")
        self.assertIn("/c/testcoll/_annalist_collection/types/Default_type", t.get_uri())
        self.assertEqual(t.get_type_id(), "_type")
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordtype_load_keys()))
        v = recordtype_read_values(type_id="Default_type")
        v.update(
            { 'rdfs:label':     'Default record type'
            , 'rdfs:comment':   'Default record type, applied when no type is specified when creating a record.'
            , 'annal:uri':      'annal:type/Default_type'
            })
        self.assertDictionaryMatch(td, v)
        return

#   -----------------------------------------------------------------------------
#
#   RecordTypeEditView tests
#
#   -----------------------------------------------------------------------------

class RecordTypeEditViewTest(AnnalistTestCase):
    """
    Tests for record type edit views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.user     = User.objects.create_user('testuser', 'user@test.example.com', 'testpassword')
        self.user.save()
        self.client   = Client(HTTP_HOST=TestHost)
        loggedin      = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        self.no_options = ['(no options)']
        self.continuation_uri = TestHostUri + entitydata_list_type_uri(coll_id="testcoll", type_id="_type")
        return

    def tearDown(self):
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def _create_record_type(self, type_id):
        "Helper function creates record type entry with supplied type_id"
        t = RecordType.create(self.testcoll, type_id, recordtype_create_values(type_id=type_id))
        return t    

    def _check_record_type_values(self, type_id, update="RecordType"):
        "Helper function checks content of record type entry with supplied type_id"
        self.assertTrue(RecordType.exists(self.testcoll, type_id))
        t = RecordType.load(self.testcoll, type_id)
        self.assertEqual(t.get_id(), type_id)
        self.assertEqual(t.get_view_uri(), TestHostUri + recordtype_uri("testcoll", type_id))
        v = recordtype_values(type_id=type_id, update=update)
        self.assertDictionaryMatch(t.get_values(), v)
        return t

    def _check_context_fields(self, response, 
            type_id="(?type_id)", 
            type_label="(?type_label)",
            type_help="(?type_help)",
            type_uri="(?type_uri)",
            type_view="Default_view",
            type_list="Default_list"
            ):
        r = response
        self.assertEqual(len(r.context['fields']), 6)
        # 1st field - Id
        type_id_help = (
            "A short identifier that distinguishes this type from all other types in the same collection."
            )
        self.assertEqual(r.context['fields'][0]['field_id'], 'Type_id')
        self.assertEqual(r.context['fields'][0]['field_name'], 'entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'], 'Id')
        self.assertEqual(r.context['fields'][0]['field_help'], type_id_help)
        self.assertEqual(r.context['fields'][0]['field_placeholder'], "(type id)")
        self.assertEqual(r.context['fields'][0]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][0]['field_render_view'], "field/annalist_view_entityref.html")
        self.assertEqual(r.context['fields'][0]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][0]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_value'], type_id)
        self.assertEqual(r.context['fields'][0]['options'], self.no_options)
        # 2nd field - Label
        type_label_help = (
            "Short string used to describe record type when displayed"
            )
        self.assertEqual(r.context['fields'][1]['field_id'], 'Type_label')
        self.assertEqual(r.context['fields'][1]['field_name'], 'Type_label')
        self.assertEqual(r.context['fields'][1]['field_label'], 'Label')
        self.assertEqual(r.context['fields'][1]['field_help'], type_label_help)
        self.assertEqual(r.context['fields'][1]['field_placeholder'], "(label)")
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][1]['field_render_view'], "field/annalist_view_text.html")
        self.assertEqual(r.context['fields'][1]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][1]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][1]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][1]['field_value'], type_label)
        self.assertEqual(r.context['fields'][1]['options'], self.no_options)
        # 3rd field - comment
        type_comment_help = (
            "Descriptive text about a record type"
            )
        type_comment_placeholder = (
            "(type description)"
            )
        self.assertEqual(r.context['fields'][2]['field_id'], 'Type_comment')
        self.assertEqual(r.context['fields'][2]['field_name'], 'Type_comment')
        self.assertEqual(r.context['fields'][2]['field_label'], 'Comment')
        self.assertEqual(r.context['fields'][2]['field_help'], type_comment_help)
        self.assertEqual(r.context['fields'][2]['field_placeholder'], type_comment_placeholder)
        self.assertEqual(r.context['fields'][2]['field_property_uri'], "rdfs:comment")
        self.assertEqual(r.context['fields'][2]['field_render_view'],   "field/annalist_view_textarea.html")
        self.assertEqual(r.context['fields'][2]['field_render_edit'],   "field/annalist_edit_textarea.html")
        self.assertEqual(r.context['fields'][2]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][2]['field_value_type'], "annal:Longtext")
        self.assertEqual(r.context['fields'][2]['field_value'], type_help)
        self.assertEqual(r.context['fields'][2]['options'], self.no_options)
        # 4th field - URI
        type_uri_help = (
            "Entity type URI"
            )
        type_uri_placeholder = (
            "(URI)"
            )
        self.assertEqual(r.context['fields'][3]['field_id'], 'Type_uri')
        self.assertEqual(r.context['fields'][3]['field_name'], 'Type_uri')
        self.assertEqual(r.context['fields'][3]['field_label'], 'URI')
        self.assertEqual(r.context['fields'][3]['field_help'], type_uri_help)
        self.assertEqual(r.context['fields'][3]['field_placeholder'], type_uri_placeholder)
        self.assertEqual(r.context['fields'][3]['field_property_uri'], "annal:uri")
        self.assertEqual(r.context['fields'][3]['field_render_view'],   "field/annalist_view_text.html")
        self.assertEqual(r.context['fields'][3]['field_render_edit'],   "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][3]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][3]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][3]['field_value'], type_uri)
        self.assertEqual(r.context['fields'][3]['options'], self.no_options)
        # 5th field - view id
        type_uri_help = (
            "Default view id for entity type"
            )
        type_uri_placeholder = (
            "(View Id)"
            )
        self.assertEqual(r.context['fields'][4]['field_id'], 'Type_view')
        self.assertEqual(r.context['fields'][4]['field_name'], 'Type_view')
        self.assertEqual(r.context['fields'][4]['field_label'], 'Default view id')
        self.assertEqual(r.context['fields'][4]['field_help'], type_uri_help)
        self.assertEqual(r.context['fields'][4]['field_placeholder'], type_uri_placeholder)
        self.assertEqual(r.context['fields'][4]['field_property_uri'], "annal:type_view")
        self.assertEqual(r.context['fields'][4]['field_render_view'],   "field/annalist_view_text.html")
        self.assertEqual(r.context['fields'][4]['field_render_edit'],   "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][4]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][4]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][4]['field_value'], type_view)
        self.assertEqual(r.context['fields'][4]['options'], self.no_options)
        # 6th field - list id
        type_uri_help = (
            "Default list id for entity type"
            )
        type_uri_placeholder = (
            "(List Id)"
            )
        self.assertEqual(r.context['fields'][5]['field_id'], 'Type_list')
        self.assertEqual(r.context['fields'][5]['field_name'], 'Type_list')
        self.assertEqual(r.context['fields'][5]['field_label'], 'Default list id')
        self.assertEqual(r.context['fields'][5]['field_help'], type_uri_help)
        self.assertEqual(r.context['fields'][5]['field_placeholder'], type_uri_placeholder)
        self.assertEqual(r.context['fields'][5]['field_property_uri'], "annal:type_list")
        self.assertEqual(r.context['fields'][5]['field_render_view'],   "field/annalist_view_text.html")
        self.assertEqual(r.context['fields'][5]['field_render_edit'],   "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][5]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][5]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][5]['field_value'], type_list)
        self.assertEqual(r.context['fields'][5]['options'], self.no_options)
        return

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_get_form_rendering(self):
        u = entitydata_edit_uri("new", "testcoll", "_type", view_id="Type_view")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # log.info(r.content)
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>'_type' data in collection 'testcoll'</h3>")
        formrow1 = """
            <div class="small-12 medium-6 columns">
                <div class="row">
                    <div class="view_label small-12 medium-4 columns">
                        <p>Id</p>
                    </div>
                    <div class="small-12 medium-8 columns">
                        <input type="text" size="64" name="entity_id" value="00000001"/>
                    </div>
                </div>
            </div>
            """
        formrow2 = """
            <div class="small-12 columns">
                <div class="row">
                    <div class="view_label small-12 medium-2 columns">
                        <p>Label</p>
                    </div>
                    <div class="small-12 medium-10 columns">
                        <input type="text" size="64" name="Type_label" value="Entity &#39;00000001&#39; of type &#39;_type&#39; in collection &#39;testcoll&#39;"/>
                    </div>
                </div>
            </div>
            """
        formrow3 = """
            <div class="small-12 columns">
                <div class="row">
                    <div class="view_label small-12 medium-2 columns">
                        <p>Comment</p>
                    </div>
                    <div class="small-12 medium-10 columns">
                                <textarea cols="64" rows="6" name="Type_comment" class="small-rows-4 medium-rows-8"></textarea>
                    </div>
                </div>
            </div>
            """
        formrow4 = """
            <div class="small-12 columns">
                <div class="row">
                    <div class="view_label small-12 medium-2 columns">
                        <p>URI</p>
                    </div>
                    <div class="small-12 medium-10 columns">
                        <input type="text" size="64" name="Type_uri" value="http://test.example.com/testsite/c/testcoll/d/_type/00000001/"/>
                    </div>
                </div>
            </div>
            """
        formrow5 = """
            <div class="row">
                <div class="small-2 columns">
                </div>
                <div class="small-12 medium-10 columns">
                    <div class="row">
                        <div class="small-12 columns text-right">
                            <input type="submit" name="save"          value="Save" />
                            <input type="submit" name="cancel"        value="Cancel" />
                        </div>
                    </div>
                </div>
            </div>
            """
        self.assertContains(r, formrow1, html=True)
        self.assertContains(r, formrow2, html=True)
        self.assertContains(r, formrow3, html=True)
        self.assertContains(r, formrow4, html=True)
        self.assertContains(r, formrow5, html=True)
        return

    def test_get_new(self):
        u = entitydata_edit_uri("new", "testcoll", "_type", view_id="Type_view")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        type_uri = entity_uri(type_id="_type", entity_id="00000001")
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_type")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['entity_uri'],       TestHostUri + type_uri)
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        # Fields
        self._check_context_fields(r, 
            type_id="00000001",
            type_label="Entity '00000001' of type '_type' in collection 'testcoll'",
            type_help="",
            type_uri=TestHostUri + recordtype_uri("testcoll", "00000001")
            )
        return

    def test_get_copy(self):
        u = entitydata_edit_uri("copy", "testcoll", "_type", entity_id="Default_type", view_id="Type_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_type")
        self.assertEqual(r.context['entity_id'],        "Default_type")
        self.assertEqual(r.context['orig_id'],          "Default_type")
        self.assertEqual(r.context['entity_uri'],       "annal:type/Default_type")
        self.assertEqual(r.context['action'],           "copy")
        self.assertEqual(r.context['continuation_uri'], "")
        # Fields
        self._check_context_fields(r, 
            type_id="Default_type",
            type_label="Default record type",
            type_help="Default record type, applied when no type is specified when creating a record.",
            type_uri="annal:type/Default_type"
            )
        return

    def test_get_copy_not_exists(self):
        u = entitydata_edit_uri("copy", "testcoll", "_type", entity_id="notype", view_id="Type_view")
        r = self.client.get(u)
        # log.info(r.content)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        self.assertContains(r, "<p>Entity &#39;notype&#39; of type &#39;_type&#39; in collection &#39;testcoll&#39; does not exist</p>", status_code=404)
        return

    def test_get_edit(self):
        u = entitydata_edit_uri("edit", "testcoll", "_type", entity_id="Default_type", view_id="Type_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_type")
        self.assertEqual(r.context['entity_id'],        "Default_type")
        self.assertEqual(r.context['orig_id'],          "Default_type")
        self.assertEqual(r.context['entity_uri'],       "annal:type/Default_type") # @@TODO: is this right?
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_uri'], "")
        # Fields
        self._check_context_fields(r, 
            type_id="Default_type",
            type_label="Default record type",
            type_help="Default record type, applied when no type is specified when creating a record.",
            type_uri="annal:type/Default_type"
            )
        return

    def test_get_edit_not_exists(self):
        u = entitydata_edit_uri("edit", "testcoll", "_type", entity_id="notype", view_id="Type_view")
        r = self.client.get(u)
        # log.info(r.content)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        self.assertContains(r, "<p>Entity &#39;notype&#39; of type &#39;_type&#39; in collection &#39;testcoll&#39; does not exist</p>", status_code=404)
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new type --------

    def test_post_new_type(self):
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        f = recordtype_entity_view_form_data(type_id="newtype", action="new", update="RecordType")
        u = entitydata_edit_uri("new", "testcoll", "_type", view_id="Type_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_uri)
        # Check that new record type exists
        self._check_record_type_values("newtype", update="RecordType")
        return

    def test_post_new_type_cancel(self):
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        f = recordtype_entity_view_form_data(
            type_id="newtype", action="new", cancel="Cancel", update="Updated RecordType"
            )
        u = entitydata_edit_uri("new", "testcoll", "_type", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_uri)
        # Check that new record type still does not exist
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        return

    def test_post_new_type_missing_id(self):
        f = recordtype_entity_view_form_data(action="new", update="RecordType")
        u = entitydata_edit_uri("new", "testcoll", "_type", view_id="Type_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        # Test context
        expect_context = recordtype_entity_view_context_data(action="new", update="RecordType")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_new_type_invalid_id(self):
        f = recordtype_entity_view_form_data(
            type_id="!badtype", orig_id="orig_type_id", action="new", update="RecordType"
            )
        u = entitydata_edit_uri("new", "testcoll", "_type", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        # Test context
        expect_context = recordtype_entity_view_context_data(
            type_id="!badtype", orig_id="orig_type_id", action="new", update="RecordType"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    #   -------- copy type --------

    def test_post_copy_type(self):
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        f = recordtype_entity_view_form_data(
            type_id="copytype", orig_id="Default_type", action="copy", update="RecordType"
            )
        u = entitydata_edit_uri("copy", "testcoll", "_type", entity_id="Default_type", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_uri)
        # Check that new record type exists
        self._check_record_type_values("copytype", update="RecordType")
        return

    def test_post_copy_type_cancel(self):
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        f = recordtype_entity_view_form_data(
            type_id="copytype", orig_id="Default_type", action="copy", cancel="Cancel", update="RecordType"
            )
        u = entitydata_edit_uri("copy", "testcoll", "_type", entity_id="Default_type", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_uri)
        # Check that target record type still does not exist
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        return

    def test_post_copy_type_missing_id(self):
        f = recordtype_entity_view_form_data(
            action="copy", update="Updated RecordType"
            )
        u = entitydata_edit_uri("copy", "testcoll", "_type", entity_id="Default_type", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        expect_context = recordtype_entity_view_context_data(action="copy", update="Updated RecordType")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_copy_type_invalid_id(self):
        f = recordtype_entity_view_form_data(
            type_id="!badtype", orig_id="Default_type", action="copy", update="Updated RecordType"
            )
        u = entitydata_edit_uri("copy", "testcoll", "_type", entity_id="Default_type", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        expect_context = recordtype_entity_view_context_data(
            type_id="!badtype", orig_id="Default_type", 
            action="copy", update="Updated RecordType"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    #   -------- edit type --------

    def test_post_edit_type(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        f = recordtype_entity_view_form_data(
            type_id="edittype", orig_id="edittype", 
            action="edit", update="Updated RecordType"
            )
        u = entitydata_edit_uri("edit", "testcoll", "_type", entity_id="edittype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_uri)
        # Check that new record type exists
        self._check_record_type_values("edittype", update="Updated RecordType")
        return

    def test_post_edit_type_new_id(self):
        self._create_record_type("edittype1")
        self._check_record_type_values("edittype1")
        f = recordtype_entity_view_form_data(
            type_id="edittype2", orig_id="edittype1", 
            action="edit", update="Updated RecordType"
            )
        u = entitydata_edit_uri("edit", "testcoll", "_type", entity_id="edittype1", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_uri)
        # Check that new record type exists and old does not
        self.assertFalse(RecordType.exists(self.testcoll, "edittype1"))
        self._check_record_type_values("edittype2", update="Updated RecordType")
        return

    def test_post_edit_type_cancel(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        f = recordtype_entity_view_form_data(
            type_id="edittype", orig_id="edittype", 
            action="edit", cancel="Cancel", update="Updated RecordType"
            )
        u = entitydata_edit_uri("edit", "testcoll", "_type", entity_id="edittype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_uri)
        # Check that target record type still does not exist and unchanged
        self._check_record_type_values("edittype")
        return

    def test_post_edit_type_missing_id(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        # Form post with ID missing
        f = recordtype_entity_view_form_data(
            action="edit", update="Updated RecordType"
            )
        u = entitydata_edit_uri("edit", "testcoll", "_type", entity_id="edittype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        # Test context for re-rendered form
        expect_context = recordtype_entity_view_context_data(action="edit", update="Updated RecordType")
        self.assertDictionaryMatch(r.context, expect_context)
        # Check original data is unchanged
        self._check_record_type_values("edittype")
        return

    def test_post_edit_type_invalid_id(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        # Form post with invalid ID
        f = recordtype_entity_view_form_data(
            type_id="!badtype", orig_id="edittype", action="edit", update="Updated RecordType"
            )
        u = entitydata_edit_uri("edit", "testcoll", "_type", entity_id="edittype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        # Test context
        expect_context = recordtype_entity_view_context_data(
            type_id="!badtype", orig_id="edittype", 
            action="edit", update="Updated RecordType"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        # Check original data is unchanged
        self._check_record_type_values("edittype")
        return

#   -----------------------------------------------------------------------------
#
#   ConfirmRecordTypeDeleteTests tests for completion of record deletion
#
#   -----------------------------------------------------------------------------

class ConfirmRecordTypeDeleteTests(AnnalistTestCase):
    """
    Tests for record type deletion on response to confirmation form
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.user = User.objects.create_user('testuser', 'user@test.example.com', 'testpassword')
        self.user.save()
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        return

    def test_CollectionActionViewTest(self):
        self.assertEqual(RecordTypeDeleteConfirmedView.__name__, "RecordTypeDeleteConfirmedView", "Check RecordTypeDeleteConfirmedView class name")
        return

    # NOTE:  test_collection checks the appropriate response from clicking the delete button, 
    # so here only need to test completion code.
    def test_post_confirmed_remove_type(self):
        t = RecordType.create(self.testcoll, "deletetype", recordtype_create_values("deletetype"))
        self.assertTrue(RecordType.exists(self.testcoll, "deletetype"))
        # Submit positive confirmation
        u = TestHostUri + recordtype_edit_uri("delete", "testcoll")
        f = recordtype_delete_confirm_form_data("deletetype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,     302)
        self.assertEqual(r.reason_phrase,   "FOUND")
        self.assertEqual(r.content,         "")
        self.assertMatch(r['location'],    
            "^"+TestHostUri+
            collection_edit_uri("testcoll")+
            r"\?info_head=.*&info_message=.*deletetype.*testcoll.*$"
            )
        # Confirm deletion
        self.assertFalse(RecordType.exists(self.testcoll, "deletetype"))
        return

# End.
