"""
The losses submodule implements loss function to be used
in segmentation tasks.
"""

from segmentation.metrics import MeanDice
from keras import backend as K
import numpy as np
import tensorflow as tf
from scipy.ndimage import distance_transform_edt as distance
from tensorflow.keras.losses import Loss


class MeanDiceLoss(MeanDice):

    def __init__(self, num_classes, name=None, dtype=None):
        super(MeanDice, self).__init__(self, name=name, dtype=dtype)


# class Weighted_DiceBoundary_Loss(Loss):
#     """
#     Weighted dice together with boundary loss function.
#
#     The two contribution are weighted by alpha, which needs to be initialized to 1,
#     and decreases its value according to function update_alpha.
#     Passing update_alpha and alpha to callback AlphaScheduler is needed.
#     DiceBoundaryLoss is defined as follows:
#     .. math::
#           \[
#           dbLoss = \alpha * wDice + (1 - \alpha) * boundLoss
#           .\]
#
#     Args:
#         num_classes: Possible number of classes the prediction task can have
#         batch_size: Size of the batches used for training
#         alpha: value of the parameter updated every epoch
#         name: (Optional) string name of the loss instance
#     Returns: weighted dice + boundary loss function, weighted with alpha parameter.
#
#     """
#
#     def __init__(self, num_classes, alpha, name=None, dtype=None):
#         super(Weighted_DiceBoundary_Loss, self).__init__()
#         self.num_classes = num_classes
#         self.alpha = alpha
#         self.name = name
#
# #     def _count_total_voxels(self):
# #         """
# #         Counts total number of voxels for the given batch size.
# #         Returns:
# #              : Total number of voxels
# #         """
# #         return N_ROWS * N_COLUMNS * N_SLICES * BATCH_SIZE
#
#     def _count_class_voxels(self, labels):
#         """
#         Counts total number of voxels for each class in the batch size.
#         input is supposed to be 5-dimensional: (batch, x, y, z, softmax probabilities)
#         Args:
#             labels: y_true, ground truth volumes
#         Returns:
#             out: 1D tf.tensor of len N_CLASSES with number of voxel per class
#         """
#         out = [0] * self.num_classes
#         out[0] = 0
#         for c in range(1, self.num_classes):
#             out[c] = tf.math.count_nonzero(labels[:, :, :, :, c])
#         first_term = tf.cast(self.nVoxels, 'int64')
#         second_term = tf.reduce_sum(out)
#         out[0] = tf.subtract(first_term, second_term)
#         return out
#
#     def _get_loss_weights(self, labels):
#         """
#         Compute loss weights for each class.
#         Args:
#             labels: y_true, ground truth volumes
#         Returns:
#              : 1D tf.tensor of len N_CLASSES with weights to assign to class voxels
#         """
#         self.nVoxels = 1
#         for i in range(len(labels.shape) - 1):
#             self.nVoxels = self.nVoxels * K.shape(labels)[i]
#         numerator_1 = self._count_class_voxels(labels)
#         numerator = tf.multiply(1.0 / self.nVoxels, numerator_1)
#         subtract_term = tf.subtract(1.0, numerator)
#         return tf.multiply(1.0 / (self.num_classes - 1), subtract_term)
#
#     def _calc_dist_map(self, seg):
#         """ Computes distance map using scipy function
#         Args:
#             seg: 3D volume array of ground truth
#         Returns:
#             res: 3D euclidean distance transform of the label
#         """
#         res = np.zeros_like(seg)
#         posmask = seg.astype(np.bool)
#
#         if posmask.any():
#             negmask = ~posmask
#             res = distance(negmask) * negmask - (distance(posmask) - 1) * posmask
#         return res
#
#     def _calc_dist_map_batch(self, labels):
#         """ Splits 5D labels (batch, x, y, z, classes) into 3D labels (x,y,z) to compute distance map.
#         Args:
#             labels: y_true, ground truth volumes. Labels is supposed to be 5-dimensional:
#             (batch, x, y, z, softmax probabilities).
#         Returns: 3D volume array of ground truth.
#         """
#         y_true_numpy = labels.numpy()
#         dist_batch = np.zeros_like(y_true_numpy)
#         for i, y in enumerate(y_true_numpy):
#             for c in range(y_true_numpy.shape[-1]):
#                 result = self._calc_dist_map(y[:, :, :, c])
#                 dist_batch[i, :, :, :, c] = result
#         return np.array(dist_batch).astype(np.float32)
#
#
#     def call(self, y_true, y_pred):
#         """
#         Multiclass weighted dice + boundary loss function.
#         Args:
#             y_true: Ground truth. Input is supposed to be 5-dimensional:
#                 (batch, x, y, z, softmax probabilities).
#             y_pred: Softmax probabilities. Input is supposed to be 5-dimensional:
#                 (batch, x, y, z, softmax probabilities).
#         Returns: weighted dice + boundary loss function, weighted with alpha parameter.
#
#         """
#         mean_over_classes = tf.zeros((1,))  # a single scalar, then broadcasted to a scalar for each data-point in the mini-batch
#         # Get loss weights
#         loss_weights = self._get_loss_weights(y_true)
#         # Loop over each class
#         for c in range(0, self.num_classes):
#             y_true_c = tf.cast(y_true[:, :, :, :, c], 'float32')
#             y_pred_c = tf.cast(y_pred[:, :, :, :, c], 'float32')
#             numerator = tf.scalar_mul(2.0, tf.reduce_sum(tf.multiply(y_true_c, y_pred_c), axis=(1, 2, 3)))
#             denominator = tf.add(tf.reduce_sum(y_true_c, axis=(1, 2, 3)), tf.reduce_sum(y_pred_c, axis=(1, 2, 3)))
#             class_loss_weight = loss_weights[c]
#
#             mean_over_classes = tf.add(mean_over_classes,
#                                        tf.multiply(class_loss_weight, tf.divide(numerator, denominator)))
#
#         SDM = tf.py_function(func=self._calc_dist_map_batch,
#                              inp=[y_true],
#                              Tout=tf.float32)
#         boundary_loss = tf.multiply(tf.reduce_sum(tf.multiply(SDM, y_pred)), 1.0 / self.nVoxels)
#
#         return self.alpha * tf.subtract(1.0, mean_over_classes) + (1 - self.alpha) * boundary_loss



