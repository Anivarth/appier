# Models

Model attributes can configured by adding keywords to their declaration:

```python
class Message(BaseModel):

    text = appier.field(
        type = unicode,
        index = True,
        immutable = True
    )
```

An attribute can be one of the following types:

* `str` - String (this is the default type);
* `unicode` - Unicode (eg: "Eyjafjallajökull");
* `int` - Integer (eg: 5);
* `bool` - Boolean (eg: True);
* `float` - Float (eg: 1.3);
* `list` - List of values (eg: ["a"]);
* `dict` - Key-value dictionary (eg: {"a": 1});
* `appier.File` - Type to be used for referencing file objects;
* `appier.Files` - Used for a set of file references;
* `appier.ImageFile` - Specialized type file for images (allows resizing, etc.);
* `appier.ImageFiles` - Sequence based data type for the image type;
* `appier.reference` - Non relational equivalent of the foreigh reference/key;
* `appier.references` - Multiple items (to many) version of the reference type;

The following keywords can be added to configure the attribute further:

* `index` - Boolean indicating if an index should be created for this attribute in 
the data source (faster searches);
* `increment` - Flag indicating if the value should be automatically generated on 
persistence by adding 1 to the previously generated value;
* `default` - Indicates that the attribute is the default representation for the model
(useful for search operations to be able to decide which attribute to search by default);
* `safe` - Safe attributes cannot be set automatically with the `apply` operation;
* `private` - Private attributes are not retrieved in `get` or `find` operations (useful
to keep passwords safe for example). This behaviour can be bypassed by passing 
`rules = False` to these methods;
* `immutable` - Immutable attributes cannot be modified, they can only be set at creation time.

### Filters

* `equals` -
* `not_equals` -
* `in` -
* `not_in` -
* `like` -
* `rlike` -
* `llike` -
* `greater` -
* `greater_equal` -
* `lesser` -
* `lesser_equal` -
* `is_null` -
* `is_not_null` -