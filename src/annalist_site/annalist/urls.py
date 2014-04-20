"""
Annalist application URL definitions
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from django.conf.urls               import patterns, url

from annalist.views.home            import AnnalistHomeView
from annalist.views.profile         import ProfileView
from annalist.views.confirm         import ConfirmView
from annalist.views.site            import SiteView, SiteActionView
from annalist.views.collection      import CollectionView, CollectionEditView
from annalist.views.recordtype      import RecordTypeDeleteConfirmedView
# from annalist.views.recordview      import RecordViewEditView # , RecordViewDeleteConfirmedView
# from annalist.views.recordlist      import RecordListEditView # , RecordListDeleteConfirmedView
# from annalist.views.recordfield     import RecordFieldEditView # , RecordFieldDeleteConfirmedView
from oauth2.views                   import LoginUserView, LoginPostView, LoginDoneView, LogoutUserView

from annalist.views.defaultlist     import EntityDefaultListView
from annalist.views.defaultedit     import EntityDefaultEditView

from annalist.views.entityedit      import GenericEntityEditView
from annalist.views.entitylist      import EntityGenericListView
from annalist.views.entitydelete    import EntityDataDeleteConfirmedView

# @@TODO: Review URI design: 1-letter path segments:
#
# c - collections
# v - view
# l - list
# d - data/default view
#
# Metadata:
#
# /c/<coll-id>/types/                             list of record types
# /c/<coll-id>/types/<type-id>                    view of type description
# /c/<coll-id>/views/                             list of record views
# /c/<coll-id>/views/<view-id>                    view of view description
# /c/<coll-id>/lists/                             list of record lists
# /c/<coll-id>/lists/<list-id>                    view of list description
#
# Data:
#
# /c/<coll-id>/d/                                 default list of records
# /c/<coll-id>/d/<type-id>/                       default list of records of specified type
# /c/<coll-id>/d/<type-id>/<entity-id>            default view of identified entity
# /c/<coll-id>/l/<list-id>/                       specified list of records
# /c/<coll-id>/l/<list-id>/<type-id>              specified list of records of specified type
# /c/<coll-id>/v/<view-id>/<type-id>/<entity-id>  specified view of record

urlpatterns = patterns('',
    url(r'^$',              AnnalistHomeView.as_view(), name='AnnalistHomeView'),
    url(r'^site/$',         SiteView.as_view(),         name='AnnalistSiteView'),
    url(r'^site/!action$',  SiteActionView.as_view(),   name='AnnalistSiteActionView'),
    url(r'^profile/$',      ProfileView.as_view(),      name='AnnalistProfileView'),
    url(r'^confirm/$',      ConfirmView.as_view(),      name='AnnalistConfirmView'),

    url(r'^c/(?P<coll_id>\w{0,32})/$',
                            CollectionView.as_view(),
                            name='AnnalistCollectionView'),
    url(r'^c/(?P<coll_id>\w{0,32})/!edit$',
                            CollectionEditView.as_view(),
                            name='AnnalistCollectionEditView'),
    url(r'^c/(?P<coll_id>\w{0,32})/_annalist_collection/types/!delete_confirmed$',
                            RecordTypeDeleteConfirmedView.as_view(),
                            name='AnnalistRecordTypeDeleteView'),

    # url(r'^c/(?P<coll_id>\w{0,32})/_annalist_collection/types/(?P<type_id>\w{0,32})/$',
    #                         RecordTypeEditView.as_view(),
    #                         name='AnnalistRecordTypeAccessView'),
    # url(r'^c/(?P<coll_id>\w{0,32})/_annalist_collection/types/!(?P<action>new)$',
    #                         RecordTypeEditView.as_view(),
    #                         name='AnnalistRecordTypeNewView'),
    # url(r'^c/(?P<coll_id>\w{0,32})/_annalist_collection/types/(?P<type_id>\w{0,32})/!(?P<action>copy)$',
    #                         RecordTypeEditView.as_view(),
    #                         name='AnnalistRecordTypeCopyView'),
    # url(r'^c/(?P<coll_id>\w{0,32})/_annalist_collection/types/(?P<type_id>\w{0,32})/!(?P<action>edit)$',
    #                         RecordTypeEditView.as_view(),
    #                         name='AnnalistRecordTypeEditView'),
    # url(r'^c/(?P<coll_id>\w{0,32})/_annalist_collection/types/!delete_confirmed$',
    #                         RecordTypeDeleteConfirmedView.as_view(),
    #                         name='AnnalistRecordTypeDeleteView'),

    # url(r'^c/(?P<coll_id>\w{0,32})/_annalist_collection/views/(?P<view_id>\w{0,32})/$',
    #                         RecordViewEditView.as_view(),
    #                         name='AnnalistRecordViewAccessView'),

    # url(r'^c/(?P<coll_id>\w{0,32})/_annalist_collection/lists/(?P<list_id>\w{0,32})/$',
    #                         RecordListEditView.as_view(),
    #                         name='AnnalistRecordListAccessView'),

    # url(r'^c/(?P<coll_id>\w{0,32})/_annalist_collection/fields/(?P<field_id>\w{0,32})/$',
    #                         RecordFieldEditView.as_view(),
    #                         name='AnnalistRecordFieldAccessView'),

    url(r'^c/(?P<coll_id>\w{0,32})/d/$',
                            EntityDefaultListView.as_view(),
                            name='AnnalistEntityDefaultListAll'),
    url(r'^c/(?P<coll_id>\w{0,32})/d/(?P<type_id>\w{0,32})/$',
                            EntityDefaultListView.as_view(),
                            name='AnnalistEntityDefaultListType'),

    url(r'^c/(?P<coll_id>\w{0,32})/d/(?P<type_id>\w{0,32})/!delete_confirmed$',
                            EntityDataDeleteConfirmedView.as_view(),
                            name='AnnalistEntityDataDeleteView'),

    url(r'^c/(?P<coll_id>\w{0,32})/d/(?P<type_id>\w{0,32})/(?P<entity_id>\w{0,32})/$',
                            EntityDefaultEditView.as_view(),
                            name='AnnalistEntityAccessView'),
    url(r'^c/(?P<coll_id>\w{0,32})/d/(?P<type_id>\w{0,32})/!(?P<action>new)$',
                            EntityDefaultEditView.as_view(),
                            name='AnnalistEntityDefaultNewView'),
    url(r'^c/(?P<coll_id>\w{0,32})/d/(?P<type_id>\w{0,32})/(?P<entity_id>\w{0,32})/!(?P<action>copy)$',
                            EntityDefaultEditView.as_view(),
                            name='AnnalistEntityDefaultEditView'),
    url(r'^c/(?P<coll_id>\w{0,32})/d/(?P<type_id>\w{0,32})/(?P<entity_id>\w{0,32})/!(?P<action>edit)$',
                            EntityDefaultEditView.as_view(),
                            name='AnnalistEntityDefaultEditView'),

    url(r'^c/(?P<coll_id>\w{0,32})/l/(?P<list_id>\w{0,32})/$',
                            EntityGenericListView.as_view(),
                            name='AnnalistEntityGenericList'),
    url(r'^c/(?P<coll_id>\w{0,32})/l/(?P<list_id>\w{0,32})/(?P<type_id>\w{0,32})/$',
                            EntityGenericListView.as_view(),
                            name='AnnalistEntityGenericList'),

    url(r'^c/(?P<coll_id>\w{0,32})/v/(?P<view_id>\w{0,32})/(?P<type_id>\w{0,32})/(?P<entity_id>\w{0,32})/$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityDataView'),
    url(r'^c/(?P<coll_id>\w{0,32})/v/(?P<view_id>\w{0,32})/(?P<type_id>\w{0,32})/!(?P<action>new)$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityNewView'),
    url(r'^c/(?P<coll_id>\w{0,32})/v/(?P<view_id>\w{0,32})/(?P<type_id>\w{0,32})/(?P<entity_id>\w{0,32})/!(?P<action>copy)$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityEditView'),
    url(r'^c/(?P<coll_id>\w{0,32})/v/(?P<view_id>\w{0,32})/(?P<type_id>\w{0,32})/(?P<entity_id>\w{0,32})/!(?P<action>edit)$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityEditView'),

    )

urlpatterns += patterns('',
    url(r'^login/$',      LoginUserView.as_view(),      name='LoginUserView'),
    url(r'^login_post/$', LoginPostView.as_view(),      name='LoginPostView'),
    url(r'^login_done/',  LoginDoneView.as_view(),      name='LoginDoneView'),
    url(r'^logout/$',     LogoutUserView.as_view(),     name='LogoutUserView'),
    )

# End.
