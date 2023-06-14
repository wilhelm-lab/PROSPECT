

# code adopted and modified based on:
# https://github.com/horsepurve/DeepRTplus/blob/cde829ef4bd8b38a216d668cf79757c07133b34b/RTdata_emb.py
def timedelta_metric(y_true, y_pred, threshold=0.95, two_sided=False):
    import numpy as np

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    abs_error = np.abs(y_true - y_pred)
    
    mark_threshold = int(np.ceil(len(y_true) * threshold))
    delta_at_threshold = sorted(abs_error)[mark_threshold - 1]
    
    norm_range = np.max(y_true) - np.min(y_true)
    
    if two_sided:
        return (delta_at_threshold * 2) / (norm_range)
    else:
        return delta_at_threshold / norm_range
      
      
def masked_spectral_distance(y_true, y_pred, epsilon = 1e-7):
    import numpy as np
    
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    pred_masked = ((y_true + 1) * y_pred) / (y_true + 1 + 1e-7)
    true_masked = ((y_true + 1) * y_true) / (y_true + 1 + 1e-7)
    
    true_norm = true_masked * (1/np.sqrt(np.sum(np.square(true_masked), axis=1)))[:,None]
    
    pred_norm = pred_masked * (1/np.sqrt(np.sum(np.square(pred_masked), axis=1)))[:,None]
    
    product = np.sum(true_norm * pred_norm, axis=1)
    
    arccosine = np.arccos(product)
    
    return 2 * arccosine / np.pi
