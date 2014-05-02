##
# @file plotter.py
# @package openmoc.plotter
# @brief The plotter module provides utility functions to plot data from
#        OpenMOCs C++ classes, in particular, the geomery, including Material,
#        Cells and flat source regions, and fluxes and pin powers.
# @author William Boyd (wboyd@mit.edu)
# @date March 10, 2013

import sys

## @var openmoc
#  @brief The openmoc module in use in the Python script using the
#         openmoc.plotter module.
openmoc = ''

# Determine which OpenMOC module is being used
if 'openmoc.gnu.double' in sys.modules:
  openmoc = sys.modules['openmoc.gnu.double']
elif 'openmoc.gnu.single' in sys.modules:
  openmoc = sys.modules['openmoc.gnu.single']
elif 'openmoc.intel.double' in sys.modules:
  openmoc = sys.modules['openmoc.intel.double']
elif 'openmoc.intel.single' in sys.modules:
  openmoc = sys.modules['openmoc.intel.single']
elif 'openmoc.bgq.double' in sys.modules:
  openmoc = sys.modules['openmoc.bgq.double']
elif 'openmoc.bgq.single' in sys.modules:
  openmoc = sys.modules['openmoc.bgq.single']
else:
  from openmoc import *


import matplotlib

# force headless backend, or set 'backend' to 'Agg'
# in your ~/.matplotlib/matplotlibrc
matplotlib.use('Agg')

import matplotlib.pyplot as plt

# Force non-interactive mode, or set 'interactive' to False
# in your ~/.matplotlib/matplotlibrc
plt.ioff()

import matplotlib.colors as colors
import matplotlib.cm as cmx
import numpy as np
import numpy.random
import os, sys

# For Python 2.X.X
if (sys.version_info[0] == 2):
  from log import *
# For Python 3.X.X
else:
  from openmoc.log import *


## A static variable for the output directory in which to save plots
subdirectory = "/plots/"

## The number of colors to use when creating a random color map for plots
num_colors = 50

## An array of random floats that represents a random color map for plots
color_map = np.random.random_sample((num_colors,))


##
# @brief Plots the characteristic tracks from an OpenMOC simulation.
# @details This method requires that Tracks have been generated by a
#          TrackGenerator object. A user may invoke this function from
#          an OpenMOC Python file as follows:
#
# @code
#         openmoc.plotter.plot_tracks(track_generator)
# @endcode
#
# @param track_generator the TrackGenerator which has generated Tracks
def plot_tracks(track_generator):

  global subdirectory

  directory = get_output_directory() + subdirectory

  # Make directory if it does not exist
  if not os.path.exists(directory):
    os.makedirs(directory)

  # Error checking
  if not 'TrackGenerator' in str(type(track_generator)):
    py_printf('ERROR', 'Unable to plot Tracks since %s was input rather ' + \
              'than a TrackGenerator', str(type(track_generator)))

  if not track_generator.containsTracks():
    py_printf('ERROR', 'Unable to plot Tracks since the track ' + \
              'generator has not yet generated tracks')

  py_printf('NORMAL', 'Plotting the tracks...')

  # Retrieve data from TrackGenerator
  num_azim = track_generator.getNumAzim()
  spacing = track_generator.getTrackSpacing()
  num_tracks = track_generator.getNumTracks()
  coords = track_generator.retrieveTrackCoords(num_tracks*4)

  # Convert data to NumPy arrays
  coords = np.array(coords)
  x = coords[0::2]
  y = coords[1::2]

  # Make figure of line segments for each Track
  fig = plt.figure()
  for i in range(num_tracks):
    plt.plot([x[i*2], x[i*2+1]], [y[i*2], y[i*2+1]], 'b-')

  plt.xlim([x.min(), x.max()])
  plt.ylim([y.min(), y.max()])

  title = 'Tracks for ' + str(num_azim) + ' angles and ' + str(spacing) + \
            ' cm spacing'

  plt.title(title)

  filename = directory + 'tracks-' + str(num_azim) + '-angles-' + \
      str(spacing) + '-spacing.png'

  fig.savefig(filename, bbox_inches='tight')


