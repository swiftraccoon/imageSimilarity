"""
This module provides functionality to find and delete images similar to a given reference image.
"""

import argparse
import os
import sys
from PIL import Image
import imagehash


def calculate_image_hash(image_path):
    """
    Calculate the hash of an image.

    Args:
        image_path (str): The path to the image file.

    Returns:
        imagehash.ImageHash: The hash of the image.
    """
    try:
        with Image.open(image_path) as img:
            return imagehash.average_hash(img)
    except IOError as error:
        print(f"Error: Cannot open the image file {image_path}. {error}")
        sys.exit(1)


def find_similar_images(user_image_path, directory_path, threshold):
    """
    Find images that are similar to the provided image within a directory.

    Args:
        user_image_path (str): The path to the user's image.
        directory_path (str): The directory path to search for similar images.
        threshold (int): The threshold for image similarity.

    Returns:
        list: A list of filenames of similar images.
    """
    user_image_hash = calculate_image_hash(user_image_path)
    similar_images = []

    for image_filename in os.listdir(directory_path):
        if image_filename == os.path.basename(user_image_path):
            continue

        image_path = os.path.join(directory_path, image_filename)
        image_hash = calculate_image_hash(image_path)

        if user_image_hash - image_hash < threshold:  # Threshold for similarity
            similar_images.append(image_filename)

    return similar_images


def delete_images(directory_path, images_to_delete):
    """
    Delete the specified images from the directory.

    Args:
        directory_path (str): The directory path where the images are located.
        images_to_delete (list): A list of filenames to delete.
    """
    for filename in images_to_delete:
        try:
            os.remove(os.path.join(directory_path, filename))
            print(f"Deleted {filename}")
        except OSError as error:
            print(f"Error: Could not delete {filename}. {error}")


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        Namespace: The namespace containing the arguments.
    """
    parser = argparse.ArgumentParser(
        description='Find and delete similar images.')
    parser.add_argument('image', help='The path to the input image.')
    parser.add_argument(
        'directory', help='The directory path to search for similar images.')
    parser.add_argument('-t', '--threshold', type=int, default=10,
                        help='The threshold for image similarity (default: 10).')
    return parser.parse_args()


def main():
    """
    Main function to handle user input and initiate the image deletion process.
    """
    args = parse_arguments()

    similar_images = find_similar_images(
        args.image, args.directory, args.threshold)
    if not similar_images:
        print("No similar images found.")
        return

    print("Similar images found:")
    for idx, filename in enumerate(similar_images, 1):
        print(f"{idx}. {filename}")

    indices = input(
        "Enter the indices of images to delete (e.g., 1,2,4-6) or 'exit': ")
    if indices.lower() == 'exit':
        return

    indices_to_delete = []
    for part in indices.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            indices_to_delete.extend(range(start, end + 1))
        else:
            indices_to_delete.append(int(part))

    images_to_delete = [similar_images[i - 1]
                        for i in indices_to_delete if 0 < i <= len(similar_images)]
    delete_images(args.directory, images_to_delete)


if __name__ == "__main__":
    main()
