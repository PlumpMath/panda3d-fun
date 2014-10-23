import struct


class formats(object):

    char = 'C'
    signed_char = 'b'
    unsigned_char = 'B'
    bool = '?'
    short = 'h'
    unsigned_short = 'H'
    int = 'i'
    unsigned_int = 'I'
    long = 'l'
    unsigned_long = 'L'
    long_long = 'q'
    unsigned_long_long = 'Q'
    float = 'f'
    double = 'd'


class Field(object):

    format = None

    def __init__(self, format=None):
        self.format = format


class Packet(object):

    #:
    protocol = None
    #:
    type = None
    #:
    length = None

    def __new__(cls, data=None):
        for attr_name, attr_value in cls.__dict__.items():
            if not isinstance(attr_value, Field):
                continue

            if getattr(attr_value, 'format', None) is None:
                raise AttributeError(
                    '{}.{} has no format specified'.format(cls.__name__, attr_name)
                )
            elif getattr(attr_value, 'format') not in formats.__dict__.values():
                raise AttributeError(
                    '{}.{} has invalid format: {!r}'.format(
                        cls.__name__, attr_name, getattr(attr_value, 'format')
                    )
                )

        return super(Packet, cls).__new__(cls)

    def __init__(self, data=None):
        pass

    def __str__(self):
        if self.type is None:
            raise AttributeError('{}.type not defined'.format(self.__class__.__name__))
        elif self.protocol is None:
            raise AttributeError('{}.protocol not defined'.format(self.__class__.__name__))

        raise NotImplementedError
