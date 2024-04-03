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
            row = []
            for j in range(i, i + self.group_size):
                if format(j, '02X') not in self.exclude_list_dib:
                    row.append(format(j, '02X'))
            if row:
                row.insert(0, len(row))
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
        for i in range(lower_limit, upper_limit + 1, self.group_size):
            row = []
            for j in range(i, i + self.group_size):
                if format(j, '02X') not in self.exclude_list_vib:
                    row.append(format(j, '02X'))
            if row:
                row.insert(0, len(row))
                DIB_VIB.append(row)
        return DIB_VIB

    def generate_message(self, type=None, extension=False):
        """
        Generates messages based on the provided type and extension.

        Args:
            type (str): The type of message to generate. Possible values are 'DIB', 'VIB_primary', and 'VIB_manual_extension'.
            extension (bool): Indicates whether an extension value should be provided for 'VIB_manual_extension' type.

        Returns:
            tuple: A tuple containing two lists. The first list contains the generated messages, and the second list contains the corresponding DIB-VIB data.

        Raises:
            None

        """
        messages = []
        dib_vib_data = []
        if type == 'DIB':
            for dib_group in self.DIB_generator():
                message_parts = []
                group_data = []
                for i, dib in enumerate(dib_group[1:], 1):
                    transformed_data, truncated_data = self.transform_data(dib, self.data)
                    message_parts.append(f"{dib.strip()} {self.VIB.strip()} {transformed_data.strip()}")
                    group_data.append({"DIB": dib, "VIB": self.VIB, "Data": truncated_data})
                dib_vib_data.append(group_data)
                messages.append(f"{self.command.strip()} {' '.join(filter(None, message_parts))}")
                self.data += 1
        elif type == 'VIB_primary':
            for vib_group in self.VIB_generator():
                message_parts = []
                group_data = []
                for i, vib in enumerate(vib_group[1:], 1):
                    transformed_data, truncated_data = self.transform_data(self.DIB, self.data)
                    message_parts.append(f"{self.DIB.strip()} {vib.strip()} {transformed_data.strip()}")
                    group_data.append({"DIB": self.DIB, "VIB": vib, "Data": truncated_data})
                dib_vib_data.append(group_data)
                messages.append(f"{self.command.strip()} {' '.join(filter(None, message_parts))}")
                self.data += 1
        elif type == 'VIB_manual_extension':
            if not extension:
                print('Please provide the extension value')
                return
            for vib_group in self.VIB_generator():
                message_parts = []
                group_data = []
                for i, vib in enumerate(vib_group[1:], 1):
                    transformed_data, truncated_data = self.transform_data(self.DIB, self.data)
                    message_parts.append(f"{extension} {self.DIB.strip()} {vib.strip()} {transformed_data.strip()}")
                    group_data.append({"DIB": self.DIB, "VIB": extension + " " + vib, "Data": truncated_data})
                dib_vib_data.append(group_data)
                messages.append(f"{self.command.strip()} {' '.join(filter(None, message_parts))}")
                self.data += 1
        else:
            print('Invalid type')
        return messages, dib_vib_data

    def transform_data(self, dib, data):
        """
        Transforms the data value into a string of bytes based on the DIB size.

        Args:
            dib (str): The DIB value.
            data (int): The data value.

        Returns:
            tuple: A tuple containing the transformed data value and the truncated data value.
            tuple: A tuple containing the transformed data value and the truncated data value.  
        """  
        dib = hex(int(dib, 16) & 0x0F)[2:].zfill(2).upper()
        if dib not in self.dib_sizes:  
            return '', 'Data not transformed, DIB not recognized'  
        if self.dib_sizes[dib] in ['n', None]:  
            return '', 'Data not transformed, invalid size'  
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
        dib = hex(int(dib, 16) & 0x0F)[2:].zfill(2).upper()  # Convert dib to string and pad with leading zero if necessary
        size = self.dib_sizes.get(dib, 0)  # Use 0 as default size if dib is not found
        data_max = 2 ** (size * 8) - 1
        data = str(data)
        while int(data) > data_max:
            data = data[1:]
        transformed_data = hex(int(data))[2:].upper().zfill(size * 2)
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
        dib=hex(int(dib, 16) & 0x0F)[2:].zfill(2).upper()
        size = self.dib_sizes.get(dib, 0)
        bcd_data = [format(int(digit), 'X') for digit in str(data)]
        bcd_data = ['0'] * (size * 2 - len(bcd_data)) + bcd_data[-size * 2:]
        bytes = [bcd_data[i] + bcd_data[i+1] for i in range(0, len(bcd_data), 2)]
        transformed_data = ' '.join(bytes[::-1]) + ' '
        truncated_data = str(int(''.join(bcd_data)))
        return transformed_data, truncated_data
    
    def input_data(self, command='20 7A 60 32 00 00'):
        """
        Collects DIB, VIB, and Data from user input and returns a list of messages and DIB/VIB data.

        Returns:
            tuple: A tuple containing two lists:
                - messages: A list of messages in the format "<command> <DIB> <VIB> <transformed_data>".
                - dib_vib_data: A list of dictionaries containing the DIB, VIB, and truncated Data.
        """
        dib_vib_data = []
        messages = []
        while True:
            dib = input("Enter DIB: ")
            vib = input("Enter VIB: ")
            try:
                dib = format(int(dib, 16) & 0x0F, '02X')
            except ValueError:
                print("\nInvalid DIB format. Please enter a hexadecimal value.")
                continue
            size = self.dib_sizes.get(dib, 0) * 8 
            print(f"\nSize in bytes based on DIB: {size}")
            data = input("Enter Data: ")
            try:
                int(data)
            except ValueError:
                print("Invalid Data format. Please enter a numeric value.")
                continue

            transformed_data, truncated_data = self.transform_data(dib, int(data))

            message = command + " " + dib + " " + vib + " " + transformed_data
            messages.append(message)
            dib_vib_data.append({"DIB": dib, "VIB": vib, "Data": truncated_data})

            another = input("Do you want to enter another? (yes/no): ")
            if another.lower() != "yes":
                break

        return messages, dib_vib_data
        
        

dib_exclude_list = ['00','05','06','07','0F','0D']

def main():
    generator = MessageGenerator(data = 11111111, exclude_list_dib=dib_exclude_list,command='[01]B>20 7A 60 32 00 00',group_size=8)
    ##messages,dib_vib_pairs = generator.generate_message(type= 'DIB', extension='FD')
    """for msg, pair_group in zip(messages, dib_vib_pairs):
        print(msg)
        for pair in pair_group:
            print( pair['DIB'], pair['VIB'], pair['Data'])"""
    with open('data.txt', 'w') as f:
        generator = MessageGenerator(command='20 7A 60 32 00 00',group_size=1)
        generator_dibs = generator.DIB_generator()
        for group in generator_dibs:
            generator.DIB = group[1]
            messages, dib_vib_pairs = generator.generate_message(type='VIB_primary')
            for msg, pair_group in zip(messages, dib_vib_pairs):
                f.write(f'{msg}\n')
                for pair in pair_group:
                    f.write(f"DIB={pair['DIB']} VIB={pair['VIB']} Data={pair['Data']}\n")
    


if __name__ == "__main__":
    main()
    