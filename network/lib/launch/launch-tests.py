import unittest

from launch import Packet, Field, formats


class PacketSubclass(Packet):
    pass


class TestPacket(unittest.TestCase):

    def test_undefined_type(self):

        class NoType(Packet):
            pass
        p = NoType()

        with self.assertRaises(AttributeError) as cm:
            str(p)
        self.assertEqual(
            'NoType.type not defined',
            str(cm.exception)
        )

    def test_undefined_protocol(self):

        class NoProtocol(Packet):
            type = 1  # doesn't mean anything
        p = NoProtocol()

        with self.assertRaises(AttributeError) as cm:
            str(p)
        self.assertEqual(
            'NoProtocol.protocol not defined',
            str(cm.exception)
        )


class TestPacketField(unittest.TestCase):

    def test_undefined_format(self):

        class NoFieldFormat(Packet):
            random_prop = Field()

        with self.assertRaises(AttributeError) as cm:
            NoFieldFormat()
        self.assertEqual(
            'NoFieldFormat.random_prop has no format specified',
            str(cm.exception)
        )

    def test_invalid_format(self):

        class InvalidFieldFormat(Packet):
            random_prop = Field(format='z')

        with self.assertRaises(AttributeError) as cm:
            InvalidFieldFormat()
        self.assertEqual(
            "InvalidFieldFormat.random_prop has invalid format: 'z'",
            str(cm.exception)
        )
