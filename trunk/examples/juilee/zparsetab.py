
# zparsetab.py
# This file is automatically generated. Do not edit.

_lr_method = 'LALR'

_lr_signature = '\xefjd\xd5\xd7\x88\xc3\xee)\xb0\x834\xd7G\x87\x12'

_lr_action_items = {'AND':([2,6,7,10,11,12,18,19,20,27,],[-5,13,-4,13,-4,-10,-7,-8,13,-6,]),'RPAREN':([2,10,11,12,18,19,20,26,27,],[-5,18,-4,-10,-7,-8,-9,27,-6,]),'ASSIGN':([8,],[16,]),'NUMBER':([4,17,25,],[9,23,26,]),'RANK':([0,15,22,],[1,1,1,]),'OR':([2,6,7,10,11,12,18,19,20,27,],[-5,14,-4,14,-4,-10,-7,-8,-9,-6,]),'STATE':([0,4,5,13,14,15,22,],[2,2,2,2,2,2,2,]),'COMMA':([9,23,],[17,25,]),'LPAREN':([0,4,5,13,14,15,22,],[4,4,4,4,4,4,4,]),'NOT':([0,4,5,13,14,15,22,],[5,5,5,5,5,5,5,]),'=':([7,16,],[15,22,]),'ID':([0,1,4,5,13,14,15,22,],[7,8,11,11,11,11,7,7,]),'$end':([2,3,6,7,11,12,18,19,20,21,24,27,],[-5,0,-3,-4,-4,-10,-7,-8,-9,-1,-2,-6,]),}

_lr_action = { }
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _lr_action.has_key(_x):  _lr_action[_x] = { }
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'expression':([0,4,5,13,14,15,22,],[6,10,12,19,20,6,6,]),'stmt':([0,15,22,],[3,21,24,]),}

_lr_goto = { }
for _k, _v in _lr_goto_items.items():
   for _x,_y in zip(_v[0],_v[1]):
       if not _lr_goto.has_key(_x): _lr_goto[_x] = { }
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S'",1,None,None,None),
  ('stmt',3,'p_stmt_init','../..\\boolean\\engine.py',31),
  ('stmt',5,'p_stmt_assign','../..\\boolean\\engine.py',40),
  ('stmt',1,'p_stmt_expression','../..\\boolean\\engine.py',45),
  ('expression',1,'p_expression_id','../..\\boolean\\engine.py',49),
  ('expression',1,'p_expression_state','../..\\boolean\\engine.py',60),
  ('expression',7,'p_expression_tuple','../..\\boolean\\engine.py',77),
  ('expression',3,'p_expression_paren','../..\\boolean\\engine.py',84),
  ('expression',3,'p_expression_binop','../..\\boolean\\engine.py',88),
  ('expression',3,'p_expression_binop','../..\\boolean\\engine.py',89),
  ('expression',2,'p_expression_not','../..\\boolean\\engine.py',99),
]
