import numpy as np
import os
import cv2
import glob
import configure as cfg
from Feature_Cluster.Feature_Extract import feature_extract
from Feature_Cluster.Feature_Optimize import feature_optimize
from Feature_Cluster.Feature_Reduce import feature_reduce
from Feature_Cluster.Feature_Cluster_Visualize import feature_cluster, feature_visualize
from Clusters_Classification.Train import train
from Clusters_Classification.Test import test
from numba import cuda
import time


def work_flow(img_root):
    # material
    start = time.time()
    material = feature_extract(img_root, 'material')
    end = time.time()
    etime = end - start

    start = time.time()
    material_fv = feature_optimize(material, 'material')
    end = time.time()
    otime = end-start

    start = time.time()
    material_pca = feature_reduce(material_fv, 'material')
    end = time.time()
    rtime = end - start
    print(
        f"Extract : {etime : .3f}\nOptimize : {otime :.3f}\nReduce : {rtime : .3f}")
    # texture
    start = time.time()
    texture = feature_extract(img_root, 'texture')
    end = time.time()
    etime = end - start

    start = time.time()
    texture_fv = feature_optimize(texture, 'texture')
    end = time.time()
    otime = end-start

    start = time.time()
    texture_pca = feature_reduce(texture_fv, 'texture')
    end = time.time()
    rtime = end - start

    print(
        f"Extract : {etime : .3f}\nOptimize : {otime :.3f}\nReduce : {rtime : .3f}")

    cuda.select_device(0)
    cuda.close()

    # color
    start = time.time()
    color = feature_extract(img_root, 'color')
    color_pca = feature_reduce(color, 'color')
    end = time.time()
    col_time = end - start
    print(f"Color : {col_time:.3f}")
    del material, material_fv, texture, texture_fv

    #######################################################################

    # material_pca = np.load(f"{cfg.Feature_Root}/material_pca.npy")
    # texture_pca = np.load(f"{cfg.Feature_Root}/texture_pca.npy")
    # color_pca = np.load(f"{cfg.Feature_Root}/color_pca.npy")

    # concatenate features
    features = np.concatenate((material_pca, texture_pca, color_pca), axis=1)

    # K-Means Clustering
    start = time.time()
    kmeans = feature_cluster(features)
    end = time.time()
    ctime = end - start
    print(f"Clustering : {ctime : .3f}")
    # Visaulize
    start = time.time()
    feature_visualize(features, kmeans, False)
    end = time.time()
    vtime = end-start
    print(f"Visualize : {vtime :.3f}")
    # Classification
    start = time.time()
    model = train(features, kmeans.labels_, epoch=50, draw=False)
    test(features, kmeans.labels_, model)
    end = time.time()
    cls_time = end - start
    print(f"Classification : {cls_time:.3f}")


if __name__ == "__main__":
    work_flow(cfg.IMG_Root)
