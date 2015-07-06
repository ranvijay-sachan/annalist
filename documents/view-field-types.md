# View fields in Annalist

Annalist uses _views_ to define user-definable presentation of data for display and editing.

These views essentially consist of a list of _fields_ to be displayted from the presented entity.  Each field is defined by a number of parameters (which are themselves managed using an Annalist view, viz. `Field_view`).

This page describes the field definition parameters and in particular introduces the available field rendering types.  It also discusses additional considerations for repeated fields, and fields that reference uploaded files or imported web resources.

Note: much of field description processing is handled by modules `annalist.views.form_utils.fielddescription` and `annalist.views.fields.bound_field`, coordinated by `annalist.views.entityedit` and `annalist.views.entitylist`.

## Field description values

A field description is entered through a form with the following fields.

(Parenthesized values are field identifiers)

### Id (`Field_id`)

This is a name that is used to distinguish the fields from all available fields.  Consists of up to 32 letters, digits and/or underscore characters.  Case sensistive, but on some systems it is not possible to have different fields whose identifiers differ in upper- and lower-case letters.

### Name (`Field_name`)

Used internally to generate the name of a field in an HTML form view.  Defaults to the value of `Field_id`.

(Currently not supported in field editing view, but can be set in stored field description records. @@)

### Field value type (`Field_type`)

Type (as a URI or CURIE) of underlying data that is stored in a field.  

This field is provided as an additional information and as a hint to the field renderer;  in most cases, the value is not actually used, so it is possible that values used are not always assigned consistently.

See also the section "Field value types" below.

### Field renderer type (`Field_render`)

Identifer that indicates how the field value is rendered, indicating one of a number of available built-in field renderers.  The stored value is an 'annal:Slug', and presented as a drop-down list based on the contents of descriptions in `annalist/sitedata/enums/Enum_render_type`.

See also the section "Field render types" below.

### Position/size (`Field_placement`)

Used to specifying the position of of a field in a form display, specified in terms of width and horizontal placement on a responsive display grid <sup>1,2</sup>.

Internally, the placement is stored as a specially formatted string.  It is presenrted for viewing as a rough visual indication of the filed placement, and for  editing as a dropdown list of options.

Default placement can be specified as part of the field description, and overridden when the field is included in a particular view.

### Label (`Field_label`)

A short textual label for the field.  The label is displayed as part of the form in which the field appears.

### Help (`Field_comment`)

A longer textual description of the field.

(@@TODO: use Markdown for formatting the field description, and use the description for pop-up help text in the form)

### Placeholder (`Field_placeholder`)

A string that is presented to describe the expected field content when the field content is empty

### Property (`Field_property`)

