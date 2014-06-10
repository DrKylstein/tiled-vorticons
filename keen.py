'''
Commander Keen 1-3 support for Tiled
2014 <dr.kylstein@gmail.com>
http://imgur.com/9qaOUWy
'''
import os
import os.path
from tiled import *
from tiled.qt import *
from keenlib.ted15 import load
from keenlib.ted15 import save

class KeenVorticons(Plugin):
        
    @classmethod
    def nameFilter(cls):
        return 'Keen 1-3 Level (level??.ck? LEVEL??.CK? level??.CK? LEVEL??.ck?)'

    @classmethod
    def supportsFile(cls, f):
        if not f[:-1].lower().endswith('.ck'):
            return False
        return True
        
    @classmethod
    def read(cls, f):
        level = load(f)
        
        map = Tiled.Map(Tiled.Map.Orthogonal, level['width'], level['height'], 16, 16)
        tset = Tiled.Tileset('Tiles', 16, 16, 0, 0)
        
        directory = os.path.dirname(f)
        episode = int(f[-1])
        is_world = int(os.path.splitext(os.path.basename(f))[0].lower()[-2:]) >= 80
        
        tileImageName = caseInsensitiveFile(directory, '{}TIL0000.BMP'.format(episode))
        if tileImageName == None:
            print 'No tileset file found'
            return map
        
        tileImage = QImage()
        if not tileImage.load(os.path.join(directory, tileImageName), 'BMP'):
            print 'Unable to open {}'.format(tileImageName)
            return map
            
        tset.loadFromImage(tileImage, tileImageName)
        tileLayer = Tiled.TileLayer('Tile Plane', 0,0, level['width'], 
            level['height'])
        spriteLayer = Tiled.ObjectGroup('Sprite Plane', 0,0, level['width'], 
            level['height'])
            
        for y in xrange(level['height']):
            for x in xrange(level['width']):
                index = level['tiles'][y][x]
                tileLayer.setCell(x, y, Tiled.Cell(tset.tileAt(index)))
        
        sprite_size = QSizeF(16,16)
        
        for y in range(level['height']):
            for x in range(level['width']):
                spriteNum = level['sprites'][y][x]
                sprite = None
                
                pos = QPointF(x*16, y*16)
                
                def create_sprite(name, type):
                    return Tiled.MapObject(name, type, pos, sprite_size)
                
                if is_world:
                    if spriteNum == 0:
                        pass
                    elif spriteNum == 255:
                        sprite = create_sprite(sprite_name(spriteNum, episode), 'Player')
                    elif spriteNum == 20:
                        sprite = create_sprite('Ship', 'Ship')
                    elif spriteNum & 0x8000:
                        sprite = create_sprite('Barricade (Level {})'.format(spriteNum & 0x7FFF), 'Barricade')
                        sprite.setProperty('Level', '{}'.format(spriteNum & 0x7FFF))
                    elif spriteNum < 32:
                        sprite = create_sprite('Level {}'.format(spriteNum), 'Level')
                        sprite.setProperty('Level', '{}'.format(spriteNum))
                    else:
                        sprite = create_sprite('Special {}'.format(hex(spriteNum)), 'Special')
                        sprite.setProperty('ID', '{}'.format(spriteNum))
                else:
                    if spriteNum == 0:
                        pass
                    elif spriteNum == 255:
                        sprite = Tiled.MapObject(sprite_name(spriteNum, episode), 'Player', pos, QSizeF(16,32))
                    elif spriteNum > 32:
                        sprite = create_sprite('Switch ({})'.format(hex(spriteNum)), 'Switch')
                        sprite.setProperty('Target', '{}, {}'.format(*load_coordinates(spriteNum)))
                    else:
                        sprite = create_sprite(sprite_name(spriteNum, episode), 'Enemy')
                        sprite.setProperty('ID', '{}'.format(spriteNum))
                    
                if sprite is not None:
                    spriteLayer.addObject(sprite)
                
        map.addLayer(tileLayer)
        map.addLayer(spriteLayer)
        map.addTileset(tset)
        return map
          
    @classmethod
    def write(cls, m, f):
        tileLayer_ = None
        spriteLayer = None
        
        for i in range(m.layerCount()):
            if isTileLayerAt(m, i):
                tileLayer_ = tileLayerAt(m, i)
            elif isObjectGroupAt(m, i):
                spriteLayer = objectGroupAt(m, i)
        
        if tileLayer_ is None:
            print 'Must have one TileLayer!'
            return False
            
        print tileLayer_
            
        if spriteLayer is None:
            print 'Must have one ObjectGroup!'
            return False
            
        level = {'width':tileLayer_.width(), 'height':tileLayer_.height(), 'tiles':[], 'sprites':[]}
        
        for y in range(tileLayer_.height()):
            level['tiles'].append([])
            level['sprites'].append([])
            for x in range(tileLayer_.width()):
                cell = tileLayer_.cellAt(x, y)
                level['tiles'][y].append(cell.tile.id())
                level['sprites'][y].append(0)
        
        for i in range(spriteLayer.objectCount()):
            item = spriteLayer.objectAt(i)
            x = int(item.x()/16)
            y = int(item.y()/16)
            if item.type() == 'Player':
                level['sprites'][y][x] = 255
            elif item.type() == 'Enemy' or item.type() == 'Special':
                level['sprites'][y][x] = int(item.property('ID'))
            elif item.type() == 'Switch':
                pair = item.property('Target').split(', ')
                pair[0] = int(pair[0])
                pair[1] = int(pair[1])
                level['sprites'][y][x] = dump_coordinates(pair)
            elif item.type() == 'Ship':
                level['sprites'][y][x] = 20
            elif item.type() == 'Level':
                level['sprites'][y][x] = int(item.property('Level'))
            elif item.type() == 'Barricade':
                level['sprites'][y][x] = int(item.property('Level')) | 0x8000
        
        save(f, level)
        
        return True