def Weighted_DiceBoundary_Loss(numClasses, alpha, dims, batchSize):

    def calc_dist_map(seg):
        """ Computes distance map using scipy function"""
        res = np.zeros_like(seg)
        posmask = seg.astype(np.bool)

        if posmask.any():
            negmask = ~posmask
            res = distance(negmask) * negmask + (distance(posmask) - 1) * posmask
        return res

    def calc_dist_map_batch(y_true):
        """ Pass 3D label volumes to calc_dist_map and return the batch distance map to loss function """
        y_true_numpy = y_true.numpy()
        dist_batch = np.zeros_like(y_true_numpy)
        for i in range(batchSize):
            for c in range(numClasses):
                dist_batch[c,i] = calc_dist_map(y_true_numpy[c,i])
        return np.array(dist_batch).astype(np.float32)

    # def surface_loss_keras(y_true, y_pred):
    #     y_true_dist_map = tf.py_function(func=calc_dist_map_batch,
    #                                      inp=[y_true],
    #                                      Tout=tf.float32)
    #     multipled = y_pred * y_true_dist_map
    #     return K.mean(multipled)

    # def count_total_voxels(batch_size):
    #     """
    #     Counts total number of voxels for the given batch size.
    #     """
    #     return N_ROWS * N_COLUMNS * N_SLICES * batch_size

    # defining weights for loss function:

    def count_class_voxels(labels, nVoxels):
        """
        Counts total number of voxels for each class in the batch size.
        input is supposed to be 5-dimensional: (batch, x, y, z, softmax probabilities)
        """
        out = [0] * numClasses
        out[0] = 0
        for c in range(1, numClasses):
            out[c] = tf.math.count_nonzero(labels[c])
        first_term = tf.cast(nVoxels, 'int64')
        second_term = tf.reduce_sum(out)
        out[0] = tf.subtract(first_term, second_term)
        return out

    def get_loss_weights(labels, nVoxels):
        """
        Compute loss weights for each class.
        """

        numerator_1 = count_class_voxels(labels, nVoxels)
        numerator = tf.multiply(1.0 / nVoxels, numerator_1)
        subtract_term = tf.subtract(1.0, numerator)
        return tf.multiply(1.0 / (numClasses - 1), subtract_term)

    def multiclass_3D_class_weighted_dice_boundary_loss(y_true, y_pred):
        """
        Compute 3D multiclass class weighted dice loss function.
        """
        # global axisSum

        if len(dims) == 2:
            axisSum = (1, 2)
            y_pred = tf.transpose(y_pred, [3, 0, 1, 2])
            y_true = tf.transpose(y_true, [3, 0, 1, 2])
        elif len(dims) == 3:
            axisSum = (1, 2, 3)
            y_pred = tf.transpose(y_pred, [4, 0, 1, 2, 3])
            y_true = tf.transpose(y_true, [4, 0, 1, 2, 3])
        else:
            print("Could not handle input dimensions.")
            return

        # Now dimensions are --> (numClasses, batchSize, Rows, Columns, Slices)

        nVoxels = batchSize
        for i in range(len(dims)):
            nVoxels = nVoxels * dims[i]

        mean_over_classes = tf.zeros((1,))
        # Get loss weights
        loss_weights = get_loss_weights(y_true, nVoxels)
        # Loop over each class
        for c in range(numClasses):
            y_true_c = y_true[c]
            y_pred_c = y_pred[c]
            numerator = tf.scalar_mul(2.0, tf.reduce_sum(tf.multiply(y_true_c, y_pred_c), axis = axisSum))
            denominator = tf.add(tf.reduce_sum(y_true_c, axis = axisSum), tf.reduce_sum(y_pred_c, axis = axisSum))
            class_loss_weight = loss_weights[c]

            mean_over_classes = tf.add(mean_over_classes,
                                       tf.multiply(class_loss_weight,
                                       tf.divide(numerator, denominator)))

        SDM = tf.py_function(func=calc_dist_map_batch,
                             inp=[y_true],
                             Tout=tf.float32)
        boundary_loss = tf.multiply(tf.reduce_sum(tf.multiply(SDM, y_pred)), 1.0/nVoxels)

        return alpha * tf.subtract(1.0, mean_over_classes) + (1-alpha) * boundary_loss

    return multiclass_3D_class_weighted_dice_boundary_loss


