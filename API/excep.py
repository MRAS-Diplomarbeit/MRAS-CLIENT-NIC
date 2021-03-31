class ElementNotFoundException(Exception):
    pass


class SinkNotLoadedException(Exception):
    pass


class NoSourcesFoundException(ElementNotFoundException):
    pass


class NoSinksFoundException(ElementNotFoundException):
    pass


class NoModulesFoundException(ElementNotFoundException):
    pass


class NoCardsFoundException(ElementNotFoundException):
    pass


class NoSinkInputsFoundException(ElementNotFoundException):
    pass