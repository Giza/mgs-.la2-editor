import struct
import os
import argparse

def unpack_binary_with_text(binary_filename, text_filename, widths, heights):
    """
    This function takes a binary file and a text file,
    reads the binary file, extracts the font data,
    and writes it to the text file.
    """
    with open(binary_filename, "rb") as f:
        # Seek to the offset, which is stored at 0x2C
        f.seek(0x2C)

        # Read the offset, which is a 32-bit unsigned integer
        offset = struct.unpack("<I", f.read(4))[0]
        print(f"offset: {offset}")

        # Seek to the offset, which is where the font data starts
        f.seek(offset)

        # Read the length of the font data, which is also a 32-bit
        # unsigned integer
        length_fonts = struct.unpack("<I", f.read(4))[0]
        print(f"length_fonts: {length_fonts}")

        # Open the text file for writing, in UTF-8 format
        with open(text_filename, "w", encoding="utf-8") as out:

            # Write the length of the font data to the text file
            out.write(f"{length_fonts}\n")

            # Iterate over each font
            for i in range(length_fonts):

                # Seek 4 bytes forward, ignoring the font data
                f.seek(4, 1)

                # Read the number of iterations, which is a 16-bit
                # unsigned integer
                num_iterations = struct.unpack("<H", f.read(2))[0]
                print(f"num_iterations: {num_iterations}")

                # Read the length of the data, which is also a 16-bit
                # unsigned integer
                length = struct.unpack("<H", f.read(2))[0]
                print(f"length: {length}")

                # Write the number of iterations to the text file
                out.write(f"{num_iterations}\n")
                print("Width:", widths[i])
                print("Height:", heights[i])
                x_pixcel = 65535/int(widths[i])
                y_pixcel = 65535/int(heights[i])
                print("x_pixcel:", x_pixcel)
                print("y_pixcel:", y_pixcel)
                

                # Iterate over each iteration
                for _ in range(num_iterations):

                    # Read the width, height, x_start, x_end, y_start,
                    # y_end, and char of the font, which are all
                    # 16-bit unsigned integers
                    width_char = struct.unpack("<H", f.read(2))[0]
                    height_char = struct.unpack("<H", f.read(2))[0]
                    #x_start = "%04x" % struct.unpack("<H", f.read(2))[0]
                    x_start = struct.unpack("<H", f.read(2))[0]/x_pixcel
                    #x_end = "%04x" % struct.unpack("<H", f.read(2))[0]
                    x_end = struct.unpack("<H", f.read(2))[0]/x_pixcel
                    #y_start = "%04x" % struct.unpack("<H", f.read(2))[0]
                    y_start = struct.unpack("<H", f.read(2))[0]/y_pixcel
                    #y_end = "%04x" % struct.unpack("<H", f.read(2))[0]
                    y_end = struct.unpack("<H", f.read(2))[0]/y_pixcel
                    char = struct.unpack("<I", f.read(4))[0]
                    #width, height
                    #x_start = 65535/width

                    # Write the width, height, x_start, x_end, y_start,
                    # y_end, and char to the text file, separated by spaces
                    out.write(f"{width_char} {height_char} {round(x_start)} {round(x_end)} {round(y_start)} {round(y_end)} {char}\n")

def modify_binary_with_text(binary_filename, text_filename, widths, heights):
    with open(binary_filename, "r+b") as binary_file, open(text_filename, "r") as text_file, open(binary_filename+"_new_font", "wb") as w:
        bytes=binary_file.read(0x2C)
        w.write(bytes)

        offset = struct.unpack("<I", binary_file.read(4))[0]
        w.write(struct.pack("<I", int(offset)))

        bytes=binary_file.read(offset-48+4)
        w.write(bytes)

        text_data = text_file.readline().strip()
        for i in range(int(text_data)):
            binary_file.read(0x04)
            w.write(b'\x00\x00\x00\x00')

            print("Width:", widths[i])
            print("Height:", heights[i])
            x_pixcel = 65535/int(widths[i])
            y_pixcel = 65535/int(heights[i])
            print("x_pixcel:", x_pixcel)
            print("y_pixcel:", y_pixcel)

            num_iterations_oreg = struct.unpack("<H", binary_file.read(2))[0]
            num_iterations = text_file.readline().strip()
            w.write(struct.pack("<H", int(num_iterations)))

            length_font_oreg = struct.unpack("<H", binary_file.read(2))[0]
            print(length_font_oreg)
            length_font=(int(num_iterations)*16)+8
            w.write(struct.pack("<H", int(length_font)))

            binary_file.read(length_font_oreg-8)

            for _ in range(int(num_iterations)):
                width_char, height_char, x_start, x_end, y_start, y_end, char = map(str.strip, text_file.readline().split())
                #x_start = int(x_start, 16)
                x_start = int(x_start)*x_pixcel
                #x_end = int(x_end, 16)
                #print(x_end)
                x_end = int(x_end)*x_pixcel
                #y_start = int(y_start, 16)
                y_start = int(y_start)*y_pixcel
                #y_end = int(y_end, 16)
                y_end = int(y_end)*y_pixcel
                w.write(struct.pack("<H", int(width_char)))
                w.write(struct.pack("<H", int(height_char)))
                w.write(struct.pack("<H", round(x_start)))
                w.write(struct.pack("<H", round(x_end)))
                w.write(struct.pack("<H", round(y_start)))
                w.write(struct.pack("<H", round(y_end)))
                w.write(struct.pack("<I", int(char)))
        
        w.write(binary_file.read())
        #print(length_font_oreg)
        #w.write(struct.pack("<H", int(length_font_oreg)))

        
        

def main():
    print("MGS 3 Export|Import *.la2 font data by Giza(tr1ton)")
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", action="store_true", help="Process .la2 files")
    parser.add_argument("-i", action="store_true", help="Process .la2 files")
    parser.add_argument("input_file", help="File .la2")
    for i in range(1, 10):
        parser.add_argument(f"resolution_{i}", help="Font resolution (ex. 1920x1080)")
    args = parser.parse_args()

    #width, height = args.resolution_1.split("x")
    widths = []
    heights = []

    for i in range(1, 10):
        resolution_str = getattr(args, f"resolution_{i}")
        width, height = resolution_str.split("x")
        widths.append(int(width))  # Convert width to integer
        heights.append(int(height))  # Convert height to integer
    #print("Widths:", widths)
    #print("Heights:", heights)
    #exit()
    base_filename = os.path.splitext(args.input_file)[0]
    read_txtfile = f"{base_filename}_font.txt"
    if args.e:
        unpack_binary_with_text(args.input_file, read_txtfile, widths, heights)
    elif args.i:
        modify_binary_with_text(args.input_file, read_txtfile, widths, heights)

if __name__ == '__main__':
    main()
