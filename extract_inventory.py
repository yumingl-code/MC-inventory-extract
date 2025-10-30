import math
import os
import re
from mca import Mca
from NBT.nbt import nbt
import io
from typing import *
import argparse
import warnings

class Inventory:
    """
    The inventory of a container
    container_type: the block id or entity id of the container, like "minecraft:brewing_stand" or "minecraft:oak_chest_boat"
    items: list of TAG_Compound, each with keys: 'Slot' 'id' 'count' and optionally 'components'
    has_shulkerbox: INITIALLY had shulkerbox, this flag should not be cleared when shulkerbox is taken out
    """
    def __init__(self, container_type:str, items:list[nbt.TAG_Compound], pos:tuple[int,int,int], is_single_slot=False, is_shulkerbox=False, set_in_field=None):
        if not isinstance(container_type, str):
            raise TypeError
        if not isinstance(items, list):
            raise TypeError
        pos_x,pos_y,pos_z=pos
        if not isinstance(pos_x,int) or not isinstance(pos_y,int) or not isinstance(pos_z,int):
            raise TypeError
        for item in items:
            if set(item.keys())!={'Slot','id','count'} and set(item.keys())!={'Slot','id','count','components'}:
                raise ValueError()
            if not isinstance(slotid:=item['Slot'].value,int) or slotid<0 or slotid>=27:
                raise ValueError(f'cannot process slot #{item['Slot'].value}')
            if container_type.endswith('shulker_box') and item['id'].value.endswith('shulker_box'):
                raise ValueError(f'{item['id'].value} should not be in a {container_type}')
            if 'components' in item.keys() and 'minecraft:container' in item['components'] and not item['id'].value.endswith('shulker_box'):
                raise ValueError(f'{item['id'].value} as an item (inside a {container_type}) should not have inventory')
        if is_single_slot and len(items)!=1:
            raise ValueError()
        self.container_type=container_type
        self.items=list(items)
        self.pos=pos
        self.is_single_slot=is_single_slot
        self.is_shulkerbox=is_shulkerbox
        self.set_in_field=set_in_field
        self.has_shulkerbox=False
        for item in items:
            if item['id'].value.endswith('shulker_box'):
                self.has_shulkerbox=True
        self.no_nonbox=True
        self.single_item=None
        itemid=None
        itemcomponent=None
        cnt=0
        items_unpacked=items.copy()
        while items_unpacked:
            item=items_unpacked.pop()
            thisid=item['id'].value
            thiscomponents=item.get('components')
            if thisid.endswith('shulker_box'):
                if thiscomponents and (cont:=thiscomponents.get('minecraft:container')):
                    items_unpacked.extend([subitem['item'] for subitem in cont])
            elif itemid is None:
                # first non-box item in inventory
                itemid = thisid
                itemcomponent = thiscomponents
                if itemcomponent is not None:
                    itemcomponent=itemcomponent.pretty_tree()
                self.no_nonbox = False
                self.single_item = True
                cnt=item['count'].value
            else:
                # subsequent non-box items
                if itemid != thisid or (thiscomponents is None and itemcomponent is not None) or (thiscomponents is not None and thiscomponents.pretty_tree()!=itemcomponent):
                    self.single_item=False
                else:
                    cnt+=item['count'].value
        if self.single_item:
            self.item_id=itemid
            self.item_count=cnt
            self.possible_farm_collection=False
            if self.item_count % 1728 ==0:
                self.possible_farm_collection=True
            if self.item_count ==320 and container_type in ["minecraft:hopper","minecraft:hopper_minecart"] or self.item_count==576 and container_type in ["minecraft:dropper","minecraft:dispenser"]:
                self.possible_farm_collection=True
        else:
            self.item_id=None
            self.item_count=None
            self.possible_farm_collection=None
            
    
    @staticmethod
    def create_single(container_type:str, item:nbt.TAG_Compound, pos, set_in_field):
        """
        For things that only have one inventory slot (decorated pot, lectern, jukebox)
        """
        if 'Slot' not in item.keys():
            item['Slot']=nbt.TAG_Byte(0)
        return Inventory(container_type, [item], pos, is_single_slot=True, set_in_field=set_in_field)
    
    def __str__(self):
        return f'''{self.container_type} @ {self.pos[0]} {self.pos[1]} {self.pos[2]}
Single slot: {self.is_single_slot}
Has shulkerbox: {self.has_shulkerbox}
No non-box: {self.no_nonbox}
Single item: {self.single_item}
Item: {self.item_id}
Item count: {self.item_count}
Is farm: {self.possible_farm_collection}
''' + '\n'.join(item.pretty_tree() for item in self.items)

