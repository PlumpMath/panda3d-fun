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

    def __init__(self, format=None):
        self.format = format

    def __get__(self, obj, type):
        raise NotImplementedError

    def __set__(self, obj, value):
        raise NotImplementedError


class Packet(object):
    """
    :attr:`protocol`, :attr:`type`, and :attr:`length` are all part of the header
    data. They are packed in the order just listed. Immediately following them
    is the payload, if any.
    """
    #: The :attr:`protocol` needs to be set by the user. All packets need to
    #: share the same protocol version. The :attr:`protocol` is assumed to be
    #: an :class:`int`.
    protocol = None
    #: The :attr:`type` needs to be set by the user. This identifies what type
    #: of packet the data belongs to. The :attr:`type` is assumed to be an
    #: :class:`int`.
    type = None

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

        inst = super(Packet, cls).__new__(cls)
        inst._length = None
        inst._format = ''
        return inst

    def __init__(self, data=None):
        pass

    @property
    def length(self):
        """
        The :attr:`length` will be set automatically and simply identifies how large
        the payload is.
        """
        return self._length

    def __str__(self):
        return str(self.__bytes__())

    def __bytes__(self):
        if self.type is None:
            raise AttributeError('{}.type not defined'.format(self.__class__.__name__))
        elif self.protocol is None:
            raise AttributeError('{}.protocol not defined'.format(self.__class__.__name__))

        self._length = struct.calcsize(self._format)
        header = struct.pack('iii', self.protocol, self.type, self.length)
        return header
