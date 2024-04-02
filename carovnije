data = 11111111
example_DIB = '09'
dib_sizes = {
            '00': 0, '01': 1, '02': 2, '03': 3, '04': 4, '05': 4, '06': 6, '07': 8,
            '08': 0, '09': 1, '0A': 2, '0B': 3, '0C': 4, '0D': 'n', '0E': 6, '0F': None
        }

def truncate_data_hexadecimal(self, data, dib):
    data_max = 2 ** (dib_sizes[dib] * 8) -1
    data = str(data)
    while int(data) > data_max:
        data = data[1:]
    return hex(int(data))[2:].upper()
    
    

print(truncate_data_hexadecimal(data, example_DIB)) # expected output: '6F'