import unittest
from DIB_VIB_generator import MessageGenerator

class TestVIBGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = MessageGenerator()

    def test_vib_generator(self):
        vib_values = self.generator.VIB_generator()
        for group in vib_values:
            for vib in group[1:]:
                print(vib)
                self.assertLess(int(vib, 16), 128)

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