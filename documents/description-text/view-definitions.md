View definitions:  this file contains the unencoded help text for Annalist site-defined view descriptions.

To embed these definitions into the site data:

1. Edit the corresponding view and paste the relevant text into the comment/help field
2. Save the view definition
3. View the JSON for the view definition
4. Copy the definition for the `rdfs:comment` field
5. Paste the definition into the corresponding site data `view-meta.jsonld` file.

----

# Collection metadata view

Presents metadata about a collection.

A collection metadata view may be displayed by selecting a collection from the site front page, and clicking on **View metadata** or **Edit metadata**.

## Fields

[Id](/annalist/c/_annalist_site/d/_field/Entity_id/):
Collection identifier, which appears on the Annalist site front page.
 
[S/W version](/annalist/c/_annalist_site/d/_field/.../):
Software version compatibility:  the oldest version of Annalist software with which the collection is compatible.  This value is maintained by the Annalist software, and may be updated whenever any value in a collection is updated.

[Label](/annalist/c/_annalist_site/d/_field/Entity_label/):
Collection descriptive label, which appears on the Annalist site front page.

[Comment](/annalist/c/_annalist_site/d/_field/Entity_comment/):
Extended description of the collection.  This appears on the collection editing (Customize) page.

[Parent](/annalist/c/_annalist_site/d/_field/Coll_parent/):
a parent collection, from which type, view and other definitions are inherited.  This allows new collections to be quickly created using predefined types, views, fields, etc.  These inherited definitions may be edited, resulting in new instances being created within the active collection.

[Default list](/annalist/c/_annalist_site/d/_field/Coll_default_list_id/):
default list for viewing collection.  Overridden by **Default view**, but even then is accessible using a URL of the form **/annalist/*collection*/l/**.  This value is set by clicking **Set default** in an explicitly chosen list view.

[Default view](/annalist/c/_annalist_site/d/_field/Coll_default_view_id/):
default view for showing collection content, used in conjuction with **Default view type** and **Default view entity**.  If specified, the indiocated entity view is used inplace of the **Default list** as the front page for an Annalist collection.  This allows a view to be created that proviodes a more useful description and overview of the collection, including links to key elements, than that which is otherwise generated by Annalist.  This value is set by clicking **Set default view** in any entity view.

[Default view type](/annalist/c/_annalist_site/d/_field/.../):
default view entity type - see **Default view**.

[Default view entity](/annalist/c/_annalist_site/d/_field/.../):
default view entity id - see **Default view**.

[Collection metadata](/annalist/c/_annalist_site/d/_field/.../):
description of Collection metadata creation details - this is used for maintanance purposes to provide an indication of the provenance of the collection metadata, and can be ignored for most purposes.


----

# Default record view

Default view applied when no view is specified when creating a record.

This view defines a minimal set of fields that are generally presumed to be present in all records: a record Id, a record type, a short label and a comment that can be used to provide an extended description.  For site data, the comment is used to populate interactive help information.

This view can also be used to change the type of a record.

## Fields:

[Id](/annalist/c/_annalist_site/d/_field/Entity_id/):
entity identifier.

[Type](/annalist/c/_annalist_site/d/_field/Entity_type/):
type of entity record.

[Label](/annalist/c/_annalist_site/d/_field/Entity_label/):
short label used to describe this entity.

[Comment](/annalist/c/_annalist_site/d/_field/Entity_comment/):
extended text description of this entity.
Uses Markdown for formatting.


----

# Field group definition view

Form used for viewing and editing field groups of fields used in a form to define an optional or repeating field group (render type `RepeatGroup` or `RepeatGroupRow`), or to present specified fields from a referenced entity (render type `RefMultifield`).

Used to view instances of type [Field group](/annalist/c/_annalist_site/d/_type/_group).

## Fields:

[Id](/annalist/c/_annalist_site/d/_field/Group_id/):
field group identifier

[Label](/annalist/c/_annalist_site/d/_field/Group_label/):
short label used to describe this field group.

[Help](/annalist/c/_annalist_site/d/_field/Group_comment/):
extended text description of this field group.
Uses Markdown for formatting.

[Record type](/annalist/c/_annalist_site/d/_field/Group_target_type/):
if specified, indicates a record type (URI or CURIE) to which this field group applies.  If not specified (blank), the field group is considered to be applicable to any record type.

[Fields](/annalist/c/_annalist_site/d/_field/Group_fields/):
a list of one of more field references, with optional properties (URIs or CURIEs) and layout position/size indicator.  If the property and/or positioning values are not specified, values from the referenced field definition are used.


----

# Field definition view

Form used for viewing and editing field definitions that may be used in a [View](/annalist/c/_annalist_site/d/_type/_view), [List](/annalist/c/_annalist_site/d/_type/_list) or [Field group](/annalist/c/_annalist_site/d/_type/_group) definition.

Used to view instances of type [View field](/annalist/c/_annalist_site/d/_type/_field).

Field definitions are a key element of Annalist mechanisms for presenting and editing data records. There are many fields, many of which used only in support of particular presentation options, and are otherwise ignored.

## Common fields (applicable to all field render types)

[Id](/annalist/c/_annalist_site/d/_field/Field_id/): 
Field identifier: used internally to identify a particular field definition, and also to name value fields on HTML forms used to present the data.

[Field render type](/annalist/c/_annalist_site/d/_field/Field_render/):
indicates a renderer that is used for presentation of this fields.  The value selected here controls both the format of the stored data, and how it is presented on the form for editing and viewing.  A list of available field render types can viewed at [_annalist_site/d/Enum_render_type/](/annalist/c/_annalist_site/d/Enum_render_type/)

[Field value type](/annalist/c/_annalist_site/d/_field/Field_type/): 
URI or CURIE for type of value displayed by this field.  (Currently not much used, if at all, but intended to eventually provide data type URIs for literals in JSON-LD/RDF data generated by Annalist.)

[Value mode](/annalist/c/_annalist_site/d/_field/Field_value_mode/):
indicates how the displayed value is accessed.  One of [Direct value](/annalist/c/_annalist_site/d/Enum_value_mode/Value_direct/), [Entity reference](/annalist/c/_annalist_site/d/Enum_value_mode/Value_entity/), [Field reference](/annalist/c/_annalist_site/d/Enum_value_mode/Value_field/), [Import from web](/annalist/c/_annalist_site/d/Enum_value_mode/Value_import/), [File upload](/annalist/c/_annalist_site/d/Enum_value_mode/Value_upload/).  If in doubt, use **Direct value**.

[Label](/annalist/c/_annalist_site/d/_field/Field_label/): 
short label used to describe this field.

[Help](/annalist/c/_annalist_site/d/_field/Field_comment/): longer text description of this field.  Intended to be used to generate online help messages to assist user data entry.
Uses Markdown for formatting.

[Property](/annalist/c/_annalist_site/d/_field/Field_property/): a URI or CURIE that is used as a key for the corresponding value in saved JSON data, and also as an property URI for data exported as RDF.

[Position/Size](/annalist/c/_annalist_site/d/_field/Field_placement/):
indicates field placement on a displayed page.  A number of options are presented, annoted with "(*pos*/*wid*)", "(*pos*/*wid* right)" or "(*pos*/*wid* column)".  The placement is based on a 12-column grid, where *pos* is the start column for the field, and *wid* is the number of columns occupied on a medium or larger display.  On small displays, all fields occupy the entire display width unless the placement includes the "columns" annotation.  The "right" annotation is intended for righjt justification of columns that appear at the end of a row, but has been rarely used in practice.

