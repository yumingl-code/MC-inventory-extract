# MC-inventory-extract

This tool scans a minecraft world for containers, and creates a structure file of the items in those containers.

## Dependencies

This was originally developed in python 3.13, and the following packages:

lz4==4.4.4  
mutf8==1.0.6  
pandas==2.3.3  

## Usage

Replace \<world directory\> with the path to your world.

```
python extract_inventory.py -ov -ne -en --isolate-box --as-chest "<world directory>" "result_box_on_floor.nbt"
```

This will create an array of mixed chests and shulker boxes containing items.

```
python extract_inventory.py -ov -ne -en --remove-farms --isolate-box --as-chest --box-up --remove-empty-boxes "<world directory>" "result_box_in_chest.nbt"
```

This will remove containers that appear to be farm output (i.e. contains a multiple of 27 stacks of the same item, or is a hopper/dropper full of the same item), then create an array of chests containing shulker boxes of items. Each shulker box contains either the non-box items originally in the same container, or all items originally in a shulker box.

Some other combinations of options can be found in `extract_inventory_generic.sh`

## Output

.nbt file: structure file to be used with structure blocks or litematica
.csv file: statistics of items included in the _output_, including extra shulker boxes created in the conversion process

## Containers scanned

This tool scans block with "Items", "RecordItem", "Book", or "item" tag in its block entity (e.g. chest, jukebox, lectern, decorated pot), as well as entities with "Items" tag (e.g. chest minecart, donkey).

## Other notes

Tested on Hermitcraft Season 10, 9, 8 world downloads. It does produce some non-empty set of items that looks right.

The output from `python extract_inventory.py -ov -ne -en --isolate-box --as-chest --box-up "./hermitcraft8" "hermitcraft8_box_up_all.nbt"` does contain all items in KikuGie's version of Hermitcraft8 stats (plus some, as farm items and generated loot chests are not filtered out).
