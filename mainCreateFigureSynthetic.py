import os
import sys

sys.path.append(os.getcwd())
import CreateFigureSynthetic as cf
import argparse
from config import Config as cfg

# select the device to be used for training
device = "cpu"  # th.device("cuda" if th.cuda.is_available() else "cpu")
data_path = "cifar-10/"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config', default="Configs/default.cfg", help="Specify config file", metavar="FILE")
    args = parser.parse_args()

    cfg.load_config(args.config)
    cfg.calc_derived_params()

    # some parameters:
    depth = 1
    # hyper-parameters per depth (resolution)
    res = [256]
    num_epochs = [5000]
    fade_ins = [0]
    batch_sizes = [1]
    latent_size = 64
    cfg.Batch_Size = 1

    # ======================================================================
    # This line creates the PRO-GAN
    # ======================================================================
    gd = cf.CreateFigure(args=cfg)
    # ======================================================================

    # ======================================================================
    # This line trains the PRO-GAN
    # ======================================================================
    gd.Create(
        epochs=num_epochs[0])