def caseInsensitiveFile(path, name):
    candidates = os.listdir(path)
    for item in candidates:
        if item.lower() == name.lower():
            return item
    return None
    
def load_coordinates(ushort):
    y = ushort >> 8
    x = ushort & 0xFF
    if x & 0x80:
        x = -(0xFF-x)
    if y & 0x80:
        y = -(0xFF-y)
    
    return (x, y)
    
def dump_coordinates(pair):
    y = pair[1] & 0xFF
    x = pair[0] & 0xFF
    if x & 0x80:
        x = 0xFF-x
    if y & 0x80:
        y = 0xFF-y
    ushort = (x | (y << 8))
    
_names = (
    {},
    {
        1:'Yorp', 
        2:'Garg',
        3:'Vorticon', 
        4:'ButlerBot', 
        5:'TankBot', 
        6:'Cannon up/right', 
        7:'Cannon up', 
        8:'Cannon down', 
        9:'Cannon up/left', 
        10:'Chain',
        255:'Keen'
    },
    {
        1:'Grunt', 
        2:'Youth', 
        3:'Elite', 
        4:'Scrub', 
        5:'GuardBot', 
        6:'Platform', 
        7:'Amoeba',
        255:'Keen'
    },
    {
        1:'Grunt', 
        2:'Youth', 
        3:'Mother', 
        4:'Meep', 
        5:'Vortininja', 
        6:'Foob', 
        7:'Ball', 
        8:'Jack', 
        9:'Horizontal Platform', 
        10:'Vertical Platform', 
        11:'Grunt Jumping', 
        12:'Spark', 
        13:'Heart', 
        14:'Turret Right', 
        15:'Turret Down', 
        16:'Arm', 
        17:'Left Leg', 
        18:'Right Leg',
        255:'Keen'
    }
)

def sprite_name(num, ep):
    if num in _names[ep]:
        return _names[ep][num]
    return hex(num)