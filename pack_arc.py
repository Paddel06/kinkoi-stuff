# (Re)Packing .ARCs used in Saga Planets/Entergram PSVita VNs - by Paddel06

import os
# import glob
import sys

# Some parameters, probably constant anyways though:
enc = 'cp932'
endian = 'little'
str_pad = 64
arc_pad_ext = 64 # visuals
arc_pad_scr = 8  # script

# Creating the info.bin for scripts:
def make_bin_scr (inPath, binName='00_info.bin'):
    print('Creating', binName, '...')
    with open(inPath + binName, 'wb') as bin_scr:
        label_count = 0
        bin_scr.write(bytes(8)) # make space for label_count later
        for file in os.listdir(inPath): # Should be ordered by character index, not windows or whatever. So far, it always was, but who knows how long...
            if file.endswith('.txt'): # because apparently "for file in glob.glob(inPath + '*.txt'):" doesn't work...
                with open(inPath + file, 'r', encoding=enc) as script:
                    file_name = bytes(file + '\x00', enc) # null-terminate string
                    label_ofs = 0
                    for line in script:
                        if line.find('<label ') != -1:
                            label_count += 1
                            label_name = bytes(line[7:-2] + '\x00', enc) # "extract" name and null-terminate
                            bin_scr.write(label_name)
                            bin_scr.write(b'\xfe' * (str_pad - len(label_name))) # pad string to required length, using 0xfe
                            bin_scr.write(file_name)
                            bin_scr.write(b'\xfe' * (str_pad - len(file_name)))
                            bin_scr.write(label_ofs.to_bytes(8, byteorder=endian))
                        label_ofs += len(bytes(line, enc)) + 1
        bin_scr.seek(0)
        bin_scr.write(label_count.to_bytes(8, byteorder=endian))
    print('Created', binName, 'with', label_count, 'labels.')

# Creating the info.bin for images (Is this even really needed? Are always the same anyways...)
# def make_bin_ext (inPath, img_res_x, img_res_y, binName='info.bin'):
#     UNKNOWN = b'\xcc' * 4
#     print('Creating', binName, '...')
#     with open(inPath, binName, 'wb') as bin_ext:
#         tile_count = 0
#         tile_pos_x = 0
#         tile_pos_y = 0
#         bin_ext.write(img_res_x.to_bytes(4, byteorder=endian))
#         bin_ext.write(img_res_y.to_bytes(4, byteorder=endian))
#         bin_ext.write(bytes(4))
#         bin_ext.write(UNKNOWN)
#         for file in os.listdir(inPath):
#             if file.endswith('.ext'):
#                 with open(inPath + file, 'rb') as tile:
#                     tile.seek(12)
#                     tile.read(4)
#                     tile_res_x = tile.tell()
#                     tile.read(4)
#                     tile_res_y = tile.tell()
#                     bin_ext.write(tile_pos_x + tile_pos_y)
#                     bin_ext.write(tile_res_x + tile_res_y)

# Creating the .ARC:
def pack_arc (inPath, arc_pad=arc_pad_scr, arcName='script.arc'):
    with open(arcName, 'wb') as archive:
        print('Creating', arcName, '...')
        file_list = os.listdir(inPath)
        file_count = len(file_list)
        index_len = (str_pad + 8) * file_count
        archive.write((index_len + 8).to_bytes(4, byteorder=endian))
        archive.write(file_count.to_bytes(4, byteorder=endian))
        indexCursor = archive.tell()
        archive.write(bytes(index_len))
        for file in file_list:
            if file_list.index(file) != 0 or archive.tell() % arc_pad != 0: # because apparently, if ofs%arc_pad==0, no padding after hdr...
                pad_bytes = arc_pad - (archive.tell() % arc_pad)
                archive.write(bytes(pad_bytes))
            file_name = bytes(file + '\x00', enc)
            file_size = os.path.getsize(inPath + file)
            file_ofs = archive.tell()
            archive.seek(indexCursor)
            archive.write(file_name + b'\xfe' * (str_pad - len(file_name)))
            archive.write(file_size.to_bytes(4, byteorder=endian))
            archive.write(file_ofs.to_bytes(4, byteorder=endian))
            indexCursor += str_pad + 8
            archive.seek(0, 2)
            with open(inPath + file, 'rb') as filedata:
                data = filedata.read()
                archive.write(data)
    print('Created', arcName, 'containing', file_count, 'files.')



filepath = sys.argv[1]
parentName = os.path.basename(os.path.normpath(filepath))
isScript = parentName == 'script.arc'

if isScript:
    make_bin_scr(filepath)
    pack_arc(filepath, arc_pad_scr)
else:
    pack_arc(filepath, arc_pad_ext, parentName)

print('...DONE!')
#input()
