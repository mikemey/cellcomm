#!/usr/bin/env bash

run_id="07-10-1340-TAC-4-dim-rot"
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