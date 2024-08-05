import glob
import pandas as pd
import subprocess

def extracte_exif_info(image_path):
    result = {}

    res = subprocess.run(f"exiftool -DateTimeOriginal -GPSLatitudeRef -GPSLatitude -GPSLongitudeRef -GPSLongitude -GPSAltitude -Make -Model -ProductName -ExposureTime -FNumber  -ISO -FocalLength  -FocalLengthIn35mmFormat -LensInfo -LensModel -LensMake {image_path}", shell=True, check=True, capture_output=True)
    res_stdout = res.stdout.decode('utf-8')
    for line in res_stdout.split("\n"):
        if len(line.strip()) == 0:
            continue
        k,v = line.split(": ")
        k = k.strip()
        v = v.strip()
        result[k] = v

    return result

if __name__ == "__main__":
    # https://github.com/exiftool/exiftool/
    src = glob.glob("data/2024-07-28打印/*.*")
    dest_infos = []
    for fp in src:
        dest_info = {
            "file": fp,
            **extracte_exif_info(fp)
        }

        # dest_info["make"] = dest_info[f"raw.Make"]
        # dest_info["date"] = dest_info[f"raw.Date/Time Original"]
        # if dest_info["make"] == "DJI":
        #     dest_info["model name"] = dest_info[f"raw.Product Name"]
        # else:
        #     dest_info["model name"] = dest_info[f"raw.Camera Model Name"]
        
        dest_infos.append(dest_info)

    dest_info_df = pd.DataFrame(dest_infos)
    dest_info_df.to_json("temp-exiftool.json",orient="records",lines=True,force_ascii=False,default_handler=str)
    
    # dest_info_df.to_excel("temp-exiftool.xlsx",index=False)
                

    # 相机品牌、型号
    # 照片焦段
    # 时间
    # 位置，经纬度转城市

    # exiftool -DateTimeOriginal -GPSLatitudeRef -GPSLatitude -GPSLongitudeRef -GPSLongitude -GPSAltitude -Model   -ExposureTime -FNumber  -ISO -FocalLength  -FocalLengthIn35mmFormat -LensInfo -LensModel -LensMake IMG_2200.HEIC IMG_0789.CR3