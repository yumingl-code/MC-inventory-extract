set +e

python extract_inventory.py -ov -ne -en --remove-farms "${MC_SAVE_LOCATION}/hermitcraft9" hermitcraft9_nofarm_asis.nbt &
python extract_inventory.py -ov -ne -en --remove-farms --as-chest "${MC_SAVE_LOCATION}/hermitcraft9" hermitcraft9_nofarm_chests.nbt &
python extract_inventory.py -ov -ne -en --remove-farms --isolate-box --as-chest "${MC_SAVE_LOCATION}/hermitcraft9" hermitcraft9_nofarm_box_on_floor.nbt &
python extract_inventory.py -ov -ne -en --remove-farms --isolate-box --as-chest --box-up --no-box-mixed-chest "${MC_SAVE_LOCATION}/hermitcraft9" hermitcraft9_nofarm_box_up_except_mixed.nbt &
python extract_inventory.py -ov -ne -en --remove-farms --isolate-box --as-chest --box-up "${MC_SAVE_LOCATION}/hermitcraft9" hermitcraft9_nofarm_box_up_all.nbt &
python extract_inventory.py -ov -ne -en --remove-farms --isolate-box --as-chest --box-up --remove-empty-boxes --no-box-mixed-chest "${MC_SAVE_LOCATION}/hermitcraft9" hermitcraft9_nofarm_noempty_box_up_except_mixed.nbt &
python extract_inventory.py -ov -ne -en --remove-farms --isolate-box --as-chest --box-up --remove-empty-boxes "${MC_SAVE_LOCATION}/hermitcraft9" hermitcraft9_nofarm_noempty_box_up_all.nbt &

wait

python extract_inventory.py -ov -ne -en "${MC_SAVE_LOCATION}/hermitcraft9" hermitcraft9_asis.nbt &
python extract_inventory.py -ov -ne -en --as-chest "${MC_SAVE_LOCATION}/hermitcraft9" hermitcraft9_chests.nbt &
python extract_inventory.py -ov -ne -en --isolate-box --as-chest "${MC_SAVE_LOCATION}/hermitcraft9" hermitcraft9_box_on_floor.nbt &
python extract_inventory.py -ov -ne -en --isolate-box --as-chest --box-up --no-box-mixed-chest "${MC_SAVE_LOCATION}/hermitcraft9" hermitcraft9_box_up_except_mixed.nbt &
python extract_inventory.py -ov -ne -en --isolate-box --as-chest --box-up "${MC_SAVE_LOCATION}/hermitcraft9" hermitcraft9_box_up_all.nbt &
python extract_inventory.py -ov -ne -en --isolate-box --as-chest --box-up --remove-empty-boxes --no-box-mixed-chest "${MC_SAVE_LOCATION}/hermitcraft9" hermitcraft9_noempty_box_up_except_mixed.nbt &
python extract_inventory.py -ov -ne -en --isolate-box --as-chest --box-up --remove-empty-boxes "${MC_SAVE_LOCATION}/hermitcraft9" hermitcraft9_noempty_box_up_all.nbt &

wait
