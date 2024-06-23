import struct
import os
import argparse
import csv

def unpack_binary_with_text(binary_filename, text_filename):
    """
    This function takes a binary file and a text file,
    reads the binary file, extracts the font data,
    and writes it to the text file.
    """
    with open(binary_filename, "rb") as f:
        # Seek to the offset, which is stored at 0x2C
        f.seek(0x08)

        # Read the offset, which is a 32-bit unsigned integer
        offset = struct.unpack("<I", f.read(4))[0]
        print(f"offset: {offset}")

        #f.seek(0x38)
        #amount = struct.unpack("<H", f.read(2))[0]
        #print(f"amount: {amount}")
                
        # Seek to the offset, which is where the font data starts
        #f.seek(offset+68)
        f.seek(offset)

        amount = struct.unpack("<I", f.read(4))[0]
        print(f"amount: {amount}")
        
        texts = []
        with open(text_filename, "w", encoding="utf-8", newline='') as out:
            for i in range(amount):
                #f.seek(2, 1)
                Data = struct.unpack("<H", f.read(2))[0]
                sizeData = struct.unpack("<H", f.read(2))[0]
                #print(f"Data: {Data}")
                #print(f"sizeData: {sizeData}")
                if Data == 9:
                    f.seek(74, 1)
                    sizeTextData = struct.unpack("<H", f.read(2))[0]
                    sizeText = struct.unpack("<I", f.read(4))[0]
                    #print(f"sizeText: {sizeText}")
                    text_bytes=f.read(sizeText)
                    Text = text_bytes.decode('utf-8').replace('\n', '\\n')
                    print(f"Text: {Text}")
                    texts.append((i, Text))
                    #out.write(f"{Text}\n")
                    f.seek(sizeTextData-4-sizeText, 1)
                else:
                    f.seek(sizeData-4, 1)
            #print(f"texts: {texts}")
            csv_writer = csv.writer(out)
            for offset, text in texts:
                csv_writer.writerow([offset, text, text])

def read_csv_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        return [(row[0], row[1], row[2]) for row in reader]
    
