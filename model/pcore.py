
class PNamedElement:
    name = String


class PClassifier(PNamedElement):
    instance_class_name = Str

    instance_class = Callable(transient=True)

    default_value = Instance(HasTraits, transient=True)

    instance_type_name = Str

    p_package = Instance(PPackage, transient=True)

    p_type_parameters = List(Instance(PTypeParameter))

    def is_instance(self, klass):
        return isinstance(self, klass)

    def get_classifier_id(self):
        return id(self)


class PClass(PClassifier):
    abstract = Bool(False)

    interface = Bool(False)

    p_super_types = List(Instance(This))

    p_attributes = List(Instance(PAttribute))

    p_references = List(Instance(PReference))

    p_operations = List(Instance(POperation))

    p_structural_features = List(Instance(PStructuralFeature))

    p_generic_super_types = List(Instance(PGenericType))

    p_all_attributes = List(Instance(PAttribute))

    p_all_references = List(Instance(PReference))

    p_all_operations = List(Instance(POperation))

    p_all_containments = List(Instance(PReference))

    p_all_structural_features = List(Instance(PStructuralFeature))

    p_all_super_types = List(Instance(This))

    p_all_generatic_super_types = List(Instance(PGenericType))

    p_is_attribute = Instance(PAttribute)

    def is_super_type_of(self, obj):
        return obj in self.p_super_types

    def get_feature_count(self):
        return len(self.p_all_structural_features)

    def get_p_structural_feature(self, i):
        return self.p_all_structural_features[i]

    def get_feature_id(self, feature):
        return id(self.p_all_structural_features[feature])

    def get_p_structural_feature(self, name):
        for feature in self.p_all_structural_features:
            if feature.name == name:
                return feature
        else:
            return None


class PTypedElement(PNamedElement):
    ordered = Bool

    unique = Bool

    lower_bound = Int

    upeer_bound = Int

    many = Bool

    required = Bool

    p_type = Instance(PClassifier)

    p_generic_type = Instance(PGenericType)


class PStructuralFeature(PTypedElement):
    changeable = Bool

    volatile = Bool

    transient = Bool

    default_value_literal = Str

    default_value = Any

    unsettable = Bool

    derived = Bool

    p_containing_class = Instance(PClass)

    def get_feature_id(self):
        return id(self)

    def get_container_class(self):
        return self.p_containing_class


class PDataType(PClassifier):
    serializable = Bool


class PAttribute(PStructuralFeature):
    id = Bool

    p_attribute_type = Instance(PDataType, allow_none=False)


class PReference(PStructuralFeature):
    containment = Bool

    container = Bool

    resolve_proxies = Bool

    p_opposite = Instance(This)

    p_reference_type = Instance(PClass)

    p_keys = List(Instance(PAttribute))


class POperation(PTypedElement):
    p_containing_class = Instance(PClass)

    p_type_parameters = List(Instance(PTypeParameter))

    p_parameters = List(Instance(PParameter))

    p_exceptions = List(Instance(PClassifier))

    p_generic_exceptions = List(Instance(EGenericType))

# EOF -------------------------------------------------------------------------
