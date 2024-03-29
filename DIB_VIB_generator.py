class MessageGenerator:
    def __init__(self, DIB="0C", VIB='13', data=int(12), exclude_list_dib=None, exclude_list_vib=None, command='20 7A 60 32 00 00'):
        """
        Initializes the MessageGenerator class.

        Args:
            DIB (str): The default DIB value.
            VIB (str): The default VIB value.
            data (int): The default data value.
            exclude_list_dib (list): A list of DIB values to exclude.
            exclude_list_vib (list): A list of VIB values to exclude.
            command (str): The default command value.
        """
        self.DIB = DIB
        self.VIB = VIB
        self.data = data
        self.exclude_list_dib = exclude_list_dib if exclude_list_dib else []
        self.exclude_list_vib = exclude_list_vib if exclude_list_vib else []
        self.command = command
        self.dib_sizes = {
            '00': 0, '01': 1, '02': 2, '03': 3, '04': 4, '05': 4, '06': 6, '07': 8,
            '08': 0, '09': 1, '0A': 2, '0B': 3, '0C': 4, '0D': 'n', '0E': 6, '0F': None
        }

    def DIB_generator(self, lower_limit=0, upper_limit=15):
        """
        Generates a list of DIB values within the specified range, excluding values in the exclude_list.

        Args:
            lower_limit (int): The lower limit of the range (inclusive).
            upper_limit (int): The upper limit of the range (inclusive).

        Returns:
            list: A list of DIB values.
        """
        DIB_VIB = []
        for i in range(lower_limit, upper_limit + 1, 8):
            row = [0]
            for j in range(i, i + 8):
                if format(j, '02X') not in self.exclude_list_dib:
                    row.append(format(j, '02X'))
            if row:
                row[0] = len(row) - 1
                DIB_VIB.append(row)
        return DIB_VIB

    def VIB_generator(self, lower_limit=0, upper_limit=127):
        """
        Generates a list of VIB values within the specified range, excluding values in the exclude_list.

        Args:
            lower_limit (int): The lower limit of the range (inclusive).
            upper_limit (int): The upper limit of the range (inclusive).

        Returns:
            list: A list of VIB values.
        """
        DIB_VIB = []
        for i in range(lower_limit, upper_limit + 1, 8):
            row = [0]
            for j in range(i, i + 8):
                if format(j, '02X') not in self.exclude_list_vib:
                        row.append(format(j, '02X'))
            if row:
                row[0] = len(row) - 1
                DIB_VIB.append(row)
        return DIB_VIB

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
                    message_parts.append(f"{dib.strip()} {self.VIB.strip()} {self.transform_data(dib, self.data).strip()}")
                    dib_vib_pair.append(f"DIB_{i} = {dib} VIB_{i} = {self.VIB} Data_{i} = {self.data}")
                dib_vib_pairs.append('\n'.join(dib_vib_pair))
                messages.append(f"{self.command.strip()} {' '.join(filter(None, message_parts))}")
                self.data += 1
        elif type == 'VIB_primary':
            for vib_group in self.VIB_generator():
                message_parts = []
                dib_vib_pair = []
                for i, vib in enumerate(vib_group[1:], 1):
                    message_parts.append(f"{self.DIB.strip()} {vib.strip()} {self.transform_data(self.DIB, self.data).strip()}")
                    dib_vib_pair.append(f"DIB_{i} = {self.DIB} VIB_{i} = {vib} Data_{i} = {self.data}")
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
                    message_parts.append(f"{extension} {self.DIB.strip()} {vib.strip()} {self.transform_data(self.DIB, self.data).strip()}")
                    dib_vib_pair.append(f"DIB_{i} = {self.DIB} VIB_{i} = {extension} {vib} Data_{i} = {self.data}")
                dib_vib_pairs.append('\n'.join(dib_vib_pair))
                messages.append(f"{self.command.strip()} {' '.join(filter(None, message_parts))}")
                self.data += 1
        else:
            print('Invalid type')
        return messages, dib_vib_pairs
            

    def transform_data(self, dib, data):
        """
        Transforms the data value into a string of bytes based on the DIB size.

        Args:
            dib (str): The DIB value.
            data (int): The data value.

        Returns:
            str: The transformed data value.
        """
        if dib not in self.dib_sizes:
            return ''
        size = self.dib_sizes[dib]
        if size == 0:
            return ''
        if dib in ['09', '0A', '0B', '0C', '0E']:
            # Convert data to BCD
            bcd_data = [format(int(digit), 'X') for digit in str(data)]
            while len(bcd_data) < size * 2:
                bcd_data.insert(0, '0')  
            bytes = [bcd_data[i] + bcd_data[i+1] for i in range(0, len(bcd_data), 2)]
        else:
            hex_data = format(data, '0' + str(size * 2) + 'X')
            bytes = [hex_data[i:i+2] for i in range(0, len(hex_data), 2)]
        bytes.reverse()
        return ' '.join(bytes)

dib_exclude_list = ['05','06','07','0F','0D']

def main():
    generator = MessageGenerator(data = 11111111, exclude_list_dib=dib_exclude_list)
    messages,dib_vib_pairs = generator.generate_message(type= 'DIB')
    for msg, pair in zip(messages, dib_vib_pairs):
        print(msg)
        print(pair)
    


if __name__ == "__main__":
    main()
