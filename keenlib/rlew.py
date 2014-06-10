'''
Commander Keen 1-3 RLEW compression
2014 <dr.kylstein@gmail.com>
'''


def rlew(words, flag):
    last = words.next()
    repeat = 1
    words_left = True
    while words_left:
        try:
            word = words.next()
        except StopIteration:
            word = None
            words_left = False
            
        if word == last:
            repeat += 1
        elif repeat > 1 or last == flag:
            if repeat > 3:
                yield flag
                yield repeat
                yield last
            else:
                for i in range(repeat):
                    yield last
            repeat = 1
        else:
            yield last
            
        last = word

def unrlew(words, flag):
    try:
        while True:
            word = words.next()
            if word == flag:
                repeat = words.next()
                value = words.next()
                for i in range(repeat):
                    yield value
            else:
                yield word
    except StopIteration:
        pass
            
if __name__ == '__main__':
    from random import randrange
    words = []
    for i in range(10):
        val = randrange(0, 0xFFFF)
        for j in range(randrange(0,8)):
            words.append(val)
    compressed = [word for word in rlew(iter(words), 0xFEFE)]
    for word in words:
        print hex(word)
    print ""
    for word in compressed:
        print hex(word)
        
    loop = [word for word in unrlew(iter(compressed), 0xFEFE)]
    
    print ""
    
    for pair in zip(loop, words):
        print "{} {}".format(hex(pair[0]), hex(pair[1]))
    
    if loop == words:
        print "Great success!"
    else:
        print "Fission mailed!"
