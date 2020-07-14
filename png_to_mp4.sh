#!/usr/bin/env bash

image_delay=50
image_ids=(
  "2Dc"
  "3Dm"
  "3Dc"
#  "pca_4d"
#  "umap_2d"
#  "umap_3d"
#  "umap_4d"
)

function convert_to_mp4 () {
    run_id="$1"
    unique_img_id="$2"
    search_query="logs/${run_id}/*${unique_img_id}*"

    files=`ls -1 ${search_query} 2> /dev/null`
    if [[ -z ${files} ]]; then
      printf "query ${unique_img_id} -> no results: [${run_id}]\n"
      return
    fi

    printf " ---- converting: [${run_id}]\n"
    fl_file="z_${unique_img_id}.txt"
    gif_file="z_${unique_img_id}.gif"
    mp4_file="${run_id}_${unique_img_id}.mp4"

    printf "image id '${unique_img_id}' = converting to gif... "
    echo "$files" > "$fl_file"
    convert -delay ${image_delay} @${fl_file} ${gif_file}
    printf "to mp4...\n"
    HandBrakeCLI --preset="HQ 720p30 Surround" --audio "none" -i "$gif_file" -o "$mp4_file" 2> /dev/null
    rm ${fl_file}
    rm ${gif_file}
}

#convert_to_mp4 "07-14-1310_TAC4-gen2inputs-e_3" "2Dc"
#convert_to_mp4 "07-14-1310_TAC4-gen2inputs-e_3" "3Dm"
#convert_to_mp4 "07-14-1310_TAC4-gen2inputs-e_4" "3Dc"

for run_id in ${@}; do
  printf "\t============ run id: '${run_id}' ============\n"
  for iid in ${image_ids[@]}; do
    convert_to_mp4 "$run_id" "$iid"
  done
done