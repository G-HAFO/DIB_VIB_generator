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



'''
    def generate_message(self, type=None, extension=False):
        """
        Generates a message by combining DIB and VIB values.

        Args:
            type (str): The type of value to generate. 'DIB' to generate DIB values and use a fixed VIB, 'VIB' to generate VIB values and use a fixed DIB.
            extension (str): The extension value to be used in case of 'VIB_single_extension' type.

        Returns:
            list: A list of combined DIB and VIB values.
        """
        messages = []
        dib_vib_pairs = []
        if type == 'DIB':
            for dib_group in self.DIB_generator():
                message_parts = []
                dib_vib_pair = []
                for i, dib in enumerate(dib_group[1:], 1):
                    transformed_data, truncated_data = self.transform_data(dib, self.data)
                    if transformed_data.strip() == '':
                        message_parts.append(f"{dib.strip()} {self.VIB.strip()}")
                    else:
                        message_parts.append(f"{dib.strip()} {self.VIB.strip()} {transformed_data.strip()}")
                    dib_vib_pair.append(f"DIB_{i} = {dib} VIB_{i} = {self.VIB} Data_{i} = {truncated_data}")
                dib_vib_pairs.append('\n'.join(dib_vib_pair))
                messages.append(f"{self.command.strip()} {' '.join(filter(None, message_parts))}")
                self.data += 1
        elif type == 'VIB_primary':
            for vib_group in self.VIB_generator():
                message_parts = []
                dib_vib_pair = []
                for i, vib in enumerate(vib_group[1:], 1):
                    message_parts.append(f"{self.DIB.strip()} {vib.strip()} {transformed_data.strip()}")
                    dib_vib_pair.append(f"DIB_{i} = {self.DIB} VIB_{i} = {vib} Data_{i} = {truncated_data}")
                dib_vib_pairs.append('\n'.join(dib_vib_pair))
                messages.append(f"{self.command.strip()} {' '.join(filter(None, message_parts))}")
                self.data += 1
        elif type == 'VIB_single_extension':
            if not extension:
                print('Please provide the extension value')
                return
            for vib_group in self.VIB_generator():
                message_parts = []
                dib_vib_pair = []
                for i, vib in enumerate(vib_group[1:], 1):
                    message_parts.append(f"{extension} {self.DIB.strip()} {vib.strip()} {transformed_data.strip()}")
                    dib_vib_pair.append(f"DIB_{i} = {self.DIB} VIB_{i} = {extension} {vib} Data_{i} = {truncated_data}")
                dib_vib_pairs.append('\n'.join(dib_vib_pair))
                messages.append(f"{self.command.strip()} {' '.join(filter(None, message_parts))}")
                self.data += 1
'''