class MessageGenerator:
    """
    A class for generating messages with DIB (Data Information Block) and VIB (Value Information Block) values.

    Attributes:
        DIB (str): The default DIB value.
        VIB (str): The default VIB value.
        data (int): The default data value.
        exclude_list_dib (list): A list of DIB values to exclude.
        exclude_list_vib (list): A list of VIB values to exclude.
        command (str): The default command value.
        dib_sizes (dict): A dictionary mapping DIB values to their corresponding sizes.
        group_size (int): The size of each DIB_VIB group.

    Methods:
        DIB_generator(lower_limit=0, upper_limit=15): Generates a list of DIB values within the specified range.
        VIB_generator(lower_limit=0, upper_limit=127): Generates a list of VIB values within the specified range.
        generate_message_parts(group, type, extension=None): Generates message parts based on the given group and type.
        generate_message(type=None, extension=False): Generates messages based on the given type.
        transform_data(dib, data): Transforms the data value into a string of bytes based on the DIB size.
        transform_and_truncate_data_hex_dec(data, dib): Transforms the given data into hexadecimal format.
        transform_and_truncate_data_BCD(data, dib): Transforms and truncates the given data into BCD format.
    """

    def __init__(self, DIB="0C", VIB='13', data=11111111, exclude_list_dib=None, exclude_list_vib=None, command='20 7A 60 32 00 00', group_size=8):
        """
        Initializes the MessageGenerator class.

        Args:
            DIB (str): The default DIB value.
            VIB (str): The default VIB value.
            data (int): The default data value.
            exclude_list_dib (list): A list of DIB values to exclude.
            exclude_list_vib (list): A list of VIB values to exclude.
            command (str): The default command value.
            group_size (int): The size of each DIB group.
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
        self.group_size = group_size

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
        for i in range(lower_limit, upper_limit + 1, self.group_size):
            row = [0]
            for j in range(i, i + self.group_size):
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

    def generate_message_parts(self, group, type, extension=None):
        """
        Generates message parts based on the given group and type.

        Args:
            group (list): The group of DIB or VIB values.
            type (str): The type of message parts to generate.
            extension (str, optional): The extension value for VIB_single_extension type.

        Returns:
            tuple: A tuple containing the generated message parts and the corresponding DIB-VIB pairs.
        """
        message_parts = []
        dib_vib_pair = []
        for i, item in enumerate(group[1:], 1):
            transformed_data, truncated_data = self.transform_data(item, self.data)
            if type == 'DIB':
                message_parts.append(f"{item.strip()} {self.VIB.strip()} {transformed_data.strip()}")
                dib_vib_pair.append(f"DIB_{i} = {item} VIB_{i} = {self.VIB} Data_{i} = {truncated_data}")
            else:
                message_parts.append(f"{self.DIB.strip()} {item.strip()} {transformed_data.strip()}")
                dib_vib_pair.append(f"DIB_{i} = {self.DIB} VIB_{i} = {item} Data_{i} = {truncated_data}")
        return message_parts, dib_vib_pair

    def generate_message(self, type=None, extension=False):
        """
        Generates messages based on the given type.

        Args:
            type (str, optional): The type of messages to generate.
            extension (bool, optional): Whether to include extension value for VIB_single_extension type.

        Returns:
            tuple: A tuple containing the generated messages and the corresponding DIB-VIB pairs.
        """
        messages = []
        dib_vib_pairs = []
        if type == 'DIB':
            for dib_group in self.DIB_generator():
                message_parts, dib_vib_pair = self.generate_message_parts(dib_group, type)
                dib_vib_pairs.append('\n'.join(dib_vib_pair))
                messages.append(f"{self.command.strip()} {' '.join(filter(None, message_parts))}")
                self.data += 1
        elif type in ['VIB_primary', 'VIB_single_extension']:
            if type == 'VIB_single_extension' and not extension:
                print('Please provide the extension value')
                return
            for vib_group in self.VIB_generator():
                message_parts, dib_vib_pair = self.generate_message_parts(vib_group, type)
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
            tuple: A tuple containing the transformed data value and the truncated data value.
        """
        if dib not in self.dib_sizes:
            return '', 'Data not transformed, DIB not recognized'
        size = self.dib_sizes[dib]
        if size == 0:
            return '', 'Data not transformed, size is 0'
        if dib in ['09', '0A', '0B', '0C', '0E']:
            return self.transform_and_truncate_data_BCD(data, dib)
        else:
            return self.transform_and_truncate_data_hex_dec(data, dib)

    def transform_and_truncate_data_hex_dec(self, data, dib):
        """
        Transforms the given data into hexadecimal format.

        Args:
            data (int): The data to be transformed.
            dib (str): The DIB (Data Information Block) value.

        Returns:
            tuple: A tuple containing the transformed data in hexadecimal format and the truncated data.
        """
        dib = int(dib, 16)
        dib = dib & 0x0F
        dib = format(dib, '02X')
        data_max = 2 ** (self.dib_sizes[dib] * 8) - 1
        data = str(data)
        while int(data) > data_max:
            data = data[1:]
        transformed_data = hex(int(data))[2:].upper()
        while len(transformed_data) < self.dib_sizes[dib] * 2:
            transformed_data = '0' + transformed_data
        bytes = [transformed_data[i:i+2] for i in range(0, len(transformed_data), 2)]
        transformed_data = ' '.join(bytes[::-1]) + ' '
        truncated_data = data
        return transformed_data, truncated_data

    def transform_and_truncate_data_BCD(self, data, dib):
        """
        Transforms and truncates the given data into BCD format.

        Args:
            data (int): The data to be transformed and truncated.
            dib (str): The DIB (Data Information Block) value.

        Returns:
            tuple: A tuple containing the transformed data and the truncated data.
                The transformed data is a string with bytes separated by spaces,
                and the truncated data is a string without leading zeros.
        """
        dib = int(dib, 16)
        dib = dib & 0x0F
        dib = format(dib, '02X')
        size = self.dib_sizes.get(dib, 0)
        bcd_data = [format(int(digit), 'X') for digit in str(data)]
        while len(bcd_data) < size * 2:
            bcd_data.insert(0, '0')
        if len(bcd_data) > size * 2:
            bcd_data = bcd_data[-size * 2:]
        bytes = [bcd_data[i] + bcd_data[i+1] for i in range(0, len(bcd_data), 2)]
        transformed_data = ' '.join(bytes) + ' '
        truncated_data = str(int(''.join(bcd_data)))
        return transformed_data, truncated_data
        transformed_data = ' '.join(bytes[::-1])
        return transformed_data, ''.join(bcd_data).lstrip('0')
        truncated_data = ''.join(bytes[::]).lstrip('0')
        return transformed_data, truncated_data

        
        

dib_exclude_list = ['05','06','07','0F','0D']

def main():
    generator = MessageGenerator(data = 11111111, exclude_list_dib=dib_exclude_list,command='')
    messages,dib_vib_pairs = generator.generate_message(type= 'DIB')
    for msg, pair in zip(messages, dib_vib_pairs):
        print(msg)
        print(pair)
    


if __name__ == "__main__":
    main()
    