import json

class MessageGenerator:
    """
    A class for generating messages with DIB (Data Information Block) and VIB (Value Information Block) values.

    Attributes:
        DIB (str): The default DIB value.
        VIB (str): The default VIB value.
        data (int): The default data value.
        exclude_list_dib (list): A list of DIB values to exclude.
        exclude_list_vib (list): A list of VIB values to exclude.
        command_start (str): The default command_start value.
        command_end (str): The default command_end value.
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

    def __init__(self, DIB="0C", VIB='13', data=11111111, exclude_list_dib=None, exclude_list_vib=None, command_start='', command_end='', group_size=8):
        """
        Initializes the MessageGenerator class.

        Args:
            DIB (str): The default DIB value.
            VIB (str): The default VIB value.
            data (int): The default data value.
            exclude_list_dib (list): A list of DIB values to exclude.
            exclude_list_vib (list): A list of VIB values to exclude.
            command_start (str): The default command_start value.
            command_end (str): The default command_end value.
            group_size (int): The size of each DIB group.
        """
        self.DIB = DIB
        self.VIB = VIB
        self.data = data
        self.exclude_list_dib = exclude_list_dib if exclude_list_dib else []
        self.exclude_list_vib = exclude_list_vib if exclude_list_vib else []
        self.command_start = command_start
        self.command_end = command_end
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
                    transformed_data, truncated_data, size = self.transform_data(dib, self.data)
                    self.command_start = self.correct_msg_length(self.command_start, dib, self.VIB, size)
                    message_parts.append(f"{dib.strip()} {self.VIB.strip()} {transformed_data.strip()}")
                    group_data.append({"DIB": dib, "VIB": self.VIB, "Data": truncated_data})
                dib_vib_data.append(group_data)
                messages.append(f"{self.command_start.strip()} {' '.join(filter(None, message_parts)).strip() } {self.command_end.strip()}")
                self.data += 1
        elif type == 'VIB_primary':
            for vib_group in self.VIB_generator():
                message_parts = []
                group_data = []
                for i, vib in enumerate(vib_group[1:], 1):
                    transformed_data, truncated_data, size = self.transform_data(self.DIB, self.data)
                    self.command_start = self.correct_msg_length(self.command_start, self.DIB, vib, size)
                    message_parts.append(f"{self.DIB.strip()} {vib.strip()} {transformed_data.strip()}")
                    group_data.append({"DIB": self.DIB, "VIB": vib, "Data": truncated_data})
                dib_vib_data.append(group_data)
                messages.append(f"{self.command_start.strip()} {' '.join(filter(None, message_parts)).strip()} {self.command_end.strip()}")
                self.data += 1
        elif type == 'VIB_manual_extension':
            if not extension:
                print('Please provide the extension value')
                return
            for vib_group in self.VIB_generator():
                message_parts = []
                group_data = []
                for i, vib in enumerate(vib_group[1:], 1):
                    transformed_data, truncated_data, size = self.transform_data(self.DIB, self.data)
                    self.command_start = self.correct_msg_length(self.command_start, self.DIB, vib + ' ' + extension, size)
                    message_parts.append(f"{self.DIB.strip()} {extension} {vib.strip()} {transformed_data.strip()}")
                    group_data.append({"DIB": self.DIB, "VIB": extension + " " + vib, "Data": truncated_data})
                dib_vib_data.append(group_data)
                messages.append(f"{self.command_start.strip()} {' '.join(filter(None, message_parts)).strip()} {self.command_end.strip()}")
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
        """
        dib = hex(int(dib[0:2], 16) & 0x0F)[2:].zfill(2).upper()
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
        return data, data[:size * 2]

    def transform_and_truncate_data_BCD(self, data, dib):
        """
        Transforms and truncates the given data into BCD format.

        Args:
            data (int): The data to be transformed.
            dib (str): The DIB (Data Information Block) value.

        Returns:
            tuple: A tuple containing the transformed data in BCD format and the truncated data.
        """
        dib = hex(int(dib, 16) & 0x0F)[2:].zfill(2).upper()  # Convert dib to string and pad with leading zero if necessary
        size = self.dib_sizes.get(dib, 0)  # Use 0 as default size if dib is not found
        data_max = 10 ** size - 1
        data = str(data)
        return data, data[:size]

    def correct_msg_length(self, command_start, dib, vib, size):
        """
        Corrects the message length by adding or removing spaces.

        Args:
            command_start (str): The command start string.
            dib (str): The DIB value.
            vib (str): The VIB value.
            size (int): The size of the data.

        Returns:
            str: The corrected command start string.
        """
        dib = hex(int(dib, 16) & 0x0F)[2:].zfill(2).upper()  # Convert dib to string and pad with leading zero if necessary
        vib = hex(int(vib, 16) & 0x0F)[2:].zfill(2).upper()  # Convert vib to string and pad with leading zero if necessary
        if size == 0:
            return command_start.strip()
        elif size == 1:
            return command_start.strip() + ' '
        elif size == 2:
            return command_start.strip() + '  '
        elif size == 3:
            return command_start.strip() + '   '
        elif size == 4:
            return command_start.strip() + '    '
        elif size == 6:
            return command_start.strip() + '      '
        elif size == 8:
            return command_start.strip() + '        '
        else:
            return command_start.strip()
        while int(data) > data_max:
            data = data[1:]
        transformed_data = hex(int(data))[2:].upper().zfill(size * 2)
        bytes = [transformed_data[i:i+2] for i in range(0, len(transformed_data), 2)]
        transformed_data = ' '.join(bytes[::-1]) + ' '
        truncated_data = data
        return transformed_data, truncated_data,size
    
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
        dib=hex(int(dib, 16) & 0x0F)[2:].zfill(2).upper()
        size = self.dib_sizes.get(dib, 0)
        bcd_data = [format(int(digit), 'X') for digit in str(data)]
        bcd_data = ['0'] * (size * 2 - len(bcd_data)) + bcd_data[-size * 2:]
        bytes = [bcd_data[i] + bcd_data[i+1] for i in range(0, len(bcd_data), 2)]
        transformed_data = ' '.join(bytes[::-1]) + ' '
        truncated_data = str(int(''.join(bcd_data)))
        return transformed_data, truncated_data,size
    
    def input_data(self, command_start='20 7A 60 32 00 00',command_end =''):
        """
        Collects DIB, VIB, and Data from user input and returns a list of messages and DIB/VIB data.

        Returns:
            tuple: A tuple containing two lists:
                - messages: A list of messages in the format "<command_start> <DIB> <VIB> <transformed_data>".
                - dib_vib_data: A list of dictionaries containing the DIB, VIB, and truncated Data.
        """
        dib_vib_data = []
        messages = []
        info_data = []
        from typing import Tuple  # Add missing import statement

        while True:
            dib = input("Enter DIB: ")
            vib = input("Enter VIB: ")
            dib_values = dib.split()
            vib_values = vib.split()
            total_size = 0
            try:
                dib_value = format(int(dib[0:2], 16) & 0x0F, '02X')
                size = self.dib_sizes.get(dib_value, 0) * 8 
                print(f"\nTotal size in bytes based on DIB: {size}")
            except ValueError:
                print("\nInvalid DIB format. Please enter hexadecimal values separated by space.")
                continue

            data = input("Enter Data: ")
            try:
                int(data)
            except ValueError:
                print("Invalid Data format. Please enter a numeric value.")
                continue

            transformed_data, truncated_data = self.transform_data(dib, int(data))

            message = dib + " " + vib + " " + transformed_data
            messages.append(message.strip())
            dib_vib_data.append({"DIB": dib, "VIB": vib, "Data": truncated_data})
            info_data.append(dib_vib_data)

            another = input("\nDo you want to enter another? (yes/no): ")
            if another.lower() != "yes":
                break

        # After the loop, join the messages and append command_start and command_end
        final_message = command_start + " " + ' '.join(messages) + ' ' + command_end
        print(final_message)

        return final_message, dib_vib_data
    
    def correct_msg_length(self, command_start,dib,vib,data_size):
        """
        Corrects the length of the message based on the size of DIB and VIB.

        Args:               
            command_start (str): The command_start value.

        Returns:    
            str: The corrected command_start value.
        """
        dib_size = len(dib.split())  # Calculate the size of DIB in bytes
        vib_size = len(vib.split())  # Calculate the size of VIB in bytes
        total_size = dib_size + vib_size + data_size + 14  # Calculate the total size in bytes

        command_start_list = command_start.split()  # Split the command_start into a list
        command_start_list[6] = f'{total_size:02X}'  # Replace the 7th element with the hex of total_size
        return ' '.join(command_start_list) 
        

