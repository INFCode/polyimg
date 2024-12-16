import numpy as np

def rmse_similarity(image1, image2):
    """
    Calculate the RMSE-based similarity score for floating-point RGB images in the range [0, 1].
    Returns a similarity score where 1 means identical images and 0 means completely different.
    """
    if image1.shape != image2.shape:
        raise ValueError("Input images must have the same dimensions.")
    
    # Compute the Mean Squared Error (MSE)
    mse = np.mean((image1 - image2) ** 2)
    
    # Normalize RMSE to [0, 1] for similarity
    max_possible_error = np.sqrt(3)  # Maximum RMSE for RGB images in [0, 1]
    rmse = np.sqrt(mse)
    similarity = 1 - (rmse / max_possible_error)
    return similarity

def psnr_similarity(image1, image2):
    """
    Calculate the PSNR-based similarity score for floating-point RGB images in the range [0, 1].
    Returns a similarity score where 1 means identical images and 0 means completely different.
    """
    if image1.shape != image2.shape:
        raise ValueError("Input images must have the same dimensions.")
    
    # Compute the Mean Squared Error (MSE)
    mse = np.mean((image1 - image2) ** 2)
    
    if mse == 0:
        return 1.0  # Images are identical
    
    # PSNR calculation
    max_pixel_value = 1.0  # For images in range [0, 1]
    psnr = np.log10(max_pixel_value / np.sqrt(mse))
    
    # Normalize PSNR to [0, 1] for similarity
    min_psnr = np.log10(max_pixel_value / (1 / np.sqrt(3)))  # Worst-case MSE = 1/3 for RGB
    similarity = 1 - min_psnr / psnr
    return similarity

def similarity_score(image1, image2, measure: str):
    if measure == "rmse":
        return rmse_similarity(image1, image2)
    elif measure == "psnr":
        return psnr_similarity(image1, image2)
    else:
        raise ValueError(f"Invalid similarity measure: {measure}")

def main():
    # Example input images (floating-point RGB in range [0, 1])
    # Replace with actual image loading code
    image1 = np.random.rand(256, 256, 3).astype(np.float32)
    image2 = np.random.rand(256, 256, 3).astype(np.float32)
    
    # Ensure images are in the correct range
    assert image1.min() >= 0 and image1.max() <= 1
    assert image2.min() >= 0 and image2.max() <= 1
    
    # Calculate RMSE and PSNR similarity
    rmse_sim = rmse_similarity(image1, image2)
    psnr_sim = psnr_similarity(image1, image2)
    
    print(f"RMSE Similarity: {rmse_sim}")
    print(f"PSNR Similarity: {psnr_sim}")

if __name__ == "__main__":
    main()