A [CURIE](http://www.w3.org/TR/curie/) or [URI](https://tools.ietf.org/html/rfc3986) that is used to relate the field value to the containing entity.  The supplied string is used as a key value in the stored JSON.  The use of CURIE or URI formats for this key allows Annalist data to be interpreted as JSON-LD, hence as [linked data](http://linkeddata.org).

A default property CURIE or URI can be specified as part of the field description, and overridden when the field is included in a particular view.

(@@TODO: not yet implemented is management of prefix URIs and JSON-LD contexts required to fully support use as linked data)

### Default (`Field_default`)

A default value for the field if none is specified.

### Entity type (`Field_entity_type`)

Type (URI or CURIE) of entity to which field applies.

This is used to restrict the fields that are offered when editing a view or list description (see also field `View_target_type` used in view descriptions).

Many, or even most, field descriptions are specific to a particular entity type, but some are generic.  If this value is not specified, the corresponding field is offered as an option for any entity type, but if given then it is offered only when editing a view or list for the specified type.

### Enum type (`Field_typeref`)

Used with render types `Enum`, `Enum_optional` and `Enum_choice` (and also `Type`, `List`, `View`, `Field` which are sumsumed by the `Enum*` render types).

When specified, this field value is an internal type identifier.  The field is taken to be a reference to an entity of the given type, and presented for editing as a drop-down list of available values.  For viewing, the field is presented as a hyperlink to a description of the corresponding type.

### Referenced field (`Field_fieldref`)

When a field refers to some target entity, this may indicate a property CURIE or URI for a field of that entity that is used for view rendering.

See section "Resource references, imports and file uploads" for more details.

### Enum restriction (`Field_restrict`)

Selection filter to restrict enumerated values that are candidate field values, used in conjunction with field `Field_fieldref`.

This is provided mainly for internal use to implement the `Field_entity_type` feature.  If in doubt, leave this field blank.

The field value is a string expression that is used to filter candidates that are presented as members of an enumerated value.  The selection filter syntax is defined by module `annalist.models.entityfimnder`, and is used for enumerated value fields and also for generating entity list displays (cf. `List_entity_selector` field used in `List_view`).

### Field group (`Field_groupref`)

Field group reference used by `RepeatGroup` and `RepeatGroupRow` renderers.  Otherwise, it is ignored.

The value is a reference to a separately defined field group, which itself contains a list of field description references.  The group itself defines a group of fields that are repeated within a view..

The field value is presented for editing as a drop-down list, and for viewing as a hyperlink to the selected field group.

See also the section "Repeated field groups"

### Add fields label (`Field_repeat_label_add`)

Button label used by `RepeatGroup` and `RepeatGroupRow` renderers.  Otherwise, it is ignored.

See also the section "Repeated field groups"

### Delete fields label (`Field_repeat_label_delete`)

Button label used by `RepeatGroup` and `RepeatGroupRow` renderers.  Otherwise, it is ignored.

See also the section "Repeated field groups"

## Repeated field groups

Some entities contain fields or groups of fields that may be repeated an arbitrary number of times.  This repetition is described within a view description as a single field that consists of a list of values rendered using a `RepeatGroup` and `RepeatGroupRow` renderer.

Repeated field groups can also be used for optional groups of fields, by virtue of allowing zero or one repetitions.

A repeated field description contains three particular elements not used by other field descriptions:

1. a reference to a field group
2. a label for a button used to create a new repetition
3. a label for a button used to delete a repeated value

The field group is a separately defined entity that mainly consists of a list of field references, along with optional property URI and placement information which, if present, overrides the default values from the individual field descriptions.

Thus, to create a repeated field in a view, the following steps must be performed:

* Create descriptions for the individual fields that are to be repeated
* Create a field group description collecting the fields to be repeated
* Create a repeat group field with render type `RepeatGroup` or `RepeatGroupRow`, referencing the field group, and defining labels for the add/remoive buttons.
* Add the repeat group field to the view in which the repeated fields are to appear.

(@@TODO: provide a simplified interface for doing the above through a single form)

(@@TODO: reordering of fields within a group)

## Resource references, imports and file uploads

Annalist primarily deals with collections of data that are stored as JSON (or JSON-LD) text files, which can in turn reference other resources, including imges and other non-textual media, that are accessible on the Web.  But sometimes it is useful to import such resources so that they become part of a published Annalist collection, and to reference such resources.

Annalist deals with such circumstances by allowing arbitrary files and resources to be "attached" to an Annalist entity, via file upload and web resource import fields. These attachments are described and referenced within the JSON part of an entity, and stored alongside the JSON as files of the appropriate type.  This approach allows Annalist to preserve information about the attachments such as the content type and provenance information.  Further, Annalist fields in one entity can reference fields in another entity, and for fields using resource renderers such as `URIImage`, a reference to such a field is treated as a reference to the attached resource.

Web resources can be imported as attachements to an entity by creating a field with render type `URIImport`.  This is rendered for editing as a text input field for the resource URI with an "Import" button alongside, and for viewing as a hyperlink that links to the imported resource attached to the entity.

Files can be uploaded as attachements to an entity by creating a field with render type `FileUpload`.  This is rendered for editing as an HTML file browser input, and for viewing as a hyperlink that links to the imported file attached to the entity.

For referencing resources, there are several options, provided through renderers like `URILink` and `URIImage`:

1. Direct reference to a resource (usually an external resource)
2. Reference to an imported or uploaded attachment in a designated entity
3. Reference to an imported attachment in the current entity
4. Reference to an uploaded attachment in the current entity

These different cases are invoked as follows.

(@@TEST: do repeated import fields work OK?)

### Direct reference to a resource (usually an external resource)

Field "Field value type" (`Field_type`) describes the target value (e.g. `annal:Identifier` or `annal:Image`), and field "Enum type" (`Field_typeref`) is unspecified or blank.

In this case the field value is used directly as the resource URI, and for editing is presented as a text input box for the URI.

### Reference to an imported or uploaded attachment in a designated entity

The value of field "Enum type" (`Field_typeref`) is the target entity type, and field "Referenced field" (`Field_fieldref`) is target field property CURIE or URI for the attachment; this is the same as the "Property" (`Field_property`) value in the target field description.

The stored field value is an identifier for a selected target record, and is presented for editing as a drop-down list of entity identifiers.

### Reference to an imported attachment in the current entity

Field "Field value type" (`Field_type`) is `annal:Import`, and field "Enum type" (`Field_typeref`) is unspecified or blank.

In this case the field value describes an attachment to the current entity, and for editing is presented as render type `annal:URIImport`.

### Reference to an uploaded attachment in the current entity

(@@TODO: not yet implemented)

Field "Field value type" (`Field_type`) is `annal:Upload`, and field "Enum type" (`Field_typeref`) is unspecified or blank.

In this case the field value describes an attachment to the current entity, and for editing is presented as render type `annal:FileUpload`.


## Field render types

Annalist provides a number of built-in field rendering functions for dealing with different types and uses of field data.

Each renderer deals with two main functions:

1. conversion between stored data to a textual value that can be used as a input value in an HTML form, and
2. generation of HTML fragments for presentation in a web page.  Different forms of presentation are provided for viewing and editing.

Some of the values listed below were created to handle earlier stages of development, are now redundant, and in due course their use should be replaced by the more generic renderers indicated.

The definitive list of render types is in `annalist/sitedata/enums/Enum_render_type`.  Renderer selection is handled through module `annalist.views.fields.rener_utils`.

* `CheckBox` - presents Boolean value as a checkbox.
* `EntityId` - presents entity identitier as a simple input field for editing, or as a hyperlink for viewing.
* `EntityTypeId` - presents the entity type identifier a simple input field for editing, or as a hyperlink for viewing.
* `Enum` - presents a value of a designated type (see field `Field_typeref`) as a dropdown list for edting, or as a hyperlink for viewing.  Requires some existing value to be selected and picks an arbitrary value for a default.
* `Enum_choice` - presents a value of a designated type (see field `Field_typeref`) as a dropdown list for edting, or as a hyperlink for viewing.  Also provides a "+" button which can be used to create a new value of the designated type. The value may be left unselected, in which case the stored value is blank.
* `Enum_optional` - presents a value of a designated type (see field `Field_typeref`) as a dropdown list for edting, or as a hyperlink for viewing.  The value may be left unselected, in which case the stored value is blank.
* `Field` - identifies a field description; subsumed by `Enum_choice`.
* `FileUpload` - upload file as resource attached to entity.  Stored as a complex structure with filename, resource reference, content type, etc.;  presented for editing as an HTML file upload input element, and for viewing as a hyperlink.  See section "Resource references, imports and file uploads"
* `Identifier` - a [CURIE](http://www.w3.org/TR/curie/) or [URI](https://tools.ietf.org/html/rfc3986).  Preesented for editing as a text box, and for viewing as a simple text element.
* `List` - identifies a list description; subsumed by `Enum_choice`.
* `Markdown` - multiline rich text.  Stored and presented for editing as Markdown text, and for viewing as  text formatted according to Markdown conventions.
* `Placement` - a special-case field renderer used for presenting placement of a field on a form.
* `RepeatGroup` - special case renderers used for describing repeated fields in a view description.  The stored value is a list of JSON objects, each of which is rendered using the field group reference from the field description (see section "Repeated field groups" and field `Field_groupref`).  Fields within each group are flowed vertically down the view with labels to the left.
* `RepeatGroupRow` - same as `RepeatGroup`, except that field groups are rendered in tabular form with field labels for column headers, with each repeated group as a row of the table.
* `Slug` - simple text value used as an internal local identifier, or Slug, presented in the same was as the 'Text' renderer.  The text value is expected to consist of up to 32 letters, digits and/or underscore characters, (but this is not currently enforced @@).
* `Text` - a simple single-line text value, presented for editing as an HTML input field, and for viewing as a simple text element.
* `Textarea` - a multi-line text value, presented for editing as an HTML "textarea" field, and for viewing as a simple flowed text element.
* `TokenSet` - a list of simple text values, presented for editing as an HTML input field, and for viewing as a simple text element.  Presented values are space-separated.  Currently there is no mechanism to escape spaces within individual text values (@@).
* `Type` - identifies an entity type description; subsumed by `Enum_choice`.
* `URIImage` - A reference to an image value, presented for viewing as the referenced image.  See also section "Resource references, imports and file uploads".
* `URIImport` - Import a web resource as an attachment to an entity.  Stored as a complex structure with resource URI, local resource reference, content type, etc.;  presented for editing as a text input field and an "Import" button, and for viewing as a hyperlink.  See section "Resource references, imports and file uploads"
* `URILink` - A URI presented for viewing as a Hyperlink, used to create fields that reference externally stored resources.  See also section "Resource references, imports and file uploads".
* `View` - identifies a view description; subsumed by `Enum_choice`.


## Field value types

Field value types are identified by URIs or CURIEs that are used to identify some value type.

Built-in values include:

* `annal:Text` - single-line text
* `annal:LongText` - multi-line text
* `annal:Slug` - short text sring used as an internal identifier (consists of up to 32 letters, digits and/or underscore characters)
* `annal:Markdown` - multi-line rich text entered, edited and stoired using Markdown formatting conventions
* `annal:Identifier` - text value containing a [CURIE](http://www.w3.org/TR/curie/) or [URI](https://tools.ietf.org/html/rfc3986)
* `annal:URI` - text value containing a [URI](https://tools.ietf.org/html/rfc3986)
* `annal:Placement` - text value indicating the placement of a field in a display, and presented as a rough visial indication of the field placement (see module `annalist.views.fields.render_placement`)
* `annal:Field_group` - value of a field that is itself a reference to a field group (which is itself a list of fields); used for repeated-value fields.
* `annal:Type` - mainly internal use for reference to an Annalist entity type; the stored value is an `annal:Slug` text value, presented as a drop-down list or a hyperlink
* `annal:View` - mainly internal use for reference to an Annalist view description; the stored value is an `annal:Slug` text value, presented as a drop-down list or a hyperlink
* `annal:List` - mainly internal use for reference to an Annalist list description; the stored value is an `annal:Slug` text value, presented as a drop-down list or a hyperlink
* `annal:User` - reference to an Annalist user; the stored value is an `annal:Slug` text value
* `annal:List_type` - type of list display: "List" or "Grid"
* `annal:TokenSet` - list of string token values (e.g. used for user permissions list); stored as a JSON list, presented as a space-separated list of tokens
* `annal:Boolean` - stored as JSON `true` or `talse`, typically presented as a checkbox.
* `annal:Import` - (see section "Resource references, imports and file uploads")
* `annal:Upload` - (see section "Resource references, imports and file uploads")



# References

1. [Foundation responsive web framwork](http://foundation.zurb.com)

2. [Foundation grid](http://foundation.zurb.com/docs/components/grid.html)

3. [CURIE](http://www.w3.org/TR/curie/)

4. [URI](https://tools.ietf.org/html/rfc3986)