[Default](/annalist/c/_annalist_site/d/_field/Field_default/):
Default value for this field.  Leave blank if there is no default value.

[Entity type](/annalist/c/_annalist_site/d/_field/Field_entity_type/):
Type (URI or CURIE) of entity type (or supertype) for which the field is applicable. Used to determine entities for which the field type is offered as an option.  Leave blank if the field is to be available for all entity types.

## Text entry fields

[Placeholder](/annalist/c/_annalist_site/d/_field/Field_placeholder/):
String value used as a placeholder for text entry fields. Use this to proviode a prompt or example of input that may be entered.  (The Annalist site data follows a convention of putting parentheses around placeholder text, but this is not a requirement.)

## Entity reference fields

Some fields contain a cross-reference to anothere entity.  The following apply to descriptions of such fields.

[Refer to type](/annalist/c/_annalist_site/d/_field/Field_typeref/):
The URI or CURIE of the type (or supertype) to which the field value refers.  This is used to select values that are offered in a dropdown list for selection.  (If subsequent renaming means a selected value no longer exists, the specified value type and id are displayed.)

[Refer to field](/annalist/c/_annalist_site/d/_field/Field_fieldref/):
The URI or CURIE of a property URI that keys a field of a referenced record.  Ther indicated field is displayed when viewing an entity, but an entity selection dropdown is provided.  (Not currently used - use of the [Fields of referenced entity](/annalist/c/_annalist_site/d/Enum_render_type/RefMultifield/) renderer is generally prefered.)

[Value restriction](/annalist/c/_annalist_site/d/_field/Field_restrict/): a selection filter expression that restricts the values that are offered as options for the displayed field.  

