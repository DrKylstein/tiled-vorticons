'''
Commander Keen 1-3 level loader/saver
2014 <dr.kylstein@gmail.com>
'''

from __future__ import print_function
import math
import rlew
import file_gen_util as util

RLEW_FLAG = 0xFEFE

HEADER_FIELDS = ('width', 'height', 'plane_count', 'unk1', 'unk2', 'unk3', 
                'unk4', 'plane_size', 'unk5', 'unk6', 'unk7', 'unk8', 'unk9', 
                'unkA', 'unkB', 'unkC')
HEADER_LENGTH = len(HEADER_FIELDS)

def log(words):
    for word in words:
        print(word)
        yield word

def load(file):
    words = rlew.unrlew(util.first(util.uniform_file( "<H", open(file, 'rb'))), 
        0xFEFE)
    for i in range(2):
        words.next()
    return _level(words)

def save(file, level):
    _regen_header(level)
    size = HEADER_LENGTH*2 + level['plane_size']*2
    size = [size & 0xFFFF, size >> 16]
    compressed = size+[item for item in rlew.rlew(_dump_level(level), 
        RLEW_FLAG)]
    #compressed = size+[item for item in _dump_level(level)]
    
    util.uniform_file_out('<H', open(file, 'wb'), util.tupelize(iter(
        compressed)))

def _plane(width, height, remainder, words):
    plane = [[words.next() for x in range(width)] for y in range(height)]
    
    for i in range(remainder):
        words.next()
        
    return plane
  
def _regen_header(level):
    if not 'plane_size' in level:
        size = level['width']*level['height']*2
        level['plane_size'] = int(math.ceil(size/16.0)*16)
    if not 'plane_count' in level:
        level['plane_count'] = 2
    for key in HEADER_FIELDS:
        if key not in level:
            level[key] = 0
    
def _level(words):
    level = {}
    
    header_words = []
    for i in range(HEADER_LENGTH):
        header_words.append(words.next())
        
    level.update(dict(zip(HEADER_FIELDS, header_words)))
    
    remainder = _plane_padding(level)
        
    level['tiles'] = _plane(level['width'], level['height'], remainder, words)

        
    level['sprites'] = _plane(level['width'], level['height'], remainder, 
        words)

    
    return level
    
def _dump_level(level):
    for key in HEADER_FIELDS:
        yield level[key]
        
    remainder = _plane_padding(level)
        
    for row in level['tiles']:
        for tile in row:
            yield tile
            
    for i in range(remainder):
        yield 0
            
    for row in level['sprites']:
        for sprite in row:
            yield sprite
            
    for i in range(remainder):
        yield 0
    
def _plane_padding(level):
    return level['plane_size']/2 - level['width']*level['height']
    
if __name__ == '__main__':
    level = load('LEVEL80.CK1')
    for key, item in level.items():
        print(key, item)
    print(level['width'], level['height'])
    for row in level['tiles']:
        for tile in row:
            print("{:<7}".format(hex(tile)), end=' ')
        print()
        
    loop = _level(_dump_level(level))
    
    if loop == level:
        print("Great Success!")
    else:
        print("Fission Mailed!")
        print(loop)
        print(loop['width'], loop['height'])
        for row in loop['tiles']:
            for tile in row:
                print("{:<7}".format(hex(tile)), end=' ')
            print()   
        
    save('LEVEL99.CK1', level)
    