def count_items(inventories:list[Inventory]):
    from collections import Counter
    items_count=Counter()
    for inv in inventories:
        for item in inv.items:
            items_count.update({item['id'].value:item['count'].value})
            if (comp:=item.get('components')) and (cont:=comp.get('minecraft:container')):
                for subitem in cont:
                    items_count.update({subitem['item']['id'].value:subitem['item']['count'].value})
    return items_count

def iterate_regions(basedir:str, section:str, overworld:bool, nether:bool, end:bool):
    """
    get the list of all region/entities files
    basedir: path of the world directory
    section: 'entities' or 'region'
    """
    mcafnameregex=re.compile(r'r\.(-?[0-9]+)\.(-?[0-9]+)\.mca')
    dimsections=[]
    if overworld:
        dimsections.append(section)
    if nether:
        dimsections.append(os.path.join('DIM-1', section))
    if end:
        dimsections.append(os.path.join('DIM1', section))
    for dimsection in dimsections:
        try:
            filelist=os.listdir(os.path.join(basedir,dimsection))
        except FileNotFoundError:
            filelist=[]
        for fname in filelist:
            match=mcafnameregex.fullmatch(fname)
            if not match:
                continue
            regionx=int(match.group(1))
            regionz=int(match.group(2))
            yield os.path.join(basedir,dimsection,f'r.{regionx}.{regionz}.mca'), regionx, regionz

