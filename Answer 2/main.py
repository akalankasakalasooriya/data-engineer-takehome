import argparse
from PIL import Image
import boto3
from botocore.exceptions import ClientError

# Config AWS Connection
# or config aws cli by giving credentials
session = boto3.Session(
    aws_access_key_id="xxx",
    aws_secret_access_key="xxx",
)
s3_client = session.client('s3')
s3 = boto3.resource('s3')


#


def get_image_paths(source_bucket_name: str) -> list:
    """

    :param source_bucket_name: source bucket name
    :return: list of image paths in source bucket
    """
    accept_image_ext = ["jpeg", "png", "jpg", "gif"]
    image_paths = []
    source_bucket = s3.Bucket(source_bucket_name)
    try:
        for file_path in source_bucket.objects.all():
            if str(file_path.key).split(".")[-1] in accept_image_ext:
                image_paths.append(str(file_path.key))
    except ClientError as e:
        print(e)
    return image_paths


# ref : https://stackoverflow.com/questions/43864101/python-pil-check-if-image-is-transparent
def has_transparency(img) -> bool:
    """

    :param img: PIL image
    :return: True if image has transparent pixels else False
    """
    if img.info.get("transparency", None) is not None:
        return True
    if img.mode == "P":
        transparent = img.info.get("transparency", -1)
        for _, index in img.getcolors():
            if index == transparent:
                return True
    elif img.mode == "RGBA":
        extrema = img.getextrema()
        if extrema[3][0] < 255:
            return True

    return False


def main_function(source_bucket: str, destination_bucket: str) -> None:
    """
    copy and log images or image name based on the transparency
    :param source_bucket: source bucket name
    :param destination_bucket: destination bucket name
    :return: None
    """
    try:
        source = s3.Bucket(source_bucket)
        source_image_paths = get_image_paths(source_bucket)
        for path in source_image_paths:
            file_object = source.Object(path)
            response = file_object.get()
            file_stream = response['Body']
            im = Image.open(file_stream)
            # check transparent status
            if has_transparency(im):
                # if image has transparent pixels log file names
                with open("./transparent_images.log", "a+") as myfile:
                    myfile.write(f"{path}\n")
            else:
                copy_source = {
                    'Bucket': source_bucket,
                    'Key': path
                }
                s3.meta.client.copy(
                    copy_source, destination_bucket, path.split("/")[-1])
    except ClientError as e:
        print(e)
    except Exception as e:
        print(e)
    print("Done")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='AWS S3 transparent pixel detector')
    parser.add_argument('--source', required=True, help='Source S3 bucket name')
    parser.add_argument('--destination', required=True, help='Destination S3 bucket name')
    args = parser.parse_args()

    if args.source and args.destination:
        main_function(args.source, args.destination)
    else:
        print("Something went wrong...")