## Repeating value fields

[Field group](/annalist/c/_annalist_site/d/_field/Field_groupref/): indicates a field group that is used to display repeated values.

[Add fields label](/annalist/c/_annalist_site/d/_field/Field_repeat_label_add/):
a text label for the button used to add new repeating value entries.

[Delete fields label](/annalist/c/_annalist_site/d/_field/Field_repeat_label_delete/):
a text label for the button used to remove an existing entry.

## Multi-field references

[Field group](/annalist/c/_annalist_site/d/_field/Field_groupref/):
indicates a field group that is used to display values from a referenced entity.


----

# List definition view

Form used for viewing and editing list definitions.

Used to view instances of type [List](/annalist/c/_annalist_site/d/_type/_list).

## Fields

[Id](/annalist/c/_annalist_site/d/_field/List_id/):
list identifier.

[List display type](/annalist/c/_annalist_site/d/_field/List_type/):
type of list display (List or Grid).  @@Not yet implemented@@

[Label](/annalist/c/_annalist_site/d/_field/List_label/):
short label used to describe this list.

[Help](/annalist/c/_annalist_site/d/_field/List_comment/):
extended text description of this list.
Uses Markdown for formatting.

[Record type](/annalist/c/_annalist_site/d/_field/List_default_type/):
Default entity type associated with this list. This is used for constructing a default record selector (i.e. all records of specified type), and also when creating a new entity from the list view.

[View](/annalist/c/_annalist_site/d/_field/List_default_view/):
Default view used when displaying, editing or creating records from this list view. (Note that record lists are not tied to a specific entity type. See also field **List_record_type**.)

[Selector](/annalist/c/_annalist_site/d/_field/List_entity_selector/):
An expression that is used to select entities to be included in the list view.  If not specified, a default selector is used that selects all records from the current collection that are of the indicated default record type (including subtypes).

[Record type URI](/annalist/c/_annalist_site/d/_field/List_target_type/):
Type (URI or CURIE) of entities displayed using this list. Used to determine field choices appropriate to this list view.  If not specified, only those fields applicable to all entity types are displayted when editing the list definition.

[Fields](/annalist/c/_annalist_site/d/_field/List_fields/):
Selects the fields and corresponding entity values that are included in the list display.


----

# Type definition view

Form used for viewing and editing type definitions.

Used to view instances of type [Type](/annalist/c/_annalist_site/d/_type/_type).

## Fields

[Id](/annalist/c/_annalist_site/d/_field/Type_id/):
type identifier.

[Label](/annalist/c/_annalist_site/d/_field/Type_label/):
short label used to describe this type.

[Comment](/annalist/c/_annalist_site/d/_field/Type_comment/):
extended text description of this type.
Uses Markdown for formatting.

[URI](/annalist/c/_annalist_site/d/_field/Type_uri/):
entity type URI or CURIE.  This URI is associated with instances of this type when published to the web as linked data.  The string used is also used as a basis for selecting subtypes of this type (see also field **Supertype URIs**)

[Supertype URIs](/annalist/c/_annalist_site/d/_field/Type_supertype_uris/):
list of URIs or CURIEs of supertypes of the current type. These are additional type URIs associated with instances of this type when published to the web as linked data.  The URI/CURIE strings are also used for detecting other types of which the current type is a subtype.

[Default view](/annalist/c/_annalist_site/d/_field/Type_view/):
Default view for presenting instances of this type.

[Default list](/annalist/c/_annalist_site/d/_field/Type_list/):
Default list for instances of this type. 

[Field aliases](/annalist/c/_annalist_site/d/_field/Type_aliases/):
A list of field aliases that may be associated with a type. That is, field values that may be returned based on some property URI other than the one associated with the field. One motivating case for this is to allow fields associated with different properties to be associated with entity labels (rdfs:label), which are used by many generic views.  The alias mechanism has also been used to implement a limited form of "superproperty URI", which can be useful for creating a unified view over disparate field types, such as linked and upoaded images.

Each alias is associated with a pair of *target* and *source* property URIs or CURIEs.  When field definition uses the *target* URI, the entity field value at the *source* URI may be used.

@@move some of this detail into the field description@@


----

# User permissions view

Form used for defining user permissions, which are the basis of Annalist access control.

Used to view instances of type [User permissions](/annalist/c/_annalist_site/d/_type/_user).

User permissions are associated with a combination of a **User Id** and a **URI**.

The **User id** is arbitrary, and can be any token specified by the user when they log in.

The URI is derived from a separate user authentication service, and usually takes the form of a `mailto:` URI with an authenticated email address for the user.  For example, when authentication is performed using Google, the email address which associated with the Google login Google is used.

