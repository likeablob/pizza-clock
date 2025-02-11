from lib.board_holder import board_holder
from lib.pizza_stand import pizza_stand, pizza_stand_lid

OUT_DIR = "."

pizza_stand().save_as_scad(filename="pizza_stand.scad", outdir=OUT_DIR)
pizza_stand_lid().save_as_scad(filename="pizza_stand_lid.scad", outdir=OUT_DIR)
board_holder().save_as_scad(filename="board_holder.scad", outdir=OUT_DIR)
