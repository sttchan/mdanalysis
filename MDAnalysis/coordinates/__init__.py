# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
# MDAnalysis --- http://mdanalysis.googlecode.com
# Copyright (c) 2006-2011 Naveen Michaud-Agrawal,
#               Elizabeth J. Denning, Oliver Beckstein,
#               and contributors (see website for details)
# Released under the GNU Public Licence, v2 or any higher version
#
# Please cite your use of MDAnalysis in published work:
#
#     N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and
#     O. Beckstein. MDAnalysis: A Toolkit for the Analysis of
#     Molecular Dynamics Simulations. J. Comput. Chem. 32 (2011), 2319--2327,
#     doi:10.1002/jcc.21787
#

"""
Coordinate/Trajectory Readers and Writers  --- :mod:`MDAnalysis.coordinates`
============================================================================

The coordinates submodule contains code to read coordinates, either
single frames (e.g. the PDB module) or trajectories (such as the DCD
reader). All readers are supposed to expose a :class:`Reader` object
that presents a common `Trajectory API`_ to other code.

The :class:`~MDAnalysis.core.AtomGroup.Universe` contains the API
entry point attribute

  :attr:`Universe.trajectory`

that points to the actual :class:`~MDAnalysis.coordinates.base.Reader`
object; all Readers are supposed to be accessible through this entry
point in the same manner ("`duck typing`_").

In order to **write coordinates**, a factory function is provided
(:func:`MDAnalysis.coordinates.core.writer`) which is made available
as :func:`MDAnalysis.Writer`) that returns a *Writer* appropriate for
the desired file format (as indicated by the filename
suffix). Furthermore, a trajectory
:class:`~MDAnalysis.coordinates.base.Reader` can also have a method
:meth:`~MDAnalysis.coordinates.base.Reader.Writer` that returns an
appropriate :class:`~MDAnalysis.coordinates.base.Writer` for the file
format of the trajectory.

In analogy to :func:`MDAnalysis.coordinates.core.writer`, there is
also a :func:`MDAnalysis.coordinates.core.reader` function available
to return a trajectory :class:`~MDAnalysis.coordinates.base.Reader`
instance although this is often not needed because the
:class:`~MDAnalysis.core.AtomGroup.Universe` class can choose an
appropriate reader automatically.

.. _duck typing: http://c2.com/cgi/wiki?DuckTyping



Supported coordinate formats
----------------------------

The table below lists the coordinate file formats understood by MDAnalysis. The
emphasis is on formats that are used in popular molecular dynamics
codes. MDAnalysis figures out formats by looking at the extension. Thus, a DCD
file always has to end with ".dcd" to be recognized as such. (A number of files
are also recognized when they are compressed with :program:`gzip` or
:program:`bzip2` such as ".xyz.bz2".)

.. _Supported coordinate formats:

.. table:: Table of Supported coordinate formats

   +---------------+-----------+-------+------------------------------------------------------+
   |Name           | extension |  IO   | remarks                                              |
   +===============+===========+=======+======================================================+
   | CHARMM,       |  dcd      |   r/w | standard CHARMM binary trajectory; endianness is     |
   | NAMD,         |           |       | autodetected. Fixed atoms may not be handled         |
   | LAMMPS        |           |       | correctly (requires testing). Module                 |
   |               |           |       | :mod:`MDAnalysis.coordinates.DCD`                    |
   +---------------+-----------+-------+------------------------------------------------------+
   | Gromacs       | xtc       |  r/w  | Compressed (lossy) xtc trajectory format. Module     |
   |               |           |       | :mod:`MDAnalysis.coordinates.XTC`                    |
   +---------------+-----------+-------+------------------------------------------------------+
   | Gromacs       | trr       |  r/w  | Full precision trr trajectory. Only coordinates are  |
   |               |           |       | processed at the moment. Module                      |
   |               |           |       | :mod:`MDAnalysis.coordinates.TRR`                    |
   +---------------+-----------+-------+------------------------------------------------------+
   | XYZ           |  xyz      |  r    | Generic white-space separate XYZ format; can be      |
   |               |           |       | compressed. Module                                   |
   |               |           |       | :mod:`MDAnalysis.coordinates.XYZ`                    |
   +---------------+-----------+-------+------------------------------------------------------+
   | Amber         | trj,      |  r    | formatted (ASCII) trajectories; the presence of a    |
   |               | mdcrd     |       | periodic box is autodetected (*experimental*).       |
   |               |           |       | Module :mod:`MDAnalysis.coordinates.TRJ`             |
   +---------------+-----------+-------+------------------------------------------------------+
   | Brookhaven    | pdb       |  r/w  | a simplified PDB format (as used in MD simulations)  |
   | [#a]_         |           |       | is read by default; the full format can be read by   |
   |               |           |       | supplying the `permissive=False` flag to             |
   |               |           |       | :class:`MDAnalysis.Universe`. Module                 |
   |               |           |       | :mod:`MDAnalysis.coordinates.PDB`                    |
   +---------------+-----------+-------+------------------------------------------------------+
   | PDBQT [#a]_   | pdbqt     | r/w   | file format used by AutoDock with atom types *t*     |
   |               |           |       | and partial charges *q*. Module:                     |
   |               |           |       | :mod:`MDAnalysis.coordinates.PDBQT`                  |
   +---------------+-----------+-------+------------------------------------------------------+
   | PQR [#a]_     | pqr       |  r    | PDB-like but whitespace-separated files with charge  |
   |               |           |       | and radius information. Module                       |
   |               |           |       | :mod:`MDAnalysis.coordinates.PQR`                    |
   +---------------+-----------+-------+------------------------------------------------------+
   | GROMOS96      | gro       |  r/w  | basic GROMOS96 format (without velocities). Module   |
   | [#a]_         |           |       | :mod:`MDAnalysis.coordinates.GRO`                    |
   +---------------+-----------+-------+------------------------------------------------------+
   | CHARMM [#a]_  | crd       |  r/w  | "CARD" coordinate output from CHARMM; deals with     |
   |               |           |       | either standard or EXTended format. Module           |
   |               |           |       | :mod:`MDAnalysis.coordinates.CRD`                    |
   +---------------+-----------+-------+------------------------------------------------------+

.. [#a] This format can also be used to provide basic *topology*
   information (i.e. the list of atoms); it is possible to create a
   full :mod:`~MDAnalysis.core.AtomGroup.Universe` by simply
   providing a file of this format: ``u = Universe(filename)``


.. _Trajectory API:

Trajectory API
--------------

The **Trajectory API** defines how classes have to be structured that allow
reading and writing of coordinate files. By following the API it is possible to
seamlessly enhance the I/O capabilities of MDAnalysis. The actual underlying
I/O code can be written in C or python or a mixture thereof.

Typically, each format resides in its own module, named by the format specifier
(and using upper case by convention).

Reader and Writer classes are derived from base classes in
:mod:`MDAnalysis.coordinates.base`.


History
~~~~~~~

- 2010-04-30 Draft [orbeckst]
- 2010-08-20 added single frame writers to API [orbeckst]
- 2010-10-09 added write() method to Writers [orbeckst]
- 2010-10-19 use close() instead of close_trajectory() [orbeckst]
- 2010-10-30 clarified Writer write() methods (see also `Issue 49`_)
- 2011-02-01 extended call signatur of Reader class
- 2011-03-30 optional Writer() method for Readers
- 2011-04-18 added time and frame managed attributes to Reader
- 2011-04-20 added volume to Timestep

.. _Issue 49: http://code.google.com/p/mdanalysis/issues/detail?id=49


Registry
~~~~~~~~

In various places, MDAnalysis tries to automatically select appropriate formats
(e.g. by looking at file extensions). In order to allow it to choose the
correct format, all I/O classes must be registered in one of three dictionaries
with the format (typically the file extension in upper case):

- Trajectory reader classes must be added to
  :data:`MDAnalysis.coordinates._trajectory_readers`.

- Trajectory writer classes must be added to
  :data:`MDAnalysis.coordinates._trajectory_writers`.

- Single-frame writer classes must be added to to
  :data:`MDAnalysis.coordinates._frame_writers`.


Timestep class
~~~~~~~~~~~~~~

A Timestep instance holds data for the current frame. It is updated whenever a
new frame of the trajectory is read.

Timestep classes are derived from
:class:`MDAnalysis.coordinates.base.Timestep`, which is the primary
implementation example (and used directly for the DCDReader).

Methods
.......

  ``__init__(arg)``
      depending on the type of *arg*, Timestep instances are created in
      different ways:

        ``int``
            empty Timestep for *arg* atoms (allocate arrays etc)
        :class:`Timestep`
            makes a deep copy of the *arg*
        :class:`numpy.ndarray`
            update the Timesteps positions array with the contents of *arg*

      Anything else raises an exception; in particular it is not possible to
      create a "empty" :class:`Timestep` instance.
  ``__getitem__(atoms)``
      position(s) of atoms; can be a slice or numpy array and then returns
      coordinate array
  ``__len__()``
      number of coordinates (atoms) in the frame
  ``__iter__()``
      iterator over all coordinates
  ``copy()``
      deep copy of the instance

Attributes
..........

  ``numatoms``
      number of atoms in the frame
  ``frame``
      current frame number
  ``dimensions``
      system box dimensions (`x, y, z, alpha, beta, gamma`)
      (typically implemented as a property because it needs to translate whatever is in the
      underlying :attr:`Timestep._unitcell` attribute)
  ``volume``
      system box volume (derived as the determinant of the box vectors of ``dimensions``)

Private attributes
..................

These attributes are set directly by the underlying trajectory
readers. Normally the user should not have to directly access those (although in
some cases it is convenient to directly use :attr:`Timestep._pos`).

  ``_pos``
      raw coordinates, a :class:`numpy.float32` array; ``X = _pos[:,0], Y =
      _pos[:,1], Z = _pos[:,2]``

  ``_unitcell``
      unit cell dimensions and angles; the format depends on the underlying
      trajectory format. A user should use :attr:`Timestep.dimensions` to
      access the data in a standard format.


Trajectory Reader class
~~~~~~~~~~~~~~~~~~~~~~~

Trajectory readers are derived from :class:`MDAnalysis.coordinates.base.Reader`.
Typically, many methods and attributes are overriden.

Methods
.......

The :class:`MDAnalysis.coordinates.DCD.DCDReader` class is the primary
implementation example.

**Mandatory methods**

The following methods must be implemented in a Reader class.

 ``__init__(filename, **kwargs)``
     open *filename*; other *kwargs* are processed as needed and the
     Reader is free to ignore them. Typically, MDAnalysis supplies as
     much information as possible to the Reader in `kwargs`; at the moment the
     following data are supplied in keywords when a trajectory is loaded from
     within :class:`MDAnalysis.Universe`:

      - *numatoms*: the number of atoms (known from the topology)

 ``__iter__()``
     allow iteration from beginning to end::

        for ts in trajectory:
            print ts.frame

 ``close()``
     close the file and cease I/O
 ``__del__()``
     ensure that the trajectory is closed
 ``next()``
     advance to next time step or raise :exc:`IOError` when moving
     past the last frame
 ``rewind()``
     reposition to first frame


**Optional methods**

Not all trajectory formats support the following methods, either because the
data are not available or the methods have not been implemented. Code should
deal with missing methods gracefully.

 ``__len__()``
     number of frames in trajectory

 ``__getitem__(arg)``
     advance to time step `arg` = `frame` and return :class:`Timestep`; or if `arg` is a
     slice, then return an iterator over that part of the trajectory.

     The first functionality allows one to randomly access frames in the
     trajectory::

       universe.trajectory[314]

     would load frame 314 into the current :class:`Timestep`.

     Using slices allows iteration over parts of a trajectory ::

       for ts in universe.trajectory[1000:2000]:
           process_frame(ts)   # do something

     or skipping frames ::

       for ts in universe.trajectory[1000::100]:
           process_frame(ts)   # do something

     The last example starts reading the trajectory at frame 1000 and
     reads every 100th frame until the end.

     The performance of the ``__getitem__()`` method depends on the underlying
     trajectory reader and if it can implement random access to frames. In many
     cases this is not easily (or reliably) implementable and thus one is
     restricted to sequential iteration.

 ``Writer(filename, **kwargs)``
     returns a :class:`~MDAnalysis.coordinates.base.Writer` which is set up with
     the same parameters as the trajectory that is being read (e.g. time step,
     length etc), which facilitates copying and simple on-the-fly manipulation.

     If no Writer is defined then a :exc:`NotImplementedError` is raised.

     The *kwargs* can be used to customize the Writer as they are typically
     passed through to the init method of the Writer, with sensible defaults
     filled in; the actual keyword arguments depend on the Writer.

 ``timeseries(atomGroup, [start[,stop[,skip[,format]]]])``
     returns a subset of coordinate data

 ``correl(timeseriesCollection[,start[,stop[,skip]]])``
     populate a :class:`MDAnalysis.core.Timeseries.TimeseriesCollection` object
     with observable timeseries computed from the trajectory


Attributes
..........

 ``filename``
     filename of the trajectory
 ``numatoms``
     number of atoms (coordinate sets) in a frame (constant)
 ``numframes``
     total number of frames (if known) -- ``None`` if not known
 ``fixed``
     bool, saying if there are fixed atoms (e.g. dcds)
 ``skip``
     step size for iterating through the trajectory [1]
 ``skip_timestep``
     number of integrator steps between frames + 1 (i.e.
     the stride at which the MD simulation was sampled)
 ``delta``
     integrator time step (in native units); hence the "length"
     of a trajctory frame is  ``skip_timestep*delta`` time units
 ``periodic``
     contains box information for periodic boundary conditions
 ``ts``
     the :class:`~base.Timestep` object; typically customized for each
     trajectory format and derived from :class:`base.Timestep`.
 ``units``
     dictionary with keys *time* and *length* and the appropriate
     unit (e.g. 'AKMA' and 'Angstrom' for Charmm dcds, 'ps' and 'nm'
     for Gromacs trajectories, ``None`` and 'Angstrom' for PDB).
 ``format``
     string that identifies the file format, e.g. "DCD", "PDB", "CRD", "XTC",
     "TRR"; this is typically the file extension in upper case.
 ``dt``
     time between frames in ps; a managed attribute (read only) that computes
     on the fly ``skip_timestep * delta`` and converts to the MDAnalysis base
     unit for time (pico seconds by default)
 ``totaltime``
     total length of the trajectory = ``numframes * dt``
 ``time``
     time of the current time step, in MDAnalysis time units (ps)
 ``frame``
     frame number of the current time step

**Optional attributes**

 ``compressed``
     string that identifies the compression (e.g. "gz" or "bz2") or ``None``.


Trajectory Writer class
~~~~~~~~~~~~~~~~~~~~~~~

Trajectory readers are derived from
:class:`MDAnalysis.coordinates.base.Writer`. They are use to write
multiple frames to a trajectory file. Every time the
:meth:`~MDAnalysis.coordinates.base.Writer.write` method is called,
another frame is appended to the trajectory.

Typically, many methods and attributes are overriden.

Signature::

   W = TrajectoryWriter(filename,numatoms,**kwargs)
   W.write_next_timestep(Timestep)

or::

   W.write(AtomGroup)   # write a selection
   W.write(Universe)    # write a whole universe
   W.write(Timestep)    # same as write_next_timestep()


Methods
.......

 ``__init__(filename,numatoms[,start[,step[,delta[,remarks]]]])``
     opens *filename* and writes header if required by format
 ``write(obj)``
     write Timestep data in *obj*
 ``write_next_timestep([timestep])``
     write data in *timestep* to trajectory file
 ``convert_dimensions_to_unitcell(timestep)``
     take the dimensions from the timestep and convert to the native
     unitcell representation of the format
 ``close_trajectory()``
     close file and finish I/O
 ``__del__()``
     ensures that close() is called

Attributes
..........

 ``filename``
     name of the trajectory file
 ``start, stop, step``
     first and last frame and step
 ``units``
     dictionary with keys *time* and *length* and the appropriate
     unit (e.g. 'AKMA' and 'Angstrom' for CHARMM dcds, 'ps' and 'nm'
     for Gromacs trajectories, ``None`` and 'Angstrom' for PDB)
 ``format``
     string that identifies the file format, e.g. "DCD", "PDB", "CRD", "XTC",
     "TRR"


**Optional**

 ``ts``
     :class:`Timestep` instance


Single Frame Writer class
~~~~~~~~~~~~~~~~~~~~~~~~~

A single frame writer is a special case of a trajectory writer in that it
writes only a single coordinate frame to a file, for instance, a pdb or gro
file. Unlike trajectory formats, which only contains coordinates, *single
frame* formats contain much more information (e.g. atom and residue names and
numbers) and hence it is possible to write selections of atoms in a meaningful
way.

Signature::

   W = FrameWriter(filename, **kwargs)
   W.write(AtomGroup)
   W.write(Universe)

The blanket *kwargs* is required so that one can pass the same kind of
arguments (filename and numatoms) as for the Trajectory writers. In
this way, the simple :func:`~MDAnalysis.coordinates.core.writer`
factory function can be used for all writers.

Methods
.......
 ``__init__(filename, **kwargs)``
   opens *filename* for writing; `kwargs` are typically ignored
 ``write(obj)``
   writes the object *obj*, containing a
   :class:`~MDAnalysis.core.AtomGroup.AtomGroup` group of atoms (typically
   obtained from a selection) or :class:`~MDAnalysis.core.AtomGroup.Universe`
   to the file and closes the file

.. Note:: Trajectory and Frame writers can be used in almost exactly the same
   manner with the one difference that Frame writers cannot deal with raw
   :class:`~MDAnalysis.coordinates.base.Timestep` objects.


Reader/Writer registry
----------------------

The following data structures connect reader/writer classes to their
format identifiers. They are documented for programmers who want to
enhance MDAnalysis; the casual user is unlikely to access them
directly.

.. autodata:: _trajectory_readers
.. autodata:: _topology_coordinates_readers
.. autodata:: _trajectory_readers_permissive
.. autodata:: _compressed_formats
.. autodata:: _frame_writers
.. autodata:: _trajectory_writers

"""