class InventoryCollection():
    inventories: list[Inventory]
    def __init__(self, inventories:list[Inventory]=[]):
        self.inventories=inventories.copy()
    
    def remove_farm_collection(self):
        self.inventories=[inv for inv in self.inventories if not inv.possible_farm_collection]
    
    def isolate_shulkerbox(self):
        new_inventories:list[Inventory]=[]
        for inv in self.inventories:
            for boxitem in inv.items.copy():
                if boxitem['id'].value.endswith('shulker_box'):
                    inv.items.remove(boxitem)
                    items=[]
                    if (comp:=boxitem.get('components')) and (cont:=comp.get('minecraft:container')):
                        for item in cont:
                            item['item']['Slot']=nbt.TAG_Byte(item['slot'].value)
                            items.append(item['item'])
                    new_inventories.append(Inventory(boxitem['id'].value, items, inv.pos, is_shulkerbox=True))
            if inv.items:
                new_inventories.append(inv)
        self.inventories = new_inventories
    
    def convert_to_chest(self, merge_singles, merge_singles_across_type):
        if not merge_singles:
            for inv in self.inventories:
                inv.container_type="minecraft:chest"
                inv.set_in_field=None
            return
        new_inventories:list[Inventory]=[inv for inv in self.inventories if not inv.is_single_slot]
        for inv in new_inventories:
            inv.container_type="minecraft:chest"
        single_containers:dict[str,list[Inventory]]={}
        for inv in self.inventories:
            if not inv.is_single_slot:
                continue
            typekey=inv.container_type if not merge_singles_across_type else ''
            if typekey not in single_containers:
                single_containers[typekey]=[]
            single_containers[typekey].append(inv)
        for inventories in single_containers.values():
            for slotid, inv in enumerate(inventories):
                inv.items[0]['Slot']=nbt.TAG_Byte(slotid%27)
            for batch in range(math.ceil(len(inventories)/27)):
                new_inventories.append(Inventory("minecraft:chest",[inv.items[0] for inv in inventories[batch*27:batch*27+27]],inventories[batch*27].pos))
        self.inventories=new_inventories
    
    def box_up(self, skip_mixed_containers, remove_empty_boxes):
        """
        make sure to isolate boxes before calling this method
        skip_mixed_containers: skip containers originally had boxes
        """
        new_inventories=[]
        pending_boxes=[]
        for inv in self.inventories:
            if skip_mixed_containers and inv.has_shulkerbox:
                new_inventories.append(inv)
                continue
            box_item=nbt.TAG_Compound()
            box_item['components']=nbt.TAG_Compound()
            container=nbt.TAG_List(nbt.TAG_Compound)
            if not inv.items:
                if not inv.container_type.endswith("shulker_box"):
                    warnings.warn(f'box_up: empty {inv.container_type} from pos {inv.pos}')
                elif remove_empty_boxes:
                    continue
            for item in inv.items:
                box_member=nbt.TAG_Compound()
                box_member['item']=item
                box_member['slot']=nbt.TAG_Int(item['Slot'].value)
                container.insert(len(box_member),box_member)
            box_item['components']['minecraft:container']=container
            box_item['count']=nbt.TAG_Int(1)
            if not inv.container_type.endswith("shulker_box"):
                box_item['id']=nbt.TAG_String("minecraft:shulker_box")
            else:
                box_item['id']=nbt.TAG_String(inv.container_type)
            pending_boxes.append(box_item)
        for slotid, box_item in enumerate(pending_boxes):
            box_item['Slot']=nbt.TAG_Byte(slotid%27)
        for batch in range(math.ceil(len(pending_boxes)/27)):
            new_inventories.append(Inventory('minecraft:chest', pending_boxes[batch*27:batch*27+27], [0,0,0]))
        self.inventories=new_inventories
    
    def get_nbt(self):
        structure_file=nbt.NBTFile()
        structure_file.name = "Item set"
        structure_file['DataVersion']=nbt.TAG_Int(4554)
        structure_file['size']=nbt.TAG_List(nbt.TAG_Int)
        structure_file['size'].append(nbt.TAG_Int(math.ceil(len(self.inventories)/32)))
        structure_file['size'].append(nbt.TAG_Int(1))
        structure_file['size'].append(nbt.TAG_Int(32))
        structure_file['palette']=nbt.TAG_List(nbt.TAG_Compound)
        block_dict={}
        for inv in self.inventories:
            blockid=inv.container_type
            if blockid not in block_dict:
                block_dict[blockid]=len(block_dict)
                blockstate=nbt.TAG_Compound()
                blockstate['Name']=nbt.TAG_String(blockid)
                structure_file['palette'].append(blockstate)
        structure_file['blocks']=nbt.TAG_List(nbt.TAG_Compound)
        for invid,inv in enumerate(self.inventories):
            block_data=nbt.TAG_Compound()
            block_data['state']=nbt.TAG_Int(block_dict[inv.container_type])
            block_data['pos']=nbt.TAG_List(nbt.TAG_Int)
            block_data['pos'].append(nbt.TAG_Int(invid//32))
            block_data['pos'].append(nbt.TAG_Int(0))
            block_data['pos'].append(nbt.TAG_Int(invid%32))
            block_data['nbt']=nbt.TAG_Compound()
            block_data['nbt']['id']=nbt.TAG_String(inv.container_type)
            block_data['nbt']['components']=nbt.TAG_Compound()
            if inv.set_in_field is None:
                block_data['nbt']['Items']=nbt.TAG_List(nbt.TAG_Compound)
                for item in inv.items:
                    block_data['nbt']['Items'].append(item)
            else:
                block_data['nbt'][inv.set_in_field]=item
            structure_file['blocks'].append(block_data)
        structure_file['entities']=nbt.TAG_List(nbt.TAG_Compound)
        return structure_file

parser = argparse.ArgumentParser(
    description='Extract inventory from blocks and entities in a specified minecraft world'
)
parser.add_argument('basedir', help='world directory')
parser.add_argument('output_file', help='output structure nbt file')
parser.add_argument('-ov',dest='overworld', action='store_true',help='include overworld')
parser.add_argument('-ne',dest='nether', action='store_true',help='include the nether')
parser.add_argument('-en',dest='end', action='store_true',help='include the end')
parser.add_argument('--remove-farms', action='store_true', help='remove containers that appear to be farm input or output (i.e. only contain a single item type, and be a multiple of 1728 or a full hopper/minecart/dropper/dispenser of it)')
parser.add_argument('--isolate-box', action='store_true', help='take shulker boxes out of containers, so they become independent containers')
parser.add_argument('--box-up', action='store_true', help='convert every container into a box.\nRequires --isolate-box')
parser.add_argument('--remove-empty-boxes', action='store_true', help='remove empty shulker boxes when putting boxes into chests.\nOnly matters if --box-up is set')
parser.add_argument('--no-box-mixed-chest', action='store_true', help='do not put content of a chest into a box, if a box was taken out of the chest.\nOnly matters if --box-up is set')
parser.add_argument('--as-chest', action='store_true', help='convert other containers to chests (should have no effect when --box-up is set)')
options = parser.parse_args()

inventories:List[Inventory]=[]

for region_file, regionx, regionz in iterate_regions(options.basedir, 'region', options.overworld, options.nether, options.end):
    region = Mca(region_file)
    for chunkz in range(regionz*32,regionz*32+32):
        for chunkx in range(regionx*32,regionx*32+32):
            nbt_data = region.get_data(chunkx,chunkz)
            if nbt_data is None:
                continue
            F=nbt.NBTFile(buffer=io.BytesIO(nbt_data))
            assert F.get('xPos').value==chunkx
            assert F.get('zPos').value==chunkz
            assert F.get('yPos').value in [-4, 0]
            if F.get('Status').value not in ['minecraft:full']:
                continue
            block_entities=F['block_entities']
            for block_entity in block_entities:
                pos=(block_entity['x'].value,block_entity['y'].value,block_entity['z'].value)
                if 'Items' in block_entity.keys():
                    if block_entity['Items']:
                        inventories.append(Inventory(block_entity['id'].value, list(block_entity['Items']), pos))
                if 'RecordItem' in block_entity.keys():
                    inventories.append(Inventory.create_single(block_entity['id'].value, block_entity['RecordItem'], pos, 'RecordItem'))
                if 'Book' in block_entity.keys():
                    inventories.append(Inventory.create_single(block_entity['id'].value, block_entity['Book'], pos, 'Book'))
                if 'item' in block_entity.keys():
                    inventories.append(Inventory.create_single(block_entity['id'].value, block_entity['item'], pos, 'item'))

for region_file, regionx, regionz in iterate_regions(options.basedir, 'entities', options.overworld, options.nether, options.end):
    region = Mca(region_file)
    for chunkz in range(regionz*32,regionz*32+32):
        for chunkx in range(regionx*32,regionx*32+32):
            nbt_data = region.get_data(chunkx,chunkz)
            if nbt_data is None:
                continue
            F=nbt.NBTFile(buffer=io.BytesIO(nbt_data))
            assert F.get('Position')[0]==chunkx
            assert F.get('Position')[1]==chunkz
            entities=F['Entities']
            while entities:
                entity=entities.pop()
                pos=(math.floor(entity['Pos'][0].value),math.floor(entity['Pos'][1].value),math.floor(entity['Pos'][2].value))
                if 'Passengers' in entity.keys():
                    entities.extend(entity['Passengers'])
                if 'Items' in entity.keys():
                    if entity['Items']:
                        inventories.append(Inventory("minecraft:chest", list(entity['Items']), pos))

# for inv in inventories:
#     if inv.single_item and len(inv.items)>1:
#         print(f'{inv.item_id:<30} {inv.item_count:5d}    ({inv.pos[0]:5d} {inv.pos[1]:5d} {inv.pos[2]:5d}) {inv.container_type}')

counter_1=count_items(inventories)
inventory_collection=InventoryCollection(inventories)
if options.remove_farms:
    inventory_collection.remove_farm_collection()
    counter_1=count_items(inventory_collection.inventories)
if options.as_chest:
    inventory_collection.convert_to_chest(True, False)
if options.isolate_box:
    inventory_collection.isolate_shulkerbox()
if options.box_up:
    inventory_collection.box_up(options.no_box_mixed_chest, options.remove_empty_boxes)
counter_2=count_items(inventory_collection.inventories)
if options.box_up and not options.remove_empty_boxes:
    assert not (counter_1-counter_2)
else:
    assert all([s.endswith('shulker_box') for s in (counter_1-counter_2).keys()])

Fout = inventory_collection.get_nbt()
Fout.write_file(options.output_file)

# block_size=100
# for batchid in range(math.ceil(len(inventory_collection.inventories)/block_size)):
#     Fout = InventoryCollection(inventory_collection.inventories[batchid*block_size:batchid*block_size+block_size]).get_nbt()
#     Fout.write_file(options.output_file.replace(".nbt",f"_{batchid:04d}.nbt"))
