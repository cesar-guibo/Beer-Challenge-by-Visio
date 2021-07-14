import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score

FEATURES_RADIUS = 2

def extract_normalized_features(image, centers, radius):
    padded = np.pad(image, radius, mode='reflect')
    window_size = 2 * radius + 1
    features = []
    for x, y in centers:
        mean_r = np.mean(padded[:,:,0][x:x+window_size,y:y+window_size])
        mean_g = np.mean(padded[:,:,1][x:x+window_size,y:y+window_size])
        mean_b = np.mean(padded[:,:,2][x:x+window_size,y:y+window_size])
        summed = mean_r + mean_g + mean_b
        features.append((mean_r / summed, mean_g / summed, mean_b / summed))
    return np.array(features)

def calculate_silhouette_scores(features, clusters):
    sscores = silhouette_samples(features, clusters)
    labels = np.unique(clusters)
    label_scores = tuple(map(lambda label: sscores[clusters == label], labels))
    points = map(len, label_scores)
    means = map(np.mean, label_scores)
    return tuple(zip(labels, points, means))

def classify_cells(image, centers, model=None):
    features = extract_normalized_features(image, centers, FEATURES_RADIUS)
    model = model if model != None else KMeans(n_clusters=2)
    clusters = model.predict(features)
    return (clusters, calculate_silhouette_scores(features, clusters))