dib_exclude_list = ['00','05','06','07','0F','0D']
dib_exclude_list = ['00','05','06','07','0F','0D']

def main():
    generator = MessageGenerator(data = 11111111, exclude_list_dib=dib_exclude_list,command_start='1B 2A 01 2A 00 00 12 44 8F 19 55 55 55 55 50 03 7A 60 32 00 00',group_size=1,command_end='1B 42')
    messages,dib_vib_pairs = generator.generate_message(type= 'VIB_manual_extension', extension='FD')
    """for msg, pair_group in zip(messages, dib_vib_pairs):
        print(msg)
        for pair in pair_group:
            print( pair['DIB'], pair['VIB'], pair['Data'])"""
    """with open('data.txt', 'w') as f:
        generator = MessageGenerator(command='20 7A 60 32 00 00',group_size=1)
        generator_dibs = generator.DIB_generator()
        for group in generator_dibs:
            generator.DIB = group[1]
            messages, dib_vib_pairs = generator.generate_message(type='VIB_primary')
            for msg, pair_group in zip(messages, dib_vib_pairs):
                f.write(f'{msg}\n')
                for pair in pair_group:
                    f.write(f"DIB={pair['DIB']} VIB={pair['VIB']} Data={pair['Data']}\n")"""
    for msg, pair_group in zip(messages, dib_vib_pairs):
        print(msg)
        for pair in pair_group:
            print( pair['DIB'], pair['VIB'], pair['Data'])
    


if __name__ == "__main__":
    main()
    