import unittest

from launch import Packet, Field, formats


class TestPacket(unittest.TestCase):

    def test_undefined_type(self):

        class NoType(Packet):
            pass
        p = NoType()

        with self.assertRaises(AttributeError) as cm:
            bytes(p)
        self.assertEqual(
            'NoType.type not defined',
            str(cm.exception)
        )

    def test_undefined_protocol(self):

        class NoProtocol(Packet):
            type = 1  # doesn't mean anything
        p = NoProtocol()

        with self.assertRaises(AttributeError) as cm:
            bytes(p)
        self.assertEqual(
            'NoProtocol.protocol not defined',
            str(cm.exception)
        )

    def test_header_packed(self):

        class PackHeader(Packet):
            protocol = 1000
            type = 2000

        p = PackHeader()
        actual = bytes(p)
        expected = b'\xe8\x03\x00\x00\xd0\x07\x00\x00\x00\x00\x00\x00'
        self.assertEqual(expected, actual)

    @unittest.skip('unfinished')
    def test_packing_no_strings(self):

        class PackNoStrings(Packet):

            field1 = Field(formats.char)
            field2 = Field(formats.signed_char)
            field3 = Field(formats.unsigned_char)
            field4 = Field(formats.bool)
            field5 = Field(formats.short)
            field6 = Field(formats.unsigned_short)
            field7 = Field(formats.int)
            field8 = Field(formats.unsigned_int)
            field9 = Field(formats.long)
            field10 = Field(formats.unsigned_long)
            field11 = Field(formats.long_long)
            field12 = Field(formats.unsigned_long_long)
            field13 = Field(formats.float)
            field14 = Field(formats.double)


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
