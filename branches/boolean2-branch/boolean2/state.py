"""
Classes to represent state of the simulation

Also may be used to generate initial states
"""

# helps generate a user friendly ID to each state


class State(object):
    """
    Represents a state

    >>> state = State( b=0, c=1)
    >>> state.a = 1
    >>> state
    State: a=1, b=0, c=1
    >>> state.fp()
    'S1'
    >>> state.bin()
    '101'
    """
    MAPPER, COUNTER  = {}, 0

    def __init__(self, **kwds ):
        self.__dict__.update( kwds )
    
    def __getitem__(self, key):
        return self.__dict__[key]
    
    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):  
        "Default string format"
        items = [ '%s=%s' % x for x in self.items() ]
        items = ', '.join(items)
        return 'State: %s' % items
   
    def items(self):
        "Returns the sorted keys"
        return sorted( self.__dict__.items() )

    def keys(self):
        "Returns the sorted keys"
        return [ x for x,y in self.items() ]

    def values(self):
        "Returns the values by sorted keys"
        return [ y for x,y in self.items() ]

    def __iter__(self):
        return iter( self.keys() )

    def copy(self):            
        "Duplicates itself"
        s = State( **self.__dict__ )
        return s

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def fp(self):
        "Returns a unique user friendly state definition"
        
        value = hash( str(self) )
        
        if value not in State.MAPPER:
            State.COUNTER += 1
            State.MAPPER[value] = 'S%d' % State.COUNTER

        return State.MAPPER[value]
    
    def bin( self ):
        "A binary representation of the states"
        values = map(str, map(int, self.values()))
        return ''.join(values)

CACHE = {}
def bit2int(bits):
    """
    Returns the integer corresponding of a bit state. 
    It only computes each bit once then stores the result to be faster

    """
    global CACHE

    if bits not in CACHE:
        value = 0
        for p, c in enumerate( reversed(bits) ):
            value += c * 2 ** p
        CACHE[bits] = value
    return CACHE[bits]

def int2bit(x, w=20):
    """
    Generates a binary representation of an integer number (as a tuple)
    
    >>> bits = int2bit(10, w=4)
    >>> bits
    (1, 0, 1, 0)
    >>> bit2int( bits )
    10
    """
    bits = [ ]
    while x:
        bits.append(x%2)
        x /= 2
    
    # a bit of padding
    bits = bits + [ 0 ] * w
    bits = bits[:w]
    bits.reverse()
    return tuple(bits)

def lookup_generator( nodes ):
    """
    Returns a generator that produces functions 
    can be used to initialize states.
    
    On each call to the lookup generator a different initial state 
    initializer will be produced
    """
    nodes = list(sorted(nodes))
    size  = len(nodes)
    for index in xrange( 2 ** size ):
        bits  = int2bit(index, w=size )
        bools = map(bool, bits)
        store = dict( zip(nodes, bools) )
        def lookup( node ):
            return store[node]
        yield lookup
        
def test():
    """
    Main testrunnner
    """
    # runs the local suite
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
    nodes = "A B C".split()
    gen = lookup_generator(nodes)

    for f in gen:
        print map(f, nodes)

