import sys
from draw_graph import Planter

arg_cnt = len(sys.argv)
if arg_cnt != 3:
    print('Error: wrong number of arguments')
    print('Usage: python3 draw msg_def_file model_file')
    exit()

msg_def = sys.argv[1]
model = sys.argv[2]

pt = Planter()

# pt.draw('large.msg','model.txt')
pt.draw(msg_def, model)