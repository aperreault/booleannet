"""
Grammar file for a boolean parser based on PLY
"""
import random, time, sys
import tokenizer, util, state
from ply import yacc
from itertools import *

# a list of all valid modes
PLDE, SYNC, ASYNC, RANK, TIME = 'plde sync async rank time'.split()

# valid modes of operation
VALID_MODES = [ PLDE, SYNC, ASYNC, RANK, TIME ] 

# the labels will be set to 1 for these
NOLABEL_MODE = [ PLDE, SYNC, ASYNC] 

# will contain the last parsed line,  used to improve error reporting
LAST_LINE = ''

tokens = tokenizer.Lexer.tokens

precedence = (
    ('left',  'OR'),
    ('left',  'AND'),
    ('right', 'NOT'),
)

# YACC style grammar rules below

def p_stmt_init(p):
    'stmt : ID EQUAL stmt '    

    # this will only be executed during initialization
    p.parser.RULE_SETVALUE( p.parser.old, p[1], p[3], p)
    p.parser.RULE_SETVALUE( p.parser.new , p[1], p[3], p)       
    p[0] = p[3]

def p_stmt_assign(p):
    'stmt : ID ASSIGN EQUAL stmt '
    p.parser.RULE_SETVALUE( p.parser.new, p[1], p[4], p)    
    p[0] = p[4]

def p_stmt_expression(p):
    'stmt : expression'    
    p[0] = p[1]
 
def p_expression_id(p):
    "expression : ID"

    # this is the only distinction bewtween synchronous and asynchronous updating
    if p.parser.sync:
        p[0] = p.parser.RULE_GETVALUE( p.parser.old, p[1], p)
    else:                        
        p[0] = p.parser.RULE_GETVALUE( p.parser.new, p[1], p)

def p_expression_state(p):
    "expression : STATE"

    if p[1] == 'Random':
        value = random.choice( (True, False) ) 
    else:
        value = ( p[1] == 'True' )

    # plde mode will transforms the boolean values to triplets
    if p.parser.mode ==  PLDE:
        value = util.bool_to_tuple( value )

    p[0] = value

def p_expression_tuple(p):
    "expression : LPAREN NUMBER COMMA NUMBER COMMA NUMBER RPAREN"
    if p.parser.mode == PLDE:
        p[0] = (p[2], p[4], p[6])
    else:
        p[0] = p[2] > p[6] / p[4]

def p_expression_paren(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]

def p_expression_binop(p):
    """expression : expression AND expression
                  | expression OR expression 
    """
    if p[2] == 'and'  : 
        p[0] = p.parser.RULE_AND( p[1], p[3], p )
    elif p[2] == 'or': 
        p[0] = p.parser.RULE_OR( p[1], p[3], p )
    else:
        util.error( "unknown operator '%s'" % p[2] )   
   
def p_expression_not(p):
    "expression : NOT expression "
    p[0] = p.parser.RULE_NOT( p[2], p )

def p_label_init(p):
    'stmt : LABEL '    

    # this is for silencing unused token warnings, 
    # labels are not used in the grammar
    util.error('invalid construct')

def p_error(p):
    if hasattr(p, 'value'):
        util.warn( 'at %s' % p.value )
    msg = "Syntax error in -> '%s'" % LAST_LINE
    util.error( msg )

class Parser(object):
    "Represents a boolean parser"
    def __init__(self, mode, text ):
        """
        Main parser baseclass for all models
        """

        # check the validity of modes
        if mode not in VALID_MODES:
            util.error( 'mode parameter must be one of %s' % VALID_MODES)

        # initialize the parsers
        self.parser = yacc.yacc( write_tables=0, debug=0 )
        
        # set the mode
        self.parser.mode  = mode

        # optimization: this check is used very often 
        self.parser.sync =  self.parser.mode == SYNC

        # define default functions
        def get_value(state, name, p):
            return  getattr( state, name )

        def set_value(state, name, value, p):
            setattr( state, name, value )
            return value

        #
        # setting the default rules
        #
        self.parser.RULE_AND = lambda a, b, p: a and b
        self.parser.RULE_OR  = lambda a, b, p: a or b
        self.parser.RULE_NOT = lambda a, p: not a
        self.parser.RULE_SETVALUE = set_value
        self.parser.RULE_GETVALUE = get_value
        self.parser.RULE_START_ITERATION = lambda index, model: index

        #
        # internally we'll maintain a full list of tokens 
        #
        self.tokens = tokenizer.tokenize( text )
        self.nodes  = tokenizer.get_nodes( self.tokens )

        # isolate various types of tokens
        self.init_tokens   = tokenizer.init_tokens( self.tokens )
        self.update_tokens = tokenizer.update_tokens( self.tokens )
        self.label_tokens  = tokenizer.label_tokens( self.update_tokens ) 
        self.async_tokens  = tokenizer.async_tokens( self.update_tokens ) 
      
        # finding the initial and update nodes
        self.init_nodes   = tokenizer.get_nodes( self.init_tokens )
        self.update_nodes = tokenizer.get_nodes( self.update_tokens )

        # find uninizitalized nodes        
        self.uninit_nodes = self.update_nodes - self.init_nodes

        # populate the initializer lines
        self.init_lines = map( tokenizer.tok2line, self.init_tokens )

        # populate the body by the ranks            
        labelmap = {} 
        for tokens in self.async_tokens:
            labelmap.setdefault( 1, []).append( tokens )            

        # overwrite the label token's value in nolabel modes
        if self.parser.mode in NOLABEL_MODE:
            for token in self.label_tokens:
                token[0].value = 1
        
        # for all PLDE, SYNC and ASYNC modes all ranks will be set to 1
        for tokens in self.label_tokens:
            rank  = tokens[0].value
            short = tokens[1:]
            labelmap.setdefault( rank, []).append( short )            
        
        # will iterate over the ranks in order
        self.ranks = list(sorted(labelmap.keys()))

        # build another parseable text, as lines stored for rank keys
        # by shuffling, sorting or reorganizing this body we can
        # implement various updating rule selection strategies
        self.update_lines = {}
        for key, values in labelmap.items():
            self.update_lines.setdefault(key, []).extend( map(tokenizer.tok2line, values))

