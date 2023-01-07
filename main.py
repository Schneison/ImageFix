import os
from datetime import datetime

from os import walk
import piexif
from piexif import ExifIFD, ImageIFD
import re

folder_path = 'Pictures'


def read_file_date_from_name(img_name: str) -> datetime | None:
    match = re.search(r"^IMG-(\d\d\d\d\d\d\d\d)-WA\d\d\d\d.*", img_name)
    if match:
        segment = match.group(1)
        return datetime.strptime(segment, '%Y%m%d')
    match = re.search(r"(\d\d\d\d\d\d\d\d_\d\d\d\d\d\d).*", img_name)
    if not match:
        return None
    segment = match.group(1)
    return datetime.strptime(segment, '%Y%m%d_%H%M%S')


def ensure_exif_exists(exif_dict: dict):
    exif_data = exif_dict['Exif']
    if not exif_data:
        exif_dict['Exif'] = {
            ExifIFD.DateTimeOriginal: "",
            ExifIFD.DateTimeDigitized: ""
        }
        exif_data = exif_dict['Exif']

    if ExifIFD.DateTimeOriginal not in exif_data:
        exif_data[ExifIFD.DateTimeOriginal] = ""

    if ExifIFD.DateTimeDigitized not in exif_data:
        exif_data[ExifIFD.DateTimeDigitized] = ""

    # 0th should always be existed
    if ImageIFD.DateTime not in exif_dict['0th']:
        exif_dict['0th'][ImageIFD.DateTime] = ""


def main():
    target_date = datetime.strptime("2021:04:29", '%Y:%m:%d').date()
    for (sub_dir, _, filenames) in walk(folder_path):
        for file in filenames:
            if not file.endswith('.jpg'):
                continue
            file_path = os.path.join(sub_dir, file)
            # Load metadata
            exif_dict = piexif.load(file_path)
            ensure_exif_exists(exif_dict)
            original_date_time = exif_dict['Exif'][ExifIFD.DateTimeOriginal]
            if original_date_time == "" or original_date_time == target_date:
                img_name = str(file)
                try:
                    date = read_file_date_from_name(img_name)
                except ValueError as e:
                    print(e)
                    continue
                if not date:
                    continue
                print(file_path + ": " + date.strftime("%Y:%m:%d_%H:%M:%S"))
                date_str = date.strftime("%Y:%m:%d %H:%M:%S").encode("utf-8")
                # Update DateTimeOriginal
                exif_dict['Exif'][ExifIFD.DateTimeOriginal] = date_str
                # Update DateTimeDigitized
                exif_dict['Exif'][ExifIFD.DateTimeDigitized] = date_str
                # Update DateTime
                exif_dict['0th'][ImageIFD.DateTime] = date_str

                exif_bytes = piexif.dump(exif_dict)
                piexif.insert(exif_bytes, file_path)


if __name__ == "__main__":
    main()
