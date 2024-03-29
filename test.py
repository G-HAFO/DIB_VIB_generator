import unittest
from DIB_VIB_generator import MessageGenerator

class TestMessageGenerator(unittest.TestCase):
    def setUp(self):
        self.dib_exclude_list = ['05','06','07','0F','0D']
        self.generator = MessageGenerator(data = 11111111, exclude_list_dib=self.dib_exclude_list)

    def test_transform_data(self):
        # Test with DIB '09'
        result = self.generator.transform_data(dib='09', data=123456)
        self.assertEqual(result, '56 34 12')

        # Test with DIB not in dib_sizes
        result = self.generator.transform_data(dib='ZZ', data=123456)
        self.assertEqual(result, '')

        # Test with size 0
        result = self.generator.transform_data(dib='05', data=123456)
        self.assertEqual(result, '')

    def test_generate_message(self):
        # Test with type 'DIB'
        messages, dib_vib_pairs = self.generator.generate_message(type='DIB')
        self.assertIsInstance(messages, list)
        self.assertIsInstance(dib_vib_pairs, list)

        # Test with invalid type
        with self.assertRaises(ValueError):
            self.generator.generate_message(type='INVALID')

if __name__ == '__main__':
    unittest.main()


    
def generate_message(self):
        """
        Generates a message by combining DIB and VIB values.

        Returns:
            list: A list of combined DIB and VIB values.
        """
        messages = []
        for vib_group in self.VIB_generator():
            message = ''
            for vib in vib_group[1:]:
                message += (self.DIB + ' ' + vib + ' ' + self.transform_data(self.DIB, self.data) + ' ')
            messages.append(self.command + ' ' + message.strip())
        return messages   