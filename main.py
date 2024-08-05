import argparse
import glob
import os, sys
import pandas as pd
import string
from datetime import datetime
import random
import json
from multiprocessing import Pool
import tqdm
import functools

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from watermark import log,exif_extractor,bar

logger = log.get_logger(__file__)

parser = argparse.ArgumentParser(prog='watermark')

parser.add_argument('-f', type=str, help='files to extract exifinfos or extracted file to process')
parser.add_argument('-e', action='store_true', help='do extract exifinfos')
parser.add_argument('-p', action='store_true', help='do process images')

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    random.seed(datetime.now().timestamp())
    return "".join(random.choice(chars) for _ in range(size))

def process_row(row_idx_and_row, output_dir):
    _, row = row_idx_and_row
    logger.info(f'processing {row["file"]}')
    exif_info = eval(row["exif_info"])
    content = row["content"]
    font_size = row.get("font_size",-1)

    final_image, res_font_size = bar.get_image_with_bar(row["file"], exif_info, content, font_size=font_size)
    row["font_size"] = res_font_size

    final_image.save(f'{output_dir}/{row["file"].split("/")[-1].split(".")[0]}.png',format="PNG")

if __name__ == "__main__":
    args = parser.parse_args()
    logger.info(f"args.f = {args.f}")
    logger.info(f"args.e = {args.e}")
    logger.info(f"args.p = {args.p}")
    assert args.e or args.p, "do e or p is needed!!!"
    assert args.e ^ args.p, "do e or p in single run!!!"
    if args.e:
        src = sorted(list(glob.glob(args.f)))
        dest_infos = []
        logger.info(f"src = {src}")
        for fp in src:
            logger.info(f"extracting {fp}")
            dest_info = {
                "file": fp,
                "exif_info": exif_extractor.extracte_exif_info(fp),
                "content": None,
                "font_size": -1
            }
            dest_infos.append(dest_info)
        dest_info_df = pd.DataFrame(dest_infos)
        dest_path = f"{id_generator(6)}.xlsx"
        logger.info(f"exif exporting to {dest_path}")
        dest_info_df.to_excel(dest_path,index=False)
    if args.p:
        df = pd.read_excel(args.f)
        output_dir = f"data/output/{id_generator(6)}"
        os.mkdir(output_dir)
        logger.info(f"output to {output_dir}")

        do_task = functools.partial(process_row, output_dir=output_dir)

        with Pool(processes=8, maxtasksperchild=3) as pool:
            results = list(tqdm.tqdm(pool.imap(do_task,  df.iterrows()), total=len(df)))
        # for _, row in df.iterrows():
        #     logger.info(f'processing {row["file"]}')
        #     exif_info = eval(row["exif_info"])
        #     content = row["content"]
        #     font_size = row["font_size"]

        #     final_image, res_font_size = bar.get_image_with_bar(row["file"], exif_info, content, font_size=font_size)
        #     row["font_size"] = res_font_size

        #     final_image.save(f'{output_dir}/{row["file"].split("/")[-1].split(".")[0]}.png',format="PNG")
        df.to_excel(f'{output_dir}/out.xlsx',index=False)