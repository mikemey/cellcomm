#!/usr/bin/env bash

run_ids=(
  "07-10-1809-TAC4-enc13"
  "07-10-2042-TAC4-enc14"
  "07-10-2317-TAC4-enc15"
  "07-11-0152-TAC4-enc16"
  "07-11-0426-TAC4-enc17"
)

image_delay=50
image_ids=(
  "tsne_3d"
  "umap_pos0"
  "umap_pos1"
  "umap_pos2"
#  "pca_3d"
#  "pca_4d"
#  "umap_2d"
#  "umap_3d"
#  "umap_4d"
)

for run_id in ${run_ids[@]}; do
  printf "\t============ run id: '${run_id}' ============\n"
  for iid in ${image_ids[@]}; do
    files=`ls -1 logs/${run_id}/*${iid}*`
    fl_file="z_${iid}.txt"
    gif_file="z_${iid}.gif"
    mp4_file="${run_id}_${iid}.mp4"

    echo "$files" > "$fl_file"

    printf "image id '${iid}' = converting to gif... "
    convert -delay ${image_delay} @${fl_file} ${gif_file}
    printf "to mp4...\n"
    HandBrakeCLI --preset="HQ 720p30 Surround" --audio "none" -i "$gif_file" -o "$mp4_file" 2> /dev/null
    rm ${fl_file}
    rm ${gif_file}
  done
done