set -e

[ ! -z "$1" ] || (echo need world name; false)
[ ! -z "${MC_SAVE_LOCATION}" ] || (echo set MC_SAVE_LOCATION to the parent directory of all your world folders; false)

export WORLD_NAME=$1

set +e

python extract_inventory.py -ov -ne -en --remove-farms "${MC_SAVE_LOCATION}/${WORLD_NAME}" "${WORLD_NAME}_nofarm_asis.nbt" &
python extract_inventory.py -ov -ne -en --remove-farms --as-chest "${MC_SAVE_LOCATION}/${WORLD_NAME}" "${WORLD_NAME}_nofarm_chests.nbt" &
python extract_inventory.py -ov -ne -en --remove-farms --isolate-box --as-chest "${MC_SAVE_LOCATION}/${WORLD_NAME}" "${WORLD_NAME}_nofarm_box_on_floor.nbt" &
python extract_inventory.py -ov -ne -en --remove-farms --isolate-box --as-chest --box-up --no-box-mixed-chest "${MC_SAVE_LOCATION}/${WORLD_NAME}" "${WORLD_NAME}_nofarm_box_up_except_mixed.nbt" &
python extract_inventory.py -ov -ne -en --remove-farms --isolate-box --as-chest --box-up "${MC_SAVE_LOCATION}/${WORLD_NAME}" "${WORLD_NAME}_nofarm_box_up_all.nbt" &
python extract_inventory.py -ov -ne -en --remove-farms --isolate-box --as-chest --box-up --remove-empty-boxes --no-box-mixed-chest "${MC_SAVE_LOCATION}/${WORLD_NAME}" "${WORLD_NAME}_nofarm_noempty_box_up_except_mixed.nbt" &
python extract_inventory.py -ov -ne -en --remove-farms --isolate-box --as-chest --box-up --remove-empty-boxes "${MC_SAVE_LOCATION}/${WORLD_NAME}" "${WORLD_NAME}_nofarm_noempty_box_up_all.nbt" &

wait

python extract_inventory.py -ov -ne -en "${MC_SAVE_LOCATION}/${WORLD_NAME}" "${WORLD_NAME}_asis.nbt" &
python extract_inventory.py -ov -ne -en --as-chest "${MC_SAVE_LOCATION}/${WORLD_NAME}" "${WORLD_NAME}_chests.nbt" &
python extract_inventory.py -ov -ne -en --isolate-box --as-chest "${MC_SAVE_LOCATION}/${WORLD_NAME}" "${WORLD_NAME}_box_on_floor.nbt" &
python extract_inventory.py -ov -ne -en --isolate-box --as-chest --box-up --no-box-mixed-chest "${MC_SAVE_LOCATION}/${WORLD_NAME}" "${WORLD_NAME}_box_up_except_mixed.nbt" &
python extract_inventory.py -ov -ne -en --isolate-box --as-chest --box-up "${MC_SAVE_LOCATION}/${WORLD_NAME}" "${WORLD_NAME}_box_up_all.nbt" &
python extract_inventory.py -ov -ne -en --isolate-box --as-chest --box-up --remove-empty-boxes --no-box-mixed-chest "${MC_SAVE_LOCATION}/${WORLD_NAME}" "${WORLD_NAME}_noempty_box_up_except_mixed.nbt" &
python extract_inventory.py -ov -ne -en --isolate-box --as-chest --box-up --remove-empty-boxes "${MC_SAVE_LOCATION}/${WORLD_NAME}" "${WORLD_NAME}_noempty_box_up_all.nbt" &

wait