##
# @brief Plots the characteristic Track segments from an OpenMOC simulation.
# @details This method requires that tracks have been generated by a
#          TrackGenerator object. Each segment is colored by the ID of the
#          unique flat flat source region it is within. A user may invoke
#          this function from an OpenMOC Python file as follows:
#
# @code
#         openmoc.plotter.plot_segments(track_generator)
# @endcode
#
# @param track_generator the TrackGenerator which has generated Tracks
def plot_segments(track_generator):

  global subdirectory

  directory = get_output_directory() + subdirectory

  # Make directory if it does not exist
  if not os.path.exists(directory):
    os.makedirs(directory)

  # Error checking
  if not 'TrackGenerator' in str(type(track_generator)):
    py_printf('ERROR', 'Unable to plot Track segments since  %s was input ' + \
              'rather than a TrackGenerator', str(type(track_generator)))

  if not track_generator.containsTracks():
    py_printf('ERROR', 'Unable to plot Track segments since the ' + \
              'TrackGenerator has not yet generated Tracks.')

  py_printf('NORMAL', 'Plotting the track segments...')

  # Retrieve data from TrackGenerator
  num_azim = track_generator.getNumAzim()
  spacing = track_generator.getTrackSpacing()
  num_segments = track_generator.getNumSegments()
  num_fsrs = track_generator.getGeometry().getNumFSRs()
  coords = track_generator.retrieveSegmentCoords(num_segments*5)

  # Convert data to NumPy arrays
  coords = np.array(coords)
  x = numpy.zeros(num_segments*2)
  y = numpy.zeros(num_segments*2)
  fsrs = numpy.zeros(num_segments)

  for i in range(num_segments):
    fsrs[i] = coords[i*5]
    x[i*2] = coords[i*5+1]
    y[i*2] = coords[i*5+2]
    x[i*2+1] = coords[i*5+3]
    y[i*2+1] = coords[i*5+4]

  # Make figure of line segments for each track
  fig = plt.figure()

  for i in range(num_segments):

    # Create a color map corresponding to FSR IDs
    jet = cm = plt.get_cmap('jet')
    cNorm  = colors.Normalize(vmin=0, vmax=max(color_map))
    scalarMap = cmx.ScalarMappable(norm=cNorm)
    color = scalarMap.to_rgba(color_map[fsrs[i] % num_colors])
    plt.plot([x[i*2], x[i*2+1]], [y[i*2], y[i*2+1]], c=color)

  plt.xlim([x.min(), x.max()])
  plt.ylim([y.min(), y.max()])

  title = 'Segments for ' + str(num_azim) + ' angles and ' + str(spacing) + \
        ' cm spacing'

  plt.title(title)

  filename = directory + 'segments-' + str(num_azim) + '-angles-' + \
      str(spacing) + '-spacing.png'

  fig.savefig(filename, bbox_inches='tight')