def modify_binary_with_text(binary_filename, text_filename):
    csv_data = read_csv_file(text_filename)

    with open(binary_filename, "r+b") as f, open(binary_filename+"_new", "wb") as w:
        f.seek(0, 2)
        len_bin_file = f.tell()
        print(f"len_bin_file: {len_bin_file}")

        f.seek(0)

        bytes=f.read(0x08)
        w.write(bytes)
        
        offset = struct.unpack("<I", f.read(4))[0]
        print(f"offset: {offset}")
        w.write(struct.pack("<I", int(len_bin_file)))

        offset_end = struct.unpack("<I", f.read(4))[0]
        print(f"offset_end: {offset_end}")
        w.write(struct.pack("<I", int(offset_end)))
        
        bytes=f.read(0x28)
        w.write(bytes)

        amount = struct.unpack("<H", f.read(2))[0]
        print(f"amount: {amount}")
        w.write(struct.pack("<H", int(amount)))

        bytes=f.read(0x2A)
        w.write(bytes)

        #id = "%04x" % struct.unpack("<I", f.read(4))[0]
        #print(id)
        line = 0
        id_new = int(1118481)
        for i in range(amount):
            #print(i)
            id = struct.unpack("<I", f.read(4))[0]
            #print(line)
            if line < len(csv_data) and i == int(csv_data[line][0]):
                #print(int(csv_data[line][0]))
                w.write(struct.pack("<I", id_new))
                bytes=f.read(0x10)
                w.write(bytes)
                line += 1
                #print(f"id: {id}")
            else:
                if line < len(csv_data) and int(csv_data[line][0]) == 99999:
                    #print(f"test_1: {int(csv_data[line][0])}")
                    w.write(struct.pack("<I", id))
                    bytes=f.read(0x10)
                    w.write(bytes)
                    line += 1
                else:
                    w.write(struct.pack("<I", id))
                    bytes=f.read(0x10)
                    w.write(bytes)
            id_new += 1
        #exit()

        #bytes=f.read(offset-58)
        #w.write(bytes)

        #read and write for end file
        w.write(f.read())

        f.seek(offset)

        amount_2 = struct.unpack("<I", f.read(4))[0]
        print(f"amount_2: {amount_2}")
        w.write(struct.pack("<I", int(amount_2)))
        
        #bytes=f.read(0x44)
        #w.write(bytes)
        line = 0
        for i in range(amount_2):
            #print(f"i: {i}")
            Data = struct.unpack("<H", f.read(2))[0]
            sizeData = struct.unpack("<H", f.read(2))[0]
            #print(f"Data: {Data}")
            #print(f"sizeData: {sizeData}")
            if Data == 9:
                bytes_skip=f.read(0x4A)
                
                sizeTextData = struct.unpack("<H", f.read(2))[0]
                sizeText = struct.unpack("<I", f.read(4))[0]

                size=sizeText%4
                #print(f"size: {size}")
                if size != 0:
                    padding = 4 - size
                else:
                    padding = 4
                    #text_bytes += b'\x00' * padding
                #print(f"sizeText: {sizeText}")
                #print(f"padding: {padding}")
                #print(f"padding_sum: {sizeText+padding}")

                #print(f"sizeText: {sizeText}")
                text_bytes=f.read(sizeText+padding)
                Text = text_bytes.decode('utf-8').replace('\n', '\\n')
                print(f"Text: {Text}")
                end_data=f.read(0x04)
                
                #text_data = text_file.readline().strip().replace('\\n', '\n')
                #print(f"i: {i}")
                
                if int(csv_data[line][0]) == 99999:
                    text_data = csv_data[line][1].replace('\\n', '\n')
                else:
                    text_data = csv_data[line][2].replace('\\n', '\n')
                print(f"text_data: {text_data}")
                #print(f"text_len: {len(text_data)}")
                text_bytes = text_data.encode('utf-8')
                text_bytes_singl = len(text_bytes)
                #w.write(struct.pack("<I", len(text_bytes)))
                size=len(text_bytes)%4
                #print(f"size_new_text: {size}")
                if size != 0:
                    padding = 4 - size
                    text_bytes += b'\x00' * padding
                else:
                    padding = 4
                    text_bytes += b'\x00' * padding

                #print(f"text_bytes_new: {text_bytes}")
                
                bytes_all=len(bytes_skip)+4+6+4+len(text_bytes)
                #print(f"bytes_all: {bytes_all}")

                w.write(struct.pack("<H", int(Data)))
                w.write(struct.pack("<H", int(bytes_all)))
                w.write(bytes_skip)
                #print(f"bytes_skip: {len(bytes_skip)}")
                sizeTextData_new=len(text_bytes)+4+4
                #print(f"sizeTextData_new: {sizeTextData_new}")
                w.write(struct.pack("<H", int(sizeTextData_new)))

                w.write(struct.pack("<I", text_bytes_singl))
                w.write(text_bytes)
                w.write(end_data)

                line += 1

                #exit()
            else:
                w.write(struct.pack("<H", int(Data)))
                w.write(struct.pack("<H", int(sizeData)))
                bytes_skip=f.read(sizeData-4)
                w.write(bytes_skip)

            

        

def main():
    print("MGS 3 Export|Import *.la2 text by Giza(tr1ton)")
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", action="store_true", help="Process .la2 files")
    parser.add_argument("-i", action="store_true", help="Process .la2 files")
    parser.add_argument("input_file", help="File .la2")
    args = parser.parse_args()

    base_filename = os.path.splitext(args.input_file)[0]
    read_txtfile = f"{base_filename}_text.csv"
    if args.e:
        unpack_binary_with_text(args.input_file, read_txtfile)
    elif args.i:
        modify_binary_with_text(args.input_file, read_txtfile)

if __name__ == '__main__':
    main()