__all__ = ['reader', 'writer']

import PDB, PQR, DCD, CRD, XTC, TRR, GRO, XYZ, TRJ, PDBQT  #, NETCDF
import base
from core import reader, writer

#: standard trajectory readers (dict with identifier as key and reader class as value)
_trajectory_readers = {'DCD': DCD.DCDReader,
                       'TRJ': DCD.DCDReader,
                       'XTC': XTC.XTCReader,
                       'XYZ': XYZ.XYZReader,
                       'TRR': TRR.TRRReader,
                       'PDB': PDB.PDBReader,
                       'PDBQT': PDBQT.PDBQTReader,
                       'CRD': CRD.CRDReader,
                       'GRO': GRO.GROReader,
                       'TRJ':TRJ.TRJReader,     # Amber text
                       'MDCRD':TRJ.TRJReader,   # Amber text
                       #'NETCDF':NETCDFReader,  # Amber netcdf
                       'PQR': PQR.PQRReader,
                       'CHAIN': base.ChainReader,
                       }

#: formats of readers that can also handle gzip or bzip2 compressed files
_compressed_formats = ['XYZ', 'TRJ', 'MDCRD', 'PQR', 'PDBQT']

#: readers of files that contain both topology/atom data and coordinates
#: (currently only the keys are used)
_topology_coordinates_readers = {
                       'PDB': PDB.PrimitivePDBReader,
                       'PDBQT': PDBQT.PDBQTReader,
                       'GRO': GRO.GROReader,
                       'CRD': CRD.CRDReader,
                       'PQR': PQR.PQRReader,
}