##
# @brief This method takes in a Geometry object and plots a color-coded 2D
#        surface plot representing the Materials in the Geometry.
# @details The Geometry object must be initialized with Materials, Cells,
#          Universes and lattices before being passed into this method. A user
#          may invoke this function from an OpenMOC Python file as follows:
#
# @code
#         openmoc.plotter.plot_materials(geometry)
# @endcode
#
# @param geometry a geometry object which has been initialized with Materials,
#        Cells, Universes and Lattices
# @param gridsize an optional number of grid cells for the plot
def plot_materials(geometry, gridsize=250):

  global subdirectory

  directory = get_output_directory() + subdirectory

  # Make directory if it does not exist
  if not os.path.exists(directory):
    os.makedirs(directory)

  # Error checking
  if not 'Geometry' in str(type(geometry)):
    py_printf('ERROR', 'Unable to plot the Materials since ' + \
                    'input was not a geometry class object')

  if not isinstance(gridsize, int):
    py_printf('ERROR', 'Unable to plot the Materials since ' + \
              'since the gridsize %s is not an integer', str(gridsize))

  if gridsize <= 0:
    py_printf('Error', 'Unable to plot the Materials ' + \
              'with a negative gridsize (%d)', gridsize)

  py_printf('NORMAL', 'Plotting the materials...')

  # Initialize a NumPy array for the surface colors
  surface = numpy.zeros((gridsize, gridsize))

  # Retrieve the bounding box for the Geometry
  xmin = geometry.getXMin()
  xmax = geometry.getXMax()
  ymin = geometry.getYMin()
  ymax = geometry.getYMax()

  # Initialize NumPy arrays for the grid points
  xcoords = np.linspace(xmin, xmax, gridsize)
  ycoords = np.linspace(ymin, ymax, gridsize)

  # Find the <aterial IDs for each grid point
  for i in range(gridsize):
    for j in range(gridsize):

      x = xcoords[i]
      y = ycoords[j]

      point = LocalCoords(x, y)
      point.setUniverse(0)
      geometry.findCellContainingCoords(point)
      fsr_id = geometry.findFSRId(point)
      material_id = geometry.findCellContainingFSR(fsr_id).getMaterial()
      surface[j][i] = color_map[material_id % num_colors]

  # Flip the surface vertically to align NumPy row/column indices with the
  # orientation expected by the user
  surface = np.flipud(surface)

  # Plot a 2D color map of the Materials
  fig = plt.figure()
  plt.imshow(surface, extent=[xmin, xmax, ymin, ymax])
  plt.title('Materials')
  filename = directory + 'materials.png'
  fig.savefig(filename, bbox_inches='tight')


##
# @brief This method takes in a Geometry object and plots a color-coded 2D
#        surface plot representing the Cells in the Geometry.
# @details The geometry object must be initialized with Materials, Cells,
#          Universes and Lattices before being passed into this method. A user
#          may invoke this function from an OpenMOC Python file as follows:
#
# @code
#         openmoc.plotter.plot_cells(geometry)
# @endcode
#
# @param geometry a Geometry object which has been initialized with Materials,
#        Cells, Universes and Lattices
# @param gridsize an optional number of grid cells for the plot
def plot_cells(geometry, gridsize=250):

  global subdirectory

  directory = get_output_directory() + subdirectory

  # Make directory if it does not exist
  if not os.path.exists(directory):
    os.makedirs(directory)

  # Error checking
  if not 'Geometry' in str(type(geometry)):
    py_printf('ERROR', 'Unable to plot the Cells since ' + \
              'input was not a Geometry class object')

  if not isinstance(gridsize, int):
    py_printf('ERROR', 'Unable to plot the Cells since ' + \
                'since the gridsize %s is not an integer', str(gridsize))

  if gridsize <= 0:
    py_printf('Error', 'Unable to plot the Cells ' + \
              'with a negative gridsize (%d)', gridsize)

  py_printf('NORMAL', 'Plotting the cells...')

  # Initialize a NumPy array for the surface colors
  surface = np.zeros((gridsize, gridsize))

  # Retrieve the bounding box for the Geometry
  xmin = geometry.getXMin()
  xmax = geometry.getXMax()
  ymin = geometry.getYMin()
  ymax = geometry.getYMax()

  # Initialize numpy arrays for the grid points
  xcoords = np.linspace(xmin, xmax, gridsize)
  ycoords = np.linspace(ymin, ymax, gridsize)

  # Find the Cell IDs for each grid point
  for i in range(gridsize):
    for j in range(gridsize):

      x = xcoords[i]
      y = ycoords[j]

      point = LocalCoords(x, y)
      point.setUniverse(0)
      geometry.findCellContainingCoords(point)
      fsr_id = geometry.findFSRId(point)
      cell_id = geometry.findCellContainingFSR(fsr_id).getId()
      surface[j][i] = color_map[cell_id % num_colors]

  # Flip the surface vertically to align NumPy row/column indices with the
  # orientation expected by the user
  surface = np.flipud(surface)

  # Plot a 2D color map of the Cells
  fig = plt.figure()
  plt.imshow(surface, extent=[xmin, xmax, ymin, ymax])
  plt.title('Cells')
  filename = directory + 'cells.png'
  fig.savefig(filename, bbox_inches='tight')



