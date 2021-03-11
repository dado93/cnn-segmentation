# CNN Segmentation Package
This repository contains the source code of the segmentation package. This package provides utility functions to be used for CNN-based segmentation of medical images.

## Submodules:
#### Segmentation 
- `segmentation.callbacks`: callbacks used during the training of the network
- `segmentation.cnn`: this module allows to define CNN-based models in a dynamic way
- `segmentation.data`: this module implements functions to handle data in various way
- `segmentation.losses`: this module allows to define loss functions to be used for segmentation tasks
- `segmentation.metrics`: in this module, metrics to be used during the training of the network are implemented
- `segmentation.utils`: utils functions used for various purposes

#### Segmentation.preprocess
Submodule to preprocess dicom or Nifti files to adapt data for training and optimize memory
- `segmentation.preprocess.main_preprocess`: this module contains the main preprocessing functions 
- `segmentation.preprocess.Cycles`: this module contains example functions to loop over files and call the main functions
- `segmentation.preprocess.utils`: utils functions used for various purposes

Current lab students working on the project:
    - Alberto Faglia: [AlbiFag](https://github.com/AlbiFag)

## Contribution
When contributing to the code and before submitting a pull request, please make sure to run
`make -B` to update the documentation of the project.

## Documentation
Documentation of the package can be found at the following link: [https://ltebs-polimi.github.io/cnn-segmentation/](https://ltebs-polimi.github.io/cnn-segmentation/)