#: hack: readers that ignore most errors (permissive=True); at the moment
#: the same as :data:`_trajectory_readers` with the exception of the
#: the PDB reader (:class:`~MDAnalysis.coordinates.PDB.PDBReader` is replaced by :class:`~MDAnalysis.coordinates.PDB.PrimitivePDBReader`).
_trajectory_readers_permissive = _trajectory_readers.copy()
_trajectory_readers_permissive['PDB'] =  PDB.PrimitivePDBReader

#: frame writers: export to single frame formats such as PDB, gro, crd
#: Signature::
#:
#:   W = FrameWriter(filename)
#:   W.write(AtomGroup)
_frame_writers = {'PDB': PDB.PrimitivePDBWriter,
                  'PDBQT': PDBQT.PDBQTWriter,
                  'CRD': CRD.CRDWriter,
                  'GRO': GRO.GROWriter,
                 }

#: trajectory writers: export frames, typically only saving coordinates
#: Signature::
#:
#:   W = TrajectoryWriter(filename,numatoms,**kwargs)
#:   W.write_next_timestep(TimeStep)
#:   W.write(Timestep)
#:   W.write(AtomGroup)
#:   W.write(Universe)
_trajectory_writers = {'DCD': DCD.DCDWriter,
                       'XTC': XTC.XTCWriter,
                       'TRR': TRR.TRRWriter,
                       }
# note: no PDB movies yet