##
# @brief This method takes in a Geometry object and plots a color-coded 2D
#        surface plot representing the flat source regions in the Geometry.
# @details The Geometry object must be initialized with Materials, Cells,
#          Universes and Lattices before being passed into this method. A user
#          may invoke this function from an OpenMOC Python file as follows:
#
# @code
#         openmoc.plotter.plot_flat_source_regions(geometry)
# @endcode
#
# @param geometry a geometry object which has been initialized with Materials,
#        Cells, Universes and Lattices
# @param gridsize an optional number of grid cells for the plot
def plot_flat_source_regions(geometry, gridsize=250):

  global subdirectory

  directory = get_output_directory() + subdirectory

  # Make directory if it does not exist
  if not os.path.exists(directory):
    os.makedirs(directory)

  # Error checking
  if not 'Geometry' in str(type(geometry)):
    py_printf('ERROR', 'Unable to plot the flat source regions since ' + \
              'input was not a geometry class object')

  if not isinstance(gridsize, int):
    py_printf('ERROR', 'Unable to plot the flat source regions since ' + \
              'since the gridsize %s is not an integer', str(gridsize))

  if gridsize <= 0:
    py_printf('Error', 'Unable to plot the flat source regions ' + \
              'with a negative gridsize (%d)', gridsize)

  py_printf('NORMAL', 'Plotting the flat source regions...')

  # Initialize a NumPy array for the surface colors
  surface = numpy.zeros((gridsize, gridsize))

  # Retrieve the bounding box for the Geometry
  xmin = geometry.getXMin()
  xmax = geometry.getXMax()
  ymin = geometry.getYMin()
  ymax = geometry.getYMax()

  # Initialize numpy arrays for the grid points
  xcoords = np.linspace(xmin, xmax, gridsize)
  ycoords = np.linspace(ymin, ymax, gridsize)

  # Find the flat source region IDs for each grid point
  for i in range(gridsize):
    for j in range(gridsize):

      x = xcoords[i]
      y = ycoords[j]

      point = LocalCoords(x, y)
      point.setUniverse(0)
      geometry.findCellContainingCoords(point)
      fsr_id = geometry.findFSRId(point)
      surface[j][i] = color_map[fsr_id % num_colors]

  # Flip the surface vertically to align NumPy row/column indices with the
  # orientation expected by the user
  surface = np.flipud(surface)

  # Plot a 2D color map of the flat source regions
  fig = plt.figure()
  plt.imshow(surface, extent=[xmin, xmax, ymin, ymax])
  plt.title('Flat Source Regions')
  filename = directory + 'flat-source-regions.png'
  fig.savefig(filename, bbox_inches='tight')