## Fields

[Id](/annalist/c/_annalist_site/d/_field/User_id/):
Short user Id string.

[User name](/annalist/c/_annalist_site/d/_field/User_name/):
the name of the user, consisting of first_name and last_name, spare-separated.  The value is quite arbitrary, and is used only for constructing some messages.

[Description](/annalist/c/_annalist_site/d/_field/User_description/):
an optional descriptive string describing the user, their role and/or permissions.

[URI](/annalist/c/_annalist_site/d/_field/User_URI/):
A URI that has an authenticated association with the user.  Usually, a `mailto:` URI containing an authenticated email addreess.

[Permissions](/annalist/c/_annalist_site/d/_field/User_permissions/):
a space-separated list of user permission tokens; e.g 'VIEW CREATE UPDATE DELETE CONFIG'. User permissions are typically defined for each collection, but, may also be site-wide if they are defined as part of the `_annalist_site` collection, in which case they are applied in any collection for which more specific permissions are niot defined. 

Currently recognized permission tokens include:

* `ADMIN` - permits user administration and permission assignment.  As a site-wide permission, also permits creating new collections, and deleting existing ones.
* `CREATE_COLLECTION` - as a site-wide permission, permits creating new collections.  Any created collections automatically grant `ADMIN` permission to the user who creates them.
* `DELETE_COLLECTION` - as a site-wide permission, permits deletion of any collection.
* `CONFIG` - permits definition and modification of collection structures in the form of types, views, lists, fields, etc.
* `VIEW` - permits viewing of data records.
* `CREATE` - permits creation of new data records.
* `UPDATE` - permits modification of existing data records.
* `DELETE` - permits deletion of existing datra reciords.

Site wide permissions are listed at [_annalist_site/l/User_list/](/annalist/c/_annalist_site/l/User_list/).


----

# View definition view

Form used for viewing and editing view definitions.

Used to view instances of type [View](/annalist/c/_annalist_site/d/_type/_view).


## Fields

[Id](/annalist/c/_annalist_site/d/_field/View_id/):
view identifier.

[Label](/annalist/c/_annalist_site/d/_field/View_label/):
short label used to describe this view.

[Help](/annalist/c/_annalist_site/d/_field/View_comment/):
extended text description of this view.
Uses Markdown for formatting.

[Record type](/annalist/c/_annalist_site/d/_field/View_target_type/):
type (URI or CURIE) of entities displayed using this view. Used in determining field choices appropriate to this view definition.  If not defined, only field types applicabvle to all types are offered.

[Editable view?](/annalist/c/_annalist_site/d/_field/View_edit_view/):
if selected, an **Edit view** button is provided while editing an entity, and **View description** while viewing an entity.  These options provide access to the view forms to define the entity view and editing interface.

(This option is view-specific: built-in views are not intended to be edited and do not present an 'Edit view' button. Subject to permissions, any view description can always be edited directly.)

[Fields](/annalist/c/_annalist_site/d/_field/View_fields/):
a list of one of more field references, with optional property URIs or CURIEs, and layout position/size indicator.  If the property and/or positioning values are not specified, values from the referenced field definition are used.


----

# Vocabulary namespace definition view

Form used for viewing and editing vocabulary namespace definitions.

Used to view instances of type [Vocabulary namespace](/annalist/c/_annalist_site/d/_type/_vocab).

A vocabulary namespace is a set of URIs used to identify a group of related concepts, where all the URIs have a common leading URI part.  The namespace identifier is also used as a prefix in CURIEs representing terms from the namespace.

# Fields

[Id](/annalist/c/_annalist_site/d/_field/Entity_id/):
namespace identifier, also used for the prefix part of CURIEs.

[Label](/annalist/c/_annalist_site/d/_field/Entity_label/):
short label used to describe this view.

[Comment](/annalist/c/_annalist_site/d/_field/Entity_comment/):
extended text description of this namespace.
Uses Markdown for formatting.

[Vocabulary URI](/annalist/c/_annalist_site/d/_field/Entity_.../):
a vocabulary namespace URI.  All terms in the namespace have URIs that start with this URI.  Whenh a CURIE is converted to a UREI, the prefix partr is replaced with the URI string, which, when concatenated with the CURIE local part, yields the corresponding full vocabulary term URI.

[See also](/annalist/c/_annalist_site/d/_field/Entity_.../):
a list of links to information related to the namespace; e.g. specification documents, schemas, etc.


----


@@@@@@ when all done, copy comment JSON from each view to the sitedatas
@@@@@@ at same time, check all view labels