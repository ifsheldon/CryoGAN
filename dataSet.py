from __future__ import print_function

import scipy
import scipy.io
import torch.utils.data
from torch.utils.data.dataset import Dataset
from torch import Tensor
from Functions.FunctionsCTF import *
from Functions.FunctionsDataset import *
from Functions.FunctionsFourier import *
from Functions.FunctionsSymmetry import *


class Cryo(Dataset):

    def __init__(self, args=None):

        self.dataset = args.dataset

        self.args = args
        dataset = self.dataset
        self.data_type = args.data_type
        self.ProjectionMask = None
        self.ProjectionMaskFourier = None

        if dataset == 'Betagal':

            self.MicrographStack = []
            self.coordinatesList = []

            numMicroGraphs = 1538

            self.numParticlesfromMicrograph = np.zeros((numMicroGraphs, 1))
            self.MicrographFromIdx = None
            self.CoordinateFromIdx = None
            dir = './Datasets/Betagal-Experimental/'

            self.ParticlePath = './Datasets/Betagal-Experimental/Particles-384/'
            list = os.listdir(self.ParticlePath)
            self.train_size = len([x for x in list if '.mrc' in x])

            self.MicrographFromIdx = np.zeros((50000, 1))

            counterParticle = -1

            for micrographNum in range(1539):

                boxName = "./Datasets/Betagal-Experimental/MicrographDetails/EMD-2984_{:04d}.box".format(micrographNum)

                numCols = 4
                boxes = np.fromfile(boxName, sep="\t", dtype=np.int).reshape(-1, numCols)
                for i in range(len(boxes)):
                    counterParticle = counterParticle + 1
                    self.MicrographFromIdx[counterParticle, 0] = micrographNum

                # ==========For Micrographs

                pathMicrographCTF = './Datasets/Betagal-Experimental/ctf-betagal-all-3185.txt'
                self.pathCTF = pathMicrographCTF

                file = open(pathMicrographCTF, 'r')
                lines = file.read().split()

                if True:
                    self.EstimatedDefocuses = np.zeros((1539, 3))

                    for i, element in enumerate(lines, 0):
                        if i // 8 == self.EstimatedDefocuses.shape[0] + 1:
                            break

                        if self.args.UseEstimatedDefocuses:

                            if 5 > i % 8 > 1:
                                self.EstimatedDefocuses[i // 8, i % 8 - 2] = float(element)

                    file.close()
                    self.EstimatedDefocuses[:, 0] = self.EstimatedDefocuses[:, 0] / 1e4
                    self.EstimatedDefocuses[:, 1] = self.EstimatedDefocuses[:, 1] / 1e4
                    self.EstimatedDefocuses[:, 2] = self.EstimatedDefocuses[:, 2] * np.pi / 180.0


        elif self.args.dataset in ['Betagal-Synthetic']:
            if self.args.AlgoType == 'generate':
                total_images = self.args.DatasetSize
            else:

                dir = './Datasets/' + self.args.dataset + '/' + self.args.dataset_name + '/'
                list = os.listdir(dir)
                listmrc = [x for x in list if '.mrc' in x]
                self.ImageStack = [dir + x for x in listmrc if 'projNoisy' in x]
                self.train_size = len(self.ImageStack)
                total_images = self.train_size

            self.train_size = total_images

        if self.data_type == 'even' or self.data_type == 'odd':
            self.train_size = self.train_size // 2
        else:
            self.train_size = self.train_size

        print('Training Size=' + str(self.train_size))

    def __len__(self):
        return self.train_size

    def __getitem__(self, idx):

        if self.data_type == 'even':
            idx = 2 * idx
        elif self.data_type == 'odd':
            idx = 2 * idx + 1

        with torch.no_grad():
            if self.dataset == 'Betagal':

                with mrcfile.open(self.ParticlePath + str(idx).zfill(6) + ".mrc") as m:
                    image = np.array(m.data, dtype=np.float32)
                if self.args.GaussianFilterProjection:
                    image = scipy.ndimage.gaussian_filter(image, self.args.GaussianSigma, )

                image = Tensor(image).unsqueeze(0).cuda()



            elif self.dataset in ['Betagal-Synthetic']:

                with mrcfile.mmap(self.ImageStack[idx], permissive=True, mode='r+') as m:
                    image = m.data
                    if self.args.GaussianFilterProjection:
                        image = scipy.ndimage.gaussian_filter(image, self.args.GaussianSigma)
                    image = Tensor(image).unsqueeze(0).cuda()

            else:

                image = self.ImageStack[idx]
                image = Tensor(image).unsqueeze(0).cuda()

        downsampling = image.shape[-1] // self.args.RawProjectionSize
        if downsampling > 1:
            image = torch.nn.functional.avg_pool2d(image, kernel_size=downsampling, stride=downsampling, padding=0)

        if self.args.NormalizeProjections:
            image = (image - image.mean()) / image.std()

        return image