class Model(Parser):
    """
    Maintains the functionality for all models
    """

    def initialize(self, missing=None, defaults={} ):
        """
        Initializes the model, needs to be called to reset the simulation 
        """

        # create a new lexer                
        self.lexer = tokenizer.Lexer().lexer
        
        self.parser.old = state.State()
        self.parser.new = state.State()
       
        # references must be attached to the parser class 
        # to be visible during parsing
        self.states = self.parser.states = [ self.parser.old ]

        # parser the initial data
        map( self.local_parse, self.init_lines )

        # deal with uninitialized nodes
        if self.uninit_nodes:
            if missing:
                for node in self.uninit_nodes:
                    value = missing( node )
                    self.parser.RULE_SETVALUE( self.parser.old, node, value, None)
                    self.parser.RULE_SETVALUE( self.parser.new, node, value, None)
            else:
                util.error( 'uninitialized nodes: %s' % list(self.uninit_nodes))

        # override any initalization with defaults
        for node, value in defaults.items():
            self.parser.RULE_SETVALUE( self.parser.old, node, value, None)
            self.parser.RULE_SETVALUE( self.parser.new, node, value, None)
        
        # will be populated upon the first call
        self.lazy_data = {}

    @property
    def first(self):
        "Returns the first state"
        return self.states[0]

    @property
    def last(self):
        "Returns the last state"
        return self.states[-1]

    @property
    def data(self):
        """
        Allows access to states via a dictionary keyed by the nodes
        """
        # this is an expensive operation so it loads lazily
        assert self.states, 'States are empty'
        if not self.lazy_data:
            nodes = self.first.keys()
            for state in self.states:
                for node in nodes:
                    self.lazy_data.setdefault( node, []).append( state[node] )
        return self.lazy_data

    def __update(self):       
        """Internal update function"""
        p = self.parser       
        p.old = p.new
        p.new = p.new.copy()                     
        p.states.append( p.new )

    def local_parse( self, line ):
        "Used like such only to keep track of the last parsed line"
        global LAST_LINE
        LAST_LINE = line
        return self.parser.parse( line )

    def iterate( self, steps, shuffler=util.default_shuffler, **kwds ):
        """
        Iterates over the lines 'steps' times. Allows other parameters for compatibility with the plde mode
        """
        
        # needs to be reset in case the data changes
        self.lazy_data = {}

        for index in xrange(steps):
            self.parser.RULE_START_ITERATION( index, self )
            self.__update()
            for rank in self.ranks:
                lines = self.update_lines[rank]
                lines = shuffler( lines )
                map( self.local_parse, lines ) 

    def save_states(self, fname):
        """
        Saves the states into a file
        """
        if self.states:
            fp = open(fname, 'wt')
            cols = [ 'STATE' ] + self.first.keys() 
            hdrs = util.join ( cols )
            fp.write( hdrs )
            for state in self.states:
                cols = [ state.fp() ] + state.values()
                line = util.join( cols )
                fp.write( line )
            fp.close()
        else:
            util.error( 'no states have been created yet' )

    def detect_cycles( self ):
        "Detect the cycles in the current states of the model"
        return util.detect_cycles( data=self.fp() )                

    def report_cycles(self ):
        """
        Convenience function that reports on steady states
        """
        index, size = self.detect_cycles()
        
        if size == 0:
            print "No cycle or steady state could be detected from the %d states" % len(self.states)
        elif size==1:
            print "Steady state starting at index %s -> %s" % (index, self.states[index] )
        else:
            print "Cycle of length %s starting at index %s" % (size, index)
    
    def fp(self):
        "The models current fingerprint"
        return [ s.fp() for s in self.states ]

if __name__ == '__main__':
    

    text = """
    A = True

    1: A* = not A
    2: B* = not B
    """

    model = Model( mode='sync', text=text )

    model.initialize( missing=util.true )
    
    
    print '>>>', model.first

    model.iterate( steps=2 )
    
    print model.fp()

    model.report_cycles()

    model.save_states( fname='states.txt' )

    fprints = ['S1', 'S2', 'S1', 'S2', 'S1', 'S2']

    print util.detect_cycles( fprints )

    


    '''
    model.initialize( )

    shuffler = lambda x: []
    model.iterate( steps=10, shuffler=shuffler)
    
    for state in model.states[:10]:
        print state
    
    model.report_cycles()
    print model.fp()
    '''          