##
# @brief This method takes in a Geometry object and plots a color-coded 2D
#        surface plot representing the flat source regions in the Geometry.
# @details The geometry object must be initialized with Materials, Cells,
#          Universes and Lattices before being passed into this method. A user
#          may invoke this function from an OpenMOC Python file as follows:
#
# @code
#         openmoc.plotter.plot_fluxes(geometry, solver, energy_groups=[1,7])
# @endcode
#
# @param geometry a Geometry object which has been initialized with Materials,
#        Cells, Universes and Lattices
# @param solver a Solver object that has converged the source for the Geometry
# @param energy_groups a Python list of integer energy groups to plot
# @param gridsize an optional number of grid cells for the plot
def plot_fluxes(geometry, solver, energy_groups=[0], gridsize=250):

  global subdirectory

  directory = get_output_directory() + subdirectory

  # Make directory if it does not exist
  if not os.path.exists(directory):
    os.makedirs(directory)

  # Error checking
  if not 'Geometry' in str(type(geometry)):
    py_printf('ERROR', 'Unable to plot the flat source region scalar ' + \
              'flux since input did not contain a geometry class object')

  if not 'Solver' in str(type(solver)):
    py_printf('ERROR', 'Unable to plot the flat source region scalar ' + \
              'flux since input did not contain a solver class object')

  if isinstance(energy_groups, list):
    for group in energy_groups:
      if not isinstance(group, int):
        py_print('ERROR', 'Unable to plot the flat source region ' + \
                 'scalar flux since the energy_groups list ' + \
                 'contains %s which is not an int', str(group))

      elif group <= 0:
        py_print('ERROR', 'Unable to plot the flat source region scalar ' + \
                 'flux since the energy_groups list contains %d which is' + \
                 'less than the index for all energy groups', str(group))

      elif group > geometry.getNumEnergyGroups():
        py_printf('ERROR', 'Unable to plot the flat source region scalar ' + \
                  'flux since the energy_groups list contains %d which is' + \
                  ' greater than the index for all energy groups', str(group))

  elif isinstance(energy_groups, int):
    if energy_groups <= 0:
      py_print('ERROR', 'Unable to plot the flat source region scalar ' + \
               'flux since the energy_groups argument contains %d which is' + \
               ' less than the index for all energy groups', str(energy_groups))

    elif energy_groups > geometry.getNumEnergyGroups():
      py_printf('ERROR', 'Unable to plot the flat source region ' + \
                'scalar flux since the energy_groups argument ' + \
                'contains %d which is greater than the index ' + \
                'for all energy groups', str(energy_groups))

    else:
      py_printf('ERROR', 'Unable to plot the flat source region ' + \
                'scalar flux since the energy_groups argument ' + \
                'is %s which is not an energy group index or a list ' + \
                'of energy group indices', str(energy_groups))

  if not isinstance(gridsize, int):
    py_printf('ERROR', 'Unable to plot the flat source region scalar flux ' + \
              'since since the gridsize %s is not an integer', str(gridsize))

  if not isinstance(energy_groups, (int, list)):
    py_printf('ERROR', 'Unable to plot the flat source region scalar ' + \
              'flux since the energy_groups is not an int or a list')

  if gridsize <= 0:
    py_printf('Error', 'Unable to plot the flat source regions ' + \
              'with a negative gridsize (%d)', gridsize)

  py_printf('NORMAL', 'Plotting the flat source region scalar fluxes...')

  if not isinstance(energy_groups, list):
    energy_groups = [energy_groups]


  # Initialize a numpy array for the groupwise scalar fluxes
  fluxes = numpy.zeros((len(energy_groups), gridsize, gridsize))

  # Retrieve the bounding box for the geometry
  xmin = geometry.getXMin()
  xmax = geometry.getXMax()
  ymin = geometry.getYMin()
  ymax = geometry.getYMax()

  # Initialize numpy arrays for the grid points
  xcoords = np.linspace(xmin, xmax, gridsize)
  ycoords = np.linspace(ymin, ymax, gridsize)

  for i in range(gridsize):
    for j in range(gridsize):

      # Find the flat source region IDs for each grid point
      x = xcoords[i]
      y = ycoords[j]

      point = LocalCoords(x, y)
      point.setUniverse(0)
      geometry.findCellContainingCoords(point)
      fsr_id = geometry.findFSRId(point)

      # Get the scalar flux for each energy group in this FSR
      for index, group in enumerate(energy_groups):
        fluxes[index,j,i] = solver.getFSRScalarFlux(fsr_id, group)

  # Loop over all energy group and create a plot
  for index, group in enumerate(energy_groups):

    # Plot a 2D color map of the flat source regions
    fig = plt.figure()
    plt.imshow(np.flipud(fluxes[index,:,:]), extent=[xmin, xmax, ymin, ymax])
    plt.colorbar()
    plt.title('Flat Source Region Scalar Flux in Group ' + str(group))
    filename = directory + 'fsr-flux-group-' + str(group) + '.png'
    fig.savefig(filename, bbox_inches='tight')


