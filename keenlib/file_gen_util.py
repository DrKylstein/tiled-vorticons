'''
Misc utilities for binary files
2014 <dr.kylstein@gmail.com>
'''
import struct

def uniform_file(fmt, f):
    unpacker = struct.Struct(fmt);
    while True:
        s = f.read(unpacker.size);
        if s:
            yield unpacker.unpack(s)
        else:
            return
            
def uniform_file_out(fmt, f, structs):
    packer = struct.Struct(fmt);
    for s in structs:
        f.write(packer.pack(s))

def tupelize(items):
    for item in items:
        yield (item)

def first(it):
    for sub_it in it:
        yield sub_it[0]
        
def prepend(first, it):
    for item in first:
        yield item
        
    for item in it:
        yield item