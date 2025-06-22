# Claude Memory

The project is to create a terminal-based medical image viewer. The following are the requirements:

1. The viewer will be called from the command-line as: >pydcmview <path_to_image_file_or_dicom_directory>
2. The viewer will support display of medical images from DICOM, NRRD, and Nifti formats.
3. Only one 2D slice will be in display at a time.
4. If the image has more than 2 dimensions (N-dimensional), then there is an overlay to select which dimensions will be x and y. The overlay will be accessible by pressing the "t" key. The overlay will then show the available dimensions. Arrow keys or vim motion keys are used to highlight a specific dimension. The "x" or "y" buttons would then be used to assign the x or y display dimension to the data dimension respectively. If a dimension is already assigned and the opposite key is pressed, the assignments will swap. The "f" key toggles dimension flipping (marked with *). Pressing ENTER or ESC will close the overlay.
5. Scrolling through the slices can be controlled by up/down arrow keys or vim motion keys (j,k).
6. A crosshair mode can be entered by pressing "c". In this mode, the arrow keys or vim motion keys will control a crosshair that is overlaid on the current image. The pixel position and the intensity value will be displays in a bottom status bar. When different axes have been selected for display, the displayed slice will correspond to the crosshair location. The crosshair opacity can be adjusted with Shift+up/down or Shift+j/k. The crosshair mode can be exited by pressing the ESC button.
7. Zoom in/out functionality is available with +/- keys in normal mode.
8. There will be a status bar at the bottom of the display that always shows the available keys. This applies for all menus and modes of the app.

The following libraries will be used for UI/UX:
1. textual
2. textual-image -- image display in textual

The SimpleITK library will be used for handling data I/O. NumPy will be used for array data types and manipulation.

Sun Jun 22 22:06:16 CEST 2025

For first implementation, only directly loading, slicing through the volume, and the functions mentioned above are needed. No additional features such as affine transforms will be implemented at this stage.
