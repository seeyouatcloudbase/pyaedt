"""
Q3d: Busbar Analysis
--------------------
This example shows how you can use PyAEDT to create a busbar design in
in Q3D and run a simulation.
"""
# sphinx_gallery_thumbnail_path = 'Resources/busbar.png'

import os

from pyaedt import Q3d

###############################################################################
# Launch AEDT in Non-Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# You can change the Boolean parameter ``NonGraphical`` to ``False`` to launch
# AEDT in graphical mode.

NonGraphical = False

###############################################################################
# Launch AEDT and Q3D
# ~~~~~~~~~~~~~~~~~~~
# This example launches AEDT 2022R1 in graphical mode.

# This example use SI units.


q = Q3d(specified_version="2022.1", non_graphical=NonGraphical, new_desktop_session=True)

###############################################################################
# Create Primitives
# ~~~~~~~~~~~~~~~~~
# Create polylines for three busbars and a box for the substrate.

b1 = q.modeler.create_polyline(
    [[0, 0, 0], [-100, 0, 0]],
    name="Bar1",
    matname="copper",
    xsection_type="Rectangle",
    xsection_width="5mm",
    xsection_height="1mm",
)
q.modeler["Bar1"].color = (255, 0, 0)

q.modeler.create_polyline(
    [[0, -15, 0], [-150, -15, 0]],
    name="Bar2",
    matname="aluminum",
    xsection_type="Rectangle",
    xsection_width="5mm",
    xsection_height="1mm",
)
q.modeler["Bar2"].color = (0, 255, 0)

q.modeler.create_polyline(
    [[0, -30, 0], [-175, -30, 0], [-175, -10, 0]],
    name="Bar3",
    matname="copper",
    xsection_type="Rectangle",
    xsection_width="5mm",
    xsection_height="1mm",
)
q.modeler["Bar3"].color = (0, 0, 255)

q.modeler.create_box([50, 30, -0.5], [-250, -100, -3], name="substrate", matname="FR4_epoxy")
q.modeler["substrate"].color = (128, 128, 128)
q.modeler["substrate"].transparency = 0.8

q.plot(show=False, export_path=os.path.join(q.working_directory, "Q3D.jpg"), plot_air_objects=False)

###############################################################################
# Set Up Boundaries
# ~~~~~~~~~~~~~~~~~
# Identify nets and assign sources and sinks to all nets.
# There is a source and sink for each busbar.

q.auto_identify_nets()

q.assign_source_to_objectface("Bar1", axisdir=q.AxisDir.XPos, source_name="Source1")
q.assign_sink_to_objectface("Bar1", axisdir=q.AxisDir.XNeg, sink_name="Sink1")

q.assign_source_to_objectface("Bar2", axisdir=q.AxisDir.XPos, source_name="Source2")
q.assign_sink_to_objectface("Bar2", axisdir=q.AxisDir.XNeg, sink_name="Sink2")
q.assign_source_to_objectface("Bar3", axisdir=q.AxisDir.XPos, source_name="Source3")
bar3_sink = q.assign_sink_to_objectface("Bar3", axisdir=q.AxisDir.YPos)
bar3_sink.name = "Sink3"

###############################################################################
# Print Infos
# ~~~~~~~~~~~
# There are different methods to print nets and terminal informations.
print(q.nets)
print(q.net_sinks("Bar1"))
print(q.net_sinks("Bar2"))
print(q.net_sinks("Bar3"))
print(q.net_sources("Bar1"))
print(q.net_sources("Bar2"))
print(q.net_sources("Bar3"))

###############################################################################
# Add a Q3D Setup
# ~~~~~~~~~~~~~~~
# This command adds a setup to the project and defines the adaptive frequency
# value.

setup1 = q.create_setup(props={"AdaptiveFreq": "100MHz"})
sw1 = setup1.add_sweep()
sw1.props["RangeStart"] = "1MHz"
sw1.props["RangeEnd"] = "100MHz"
sw1.props["RangeStep"] = "5MHz"
sw1.update()

###############################################################################
# Get Curves for plot
# ~~~~~~~~~~~~~~~~~~~
# This command simplify the way you can get curves to be plotted.

data_plot_self = q.matrices[0].get_sources_for_plot(get_self_terms=True, get_mutual_terms=False)
data_plot_mutual = q.get_traces_for_plot(get_self_terms=False, get_mutual_terms=True, category="C")
data_plot_self
data_plot_mutual

###############################################################################
# Create a Rectangular Plot
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# This command creates a rectangular plot and a Data Table.
q.post.create_report(expressions=data_plot_self)

q.post.create_report(expressions=data_plot_mutual, context="Original", plot_type="Data Table")

###############################################################################
# Solve the Setup
# ~~~~~~~~~~~~~~~
# This command solves the setup.

q.analyze_nominal()

###############################################################################
# Get Report Data
# ~~~~~~~~~~~~~~~
# This command get the report data into a Data Structure that allows to manipulate them.

a = q.post.get_solution_data(expressions=data_plot_self, context="Original")
a.sweeps["Freq"]
a.data_magnitude()
a.plot()

###############################################################################
# Close AEDT
# ~~~~~~~~~~
# After the simulaton is completed, you can close AEDT or release it using the
# `release_desktop` method.
# All methods provide for saving projects before exiting.
if os.name != "posix":
    q.release_desktop(close_projects=True, close_desktop=True)
