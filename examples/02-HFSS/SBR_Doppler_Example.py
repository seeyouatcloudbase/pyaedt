"""
Sbr+: Doppler Setup
-------------------
This example shows how you can use PyAEDT to create a Multipart Scenario in SBR+ and setup a doppler Analysis.
"""

###############################################################################
# Launch AEDT in Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This examples launches AEDT 2022R1 in graphical mode.
import os
import tempfile
import pyaedt
from pyaedt import examples, generate_unique_name

# Start Electronics Desktop
aedt_version = "2022.1"
projectname = "MicroDoppler_with_ADP"
designname = "doppler"
library_path = examples.download_multiparts()

###############################################################################
# Open Project
# ~~~~~~~~~~~~
# Download Project, opens it and save to TEMP Folder.

tmpfold = tempfile.gettempdir()


temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

# Instantiate the application.
app = pyaedt.Hfss(
    specified_version=aedt_version,
    solution_type="SBR+",
    new_desktop_session=True,
    projectname=projectname,
    close_on_exit=True,
)


app.autosave_disable()

###############################################################################
# Create Design
# ~~~~~~~~~~~~~
# Save project and rename design

app.save_project(project_file=os.path.join(temp_folder, projectname + ".aedt"))
app.rename_design(designname)


###############################################################################
# Libraries
# ~~~~~~~~~~~~~~~
# Setup Library Path to 3d Components

actor_lib = os.path.join(library_path, "actor_library")
env_lib = os.path.join(library_path, "environment_library")
radar_lib = os.path.join(library_path, "radar_modules")
env_folder = os.path.join(env_lib, "road1")
person_folder = os.path.join(actor_lib, "person3")
car_folder = os.path.join(actor_lib, "vehicle1")
bike_folder = os.path.join(actor_lib, "bike1")
bird_folder = os.path.join(actor_lib, "bird1")

###############################################################################
# Environment
# ~~~~~~~~~~~~~~
# Define background environment

road1 = app.modeler.add_environment(env_folder=env_folder, environment_name="Bari")
prim = app.modeler

###############################################################################
# Actors
# ~~~~~~~~~~~~~~~~~~~~~
# Put Actors in environment. This example has persons, birds, bikes and cars.

person1 = app.modeler.add_person(
    actor_folder=person_folder, speed=1.0, global_offset=[25, 1.5, 0], yaw=180, actor_name="Massimo"
)
person2 = app.modeler.add_person(
    actor_folder=person_folder, speed=1.0, global_offset=[25, 2.5, 0], yaw=180, actor_name="Devin"
)
car1 = app.modeler.add_vehicle(actor_folder=car_folder, speed=8.7, global_offset=[3, -2.5, 0], actor_name="LuxuryCar")
bike1 = app.modeler.add_vehicle(
    actor_folder=bike_folder, speed=2.1, global_offset=[24, 3.6, 0], yaw=180, actor_name="Alberto_in_bike"
)
bird1 = app.modeler.add_bird(
    actor_folder=bird_folder,
    speed=1.0,
    global_offset=[19, 4, 3],
    yaw=120,
    pitch=-5,
    flapping_rate=30,
    actor_name="Pigeon",
)
bird2 = app.modeler.add_bird(
    actor_folder=bird_folder, speed=1.0, global_offset=[6, 2, 3], yaw=-60, pitch=10, actor_name="Eagle"
)

###############################################################################
# Radar
# ~~~~~~~~~~~~~~~~~~~~~
# Put radar on car. The radar will be created relative to the car coordinate system.

radar1 = app.create_sbr_radar_from_json(
    radar_file=radar_lib,
    radar_name="Example_1Tx_1Rx",
    offset=[2.57, 0, 0.54],
    use_relative_cs=True,
    relative_cs_name=car1.cs_name,
)

###############################################################################
# Setup and validation
# ~~~~~~~~~~~~~~~~~~~~~
# Create setup and validate it. This command will create a setup and a parametric sweep on the time variable of the
# duration of 2 seconds. the step is computed automatically from CPI.

setup, sweep = app.create_sbr_pulse_doppler_setup(sweep_time_duration=2)
app.set_sbr_current_sources_options()
app.validate_simple()

###############################################################################
# Plot the model
# ~~~~~~~~~~~~~~

app.plot(show=False, export_path=os.path.join(app.working_directory, "Image.jpg"), plot_air_objects=True)

###############################################################################
# Solve and release desktop
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Solves problem and close it. Uncomment the next command to activate the simulation

# app.analyze_setup(sweep.name)
app.save_project()
app.release_desktop(close_projects=True, close_desktop=True)
