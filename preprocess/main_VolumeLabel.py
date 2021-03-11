
from __future__ import print_function
import os
import numpy as np
import trimesh
from stl import mesh
import matplotlib.pyplot as plt
import pandas
import xlrd
from scipy.io import loadmat
import pydicom
import nibabel as nib
import plotly.graph_objects as go
from scipy.ndimage.morphology import binary_fill_holes, binary_closing, binary_erosion, binary_dilation
from skimage.transform import resize
from skimage.morphology.selem import square, disk


def Volume_Label():
    setDirVariables()

    ## Options
    b_display = 0
    cubic = 0
    compare_Matlab_Python = 0

    # Output size
    if cubic == 1:
        outSize = [200, 200, 131]
    else:
        outSize = [128, 128, 128]
    templateSize = str(outSize[0]) + '_' + str(outSize[1]) + '_' + str(outSize[2])

    # Sets
    if cubic == 0:
        InDCMmSet = 'reshape_knee_'
    else:
        InDCMmSet = 'cubic_vox_knee_'
    InDCMmSetdicom = 'knee'

    fileTemplate = InDCMmSet + templateSize
    anatomy = 'tibia'  # 'tibia'
    position = 'prox'  # 'prox'
    InSurfSet = 'ct_' + anatomy + '_'
    outSet = position + anatomy

    os.chdir(mainInputDataDirectory)

    fp = open('case.txt', 'r+')
    casePatient = fp.read()
    casePatient = int(casePatient)
    casePatient = 3
    fp.close()
    print('Patient no. {}'.format(casePatient))

    xlsName = os.path.join(mainInputDataDirectory, 'Preop Data.xlsx')
    name = pandas.ExcelFile(xlsName)
    name = xlrd.open_workbook(xlsName)
    sheet = name.sheet_by_index(0)
    rows = sheet.nrows
    study = [sheet.cell_value(i, 0) for i in range(1, rows)]

    os.chdir(mainCodeDirectory)

    ## Read volume nii
    mainPatientDirectory = 'Patient{:03d}'.format(casePatient)
    mainPatientDirectory = mainInputDataDirectory + '/' + mainPatientDirectory + '/'
    mainInputDicomDirectory = mainPatientDirectory + '/' + InDCMmSetdicom + '/'

    os.chdir(mainPatientDirectory)

    niiFilename = 'volumeCT_' + fileTemplate + '_{:03d}.nii'.format(casePatient)
    VolumeCT = loadNiiVolume(niiFilename, mainInputDicomDirectory)
    ## Normalize
    VolumeCT = normVolumeScan(VolumeCT)

    # Read stl and display
    filename = InSurfSet + study[casePatient - 1] + '.stl'
    os.chdir(mainPatientDirectory)
    my_mesh1 = trimesh.load(filename)
    my_mesh = mesh.Mesh.from_file(filename)

    os.chdir(mainCodeDirectory)

    # Build  binary volume of the reference surface corresponding to the CT volume
    VolumeSurf = VolumeCT
    VolumeSurf.volumeData = np.zeros(VolumeSurf.volumeData.shape, dtype=int)

    heights = []
    for i in range(VolumeSurf.volumeDim[2]):
        heights.append(float(VolumeSurf.volumeOffset[2]) + i * VolumeSurf.voxelSize[2])

    contours = mesh2vol(my_mesh1, heights, VolumeSurf.volumeOffset, VolumeSurf.voxelSize, VolumeSurf.volumeDim)
    indicesX = []
    indicesY = []

    for ip in range(VolumeSurf.volumeDim[2]):

        if contours[ip].shape[0] != 0:

            val = contours[ip][:, 0] - VolumeSurf.volumeOffset[0]
            val = val / (VolumeSurf.volumeDim[0] * VolumeSurf.voxelSize[0])
            val = np.round(val * VolumeSurf.volumeDim[0], 0)
            valX = val.astype(int)

            val = contours[ip][:, 1] - VolumeSurf.volumeOffset[1]
            val = val / (VolumeSurf.volumeDim[1] * VolumeSurf.voxelSize[1])
            val = np.round(val * VolumeSurf.volumeDim[0], 0)
            valY = val.astype(int)

            val_index = np.zeros((valX.shape[0], 2))
            val_index[:, 0] = valX
            val_index[:, 1] = valY
            val_index = np.unique(val_index, axis=0).astype(int)

            indicesX.append(val_index[:, 0])
            indicesY.append(val_index[:, 1])

            for i, j in zip(valY, valX):
                VolumeSurf.volumeData[i - 1, j - 1, ip] = 1
        else:
            indicesX.append([])
            indicesY.append([])

    VolumeSurfLabeled = VolumeSurf
    counter = 0
    # fill in the image each contour
    for ip in range(VolumeSurfLabeled.volumeDim[2]):

        if contours[ip].shape[0] != 0:

            non_zero_start = np.count_nonzero(VolumeSurf.volumeData[:, :, ip])

            ######## REGION FILL
            binaryImage = binary_fill_holes(VolumeSurf.volumeData[:, :, ip])
            binaryImage = binaryImage > 1 / 255
            ######### CLOSING
            kernel = np.ones((5, 5), np.uint8)
            binaryImage = binary_closing(binaryImage, kernel)
            ######### FILL HOLES AGAIN
            binaryImage = binary_fill_holes(binaryImage)

            non_zero_end = np.count_nonzero(binaryImage)

            ######### ALTERNATIVE PROCESSING FOR NON CLOSED CONTOURS
            if non_zero_end < non_zero_start * 4:
                strel = disk(2)
                binaryImage = binary_dilation(VolumeSurf.volumeData[:, :, ip], strel)
                binaryImage = binary_dilation(binaryImage, strel)
                binaryImage = binary_fill_holes(binaryImage)
                binaryImage = binary_erosion(binaryImage, strel)
                binaryImage = binary_erosion(binaryImage, strel)
                counter = counter + 1

            VolumeSurfLabeled.volumeData[:, :, ip] = binaryImage

            dMin = VolumeSurfLabeled.volumeData.min()
            D = VolumeSurfLabeled.volumeData + abs(dMin)
            D = D / D.max() * 255

    print(counter)

    ###### PLOT AND SCROLL ACROSS SLICES
    if b_display == 1:
        fig, ax = plt.subplots(1, 1)
        tracker = IndexTracker(ax, D)
        fig.canvas.mpl_connect('scroll_event', tracker.onscroll)
        plt.show()

    if compare_Matlab_Python == 1:
        name_dir = outSet + 'Label'
        mainLabelDirectory = os.path.join(mainPatientDirectory, '{}'.format(name_dir))
        os.chdir(mainLabelDirectory)
        mean_dice = dice_coeff(VolumeSurfLabeled.volumeData, outSet)
        print(mean_dice)

    # Make nii file label
    volumeData = VolumeSurfLabeled.volumeData.astype(np.short)
    volumeData = np.transpose(volumeData, [1, 0, 2])
    voxelSize = VolumeSurfLabeled.voxelSize
    volumeOffset = VolumeSurfLabeled.volumeOffset

    affine = np.eye(4)
    niiVolumeLabel = nib.Nifti1Image(volumeData, affine)
    niiVolumeLabel.header.set_slope_inter(VolumeSurfLabeled.rescaleSlope, VolumeSurfLabeled.rescaleIntercept)
    niiVolumeLabel.header.set_qform(affine, 1)
    niiVolumeLabel.header.set_zooms(voxelSize)
    niiVolumeLabel.header['qoffset_x'] = volumeOffset[0]
    niiVolumeLabel.header['qoffset_y'] = volumeOffset[1]
    niiVolumeLabel.header['qoffset_z'] = volumeOffset[2]

    os.chdir(mainPatientDirectory)

    # Save nii
    filenameLabel = 'volumeLabel_' + outSet + '_' + templateSize + '_{:03d}.nii'.format(casePatient)
    #nib.nifti1.save(niiVolumeLabel, filenameLabel)

    os.chdir(mainCodeDirectory)