##
# @brief This method takes in a Mesh object for CMFD acceleration and plots a
#        color-coded 2D surface plot representing the mesh cell flux.A user
#        may invoke this function from an OpenMOC Python file as follows:
#
# @code
#         openmoc.plotter.plotMeshFluxes(mesh)
# @endcode
#
# @param mesh Mesh object which has been initialized for CMFD.
# @param energy_groups a Python list of the integer energy groups to plot
# @param gridsize an optional number of grid cells for the plot
def plot_mesh_fluxes(mesh, energy_groups=[1], gridsize=500):

  global subdirectory

  directory = get_output_directory() + subdirectory

  # Make directory if it does not exist
  if not os.path.exists(directory):
    os.makedirs(directory)

  # Error checking
  if not 'Mesh' in str(type(mesh)):
    py_printf('ERROR', 'Unable to plot the mesh scalar flux ' + \
                'since input did not contain a mesh class object')

  if isinstance(energy_groups, list):
    for group in energy_groups:

      if not isinstance(group, int):
        py_printf('ERROR', 'Unable to plot the mesh scalar flux since the ' + \
                  'energy_groups list contains %s which is not an int',
                  str(group))

      elif group <= 0:
        py_printf('ERROR', 'Unable to plot the mesh scalar flux since the ' + \
                  'energy_groups list contains %d which is less than the ' + \
                  'index for all energy groups', str(group))

      elif group > mesh.getNumGroups():
        py_printf('ERROR', 'Unable to plot the mesh scalar flux since the ' + \
                  'energy_groups list contains %d which is greater than ' + \
                  'the index for all energy groups', str(group))

  elif isinstance(energy_groups, int):
    if energy_groups <= 0:
      py_printf('ERROR', 'Unable to plot the mesh scalar flux since the ' + \
                'energy_groups argument contains %d which is less than the ' + \
                'index for all energy groups', str(energy_groups))

    elif energy_groups > mesh.getNumGroups():
      py_printf('ERROR', 'Unable to plot the mesh scalar flux since the ' + \
                'energy_groups argument contains %d which is greater than ' + \
                'the index for all energy groups', str(energy_groups))

  else:
    py_printf('ERROR', 'Unable to plot the mesh scalar flux since the ' + \
              'energy_groups argument is %s which is not an energy group ' + \
              'index or a list of energy group indices', str(energy_groups))

  if not isinstance(gridsize, int):
    py_printf('ERROR', 'Unable to plot the mesh scalar flux since the ' + \
                'gridsize %s is not an integer', str(gridsize))

  if not isinstance(energy_groups, (int, list)):
    py_printf('ERROR', 'Unable to plot the mesh scalar ' + \
                'flux since the energy_groups is not an int or a list')

  if gridsize <= 0:
    py_printf('Error', 'Unable to plot the mesh ' + \
                'with a negative gridsize (%d)', gridsize)

  py_printf('NORMAL', 'Plotting the mesh scalar fluxes...')

  if not isinstance(energy_groups, list):
    energy_groups = [energy_groups]


  # Initialize a numpy array for the groupwise scalar fluxes
  fluxes = numpy.zeros((len(energy_groups), gridsize, gridsize))

  # Retrieve the bounding box for the geometry
  xmin = -mesh.getLengthX()/2.0
  xmax = mesh.getLengthX()/2.0
  ymin = -mesh.getLengthY()/2.0
  ymax = mesh.getLengthY()/2.0

  # Initialize numpy arrays for the grid points
  xcoords = np.linspace(xmin, xmax, gridsize)
  ycoords = np.linspace(ymin, ymax, gridsize)

  for i in range(gridsize):
    for j in range(gridsize):

      # Find the flat source region IDs for each grid point
      x = xcoords[i]
      y = ycoords[j]

      point = LocalCoords(x, y)
      point.setUniverse(0)
      cell_id = mesh.findCellId(point)

      # Get the scalar flux for each energy group in this FSR
      for index, group in enumerate(energy_groups):
        fluxes[index,j,i] = mesh.getFlux(cell_id, group-1)

  # Loop over all energy group and create a plot
  for index, group in enumerate(energy_groups):

    # Plot a 2D color map of the flat source regions
    fig = plt.figure()
    plt.imshow(np.flipud(fluxes[index,:,:]), extent=[xmin, xmax, ymin, ymax])
    plt.colorbar()
    plt.title('Mesh Scalar Flux in Group ' + str(group))
    filename = directory + 'mesh-flux-group-' + str(group) + '.png'
    fig.savefig(filename, bbox_inches='tight')

