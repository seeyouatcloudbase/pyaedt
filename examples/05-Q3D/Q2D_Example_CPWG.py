"""
2d Extractor: CPWG Analysis
---------------------------
This example shows how you can use PyAEDT to create a coplanar waveguide design
in Q2D and run a simulation.
"""

import os

from pyaedt import Q2d, Desktop
from pyaedt.generic.general_methods import generate_unique_name

###############################################################################
# Launch AEDT in Non-Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# You can change the Boolean parameter ``non_graphical`` to ``False`` to launch
# AEDT in graphical mode.

non_graphical = True

###############################################################################
# Launch AEDT and Q2D
# This example launches AEDT 2022.1 in graphical mode.
# This example use SI units.

q = Q2d(specified_version="2022.1", non_graphical=non_graphical, new_desktop_session=True,
        projectname=generate_unique_name("pyaedt_q2d_example"), designname="coplanar_waveguide")

###############################################################################
# Create variables

e_factor = "e_factor"
sig_bot_w = "sig_bot_w"
co_gnd_w = "gnd_w"
clearance = "clearance"
cond_h = "cond_h"
d_h = "d_h"
sm_h = "sm_h"

for var_name, var_value in {
    "sig_bot_w": "150um",
    "e_factor": "2",
    "gnd_w": "500um",
    "clearance": "150um",
    "cond_h": "50um",
    "d_h": "150um",
    "sm_h": "20um",
}.items():
    q[var_name] = var_value

delta_w_half = "({0}/{1})".format(cond_h, e_factor)
sig_top_w = "({1}-{0}*2)".format(delta_w_half, sig_bot_w)
co_gnd_top_w = "({1}-{0}*2)".format(delta_w_half, co_gnd_w)
model_w = "{}*2+{}*2+{}".format(co_gnd_w, clearance, sig_bot_w)

###############################################################################
# Create Primitives
# Define layer heights

layer_1_lh = 0
layer_1_uh = cond_h
layer_2_lh = layer_1_uh + "+" + d_h
layer_2_uh = layer_2_lh + "+" + cond_h

###############################################################################
# Create signal
# ~~~~~~~~~~~~~
base_line_obj = q.modeler.create_polyline([[0, layer_2_lh, 0], [sig_bot_w, layer_2_lh, 0]], name="signal")
top_line_obj = q.modeler.create_polyline([[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]])
q.modeler.move([top_line_obj], [delta_w_half, 0, 0])
q.modeler.connect([base_line_obj, top_line_obj])
q.modeler.move([base_line_obj], ["{}+{}".format(co_gnd_w, clearance), 0, 0])

###############################################################################
# Create coplanar ground

base_line_obj = q.modeler.create_polyline([[0, layer_2_lh, 0], [co_gnd_w, layer_2_lh, 0]], name="co_gnd_left")
top_line_obj = q.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
q.modeler.move([top_line_obj], [delta_w_half, 0, 0])
q.modeler.connect([base_line_obj, top_line_obj])

base_line_obj = q.modeler.create_polyline([[0, layer_2_lh, 0], [co_gnd_w, layer_2_lh, 0]], name="co_gnd_right")
top_line_obj = q.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
q.modeler.move([top_line_obj], [delta_w_half, 0, 0])
q.modeler.connect([base_line_obj, top_line_obj])
q.modeler.move([base_line_obj], ["{}+{}*2+{}".format(co_gnd_w, clearance, sig_bot_w), 0, 0])

###############################################################################
# Create reference ground plane

q.modeler.create_rectangle(position=[0, layer_1_lh, 0], dimension_list=[model_w, cond_h], name="ref_gnd")

###############################################################################
# Create dielectric

q.modeler.create_rectangle(
    position=[0, layer_1_uh, 0], dimension_list=[model_w, d_h], name="Dielectric", matname="FR4_epoxy"
)

###############################################################################
# Create conformal coating

sm_obj_list = []
for obj_name in ["signal", "co_gnd_left", "co_gnd_right"]:
    obj = q.modeler.get_object_from_name(obj_name)
    e_obj_list = []
    for i in [1, 2, 3]:
        e_obj = q.modeler.create_object_from_edge(obj.edges[i])
        e_obj_list.append(e_obj)
    e_obj_1 = e_obj_list[0]
    q.modeler.unite(e_obj_list)
    new_obj = q.modeler.sweep_along_vector(e_obj_1.id, [0, sm_h, 0])
    sm_obj_list.append(new_obj)

new_obj = q.modeler.create_rectangle(position=[co_gnd_w, layer_2_lh, 0], dimension_list=[clearance, sm_h])
sm_obj_list.append(new_obj)

new_obj = q.modeler.create_rectangle(position=[co_gnd_w, layer_2_lh, 0], dimension_list=[clearance, sm_h])
q.modeler.move([new_obj], [sig_bot_w + "+" + clearance, 0, 0])
sm_obj_list.append(new_obj)

sm_obj = sm_obj_list[0]
q.modeler.unite(sm_obj_list)
sm_obj.material_name = "SolderMask"
sm_obj.color = (0, 150, 100)
sm_obj.name = "solder_mask"

###############################################################################
# Assign conductors
# Signal

obj = q.modeler.get_object_from_name("signal")
q.assign_single_conductor(
    name=obj.name, target_objects=[obj], conductor_type="SignalLine", solve_option="SolveOnBoundary", unit="mm"
)

###############################################################################
# Reference ground

obj = [q.modeler.get_object_from_name(i) for i in ["co_gnd_left", "co_gnd_right", "ref_gnd"]]
q.assign_single_conductor(
    name="gnd", target_objects=obj, conductor_type="ReferenceGround", solve_option="SolveOnBoundary", unit="mm"
)

###############################################################################
# Assign Huray model on signal
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

obj = q.modeler.get_object_from_name("signal")
q.assign_huray_finitecond_to_edges(obj.edges, radius="0.5um", ratio=3, name="b_" + obj.name)

###############################################################################
# Create setup and analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~
setup = q.create_setup(setupname="new_setup")

sweep = setup.add_sweep(sweepname="sweep1", sweeptype="Discrete")
sweep.props["RangeType"] = "LinearStep"
sweep.props["RangeStart"] = "1GHz"
sweep.props["RangeStep"] = "100MHz"
sweep.props["RangeEnd"] = "5GHz"
sweep.props["SaveFields"] = False
sweep.props["SaveRadFields"] = False
sweep.props["Type"] = "Interpolating"

sweep.update()

q.analyze_nominal()

a = q.post.get_solution_data(expressions="Z0(signal,signal)", context="Original")
a.plot()

###############################################################################
# Save the project and exit

home = os.path.expanduser("~")
q.save_project(os.path.join(home, "Downloads", "pyaedt_example", q.project_name + ".aedt"))
q.close_desktop()
