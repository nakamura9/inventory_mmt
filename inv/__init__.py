"""Application that is used to manage inventory items consisting of engineering equipment and production related resources such as raw materials and finished goods.
The engineering equipment is further subdivided into 5 levels of equipment:
    Machine
    Section(s)
    SubUnit(s)
    SubAssembly(s)
    Component(s)

Models
========
Machine 
Section
SubUnit
SubAssembly
Component
Order
Spares
InventoryItem
Asset

URLS
========
inventory-home
add_plant
engineering-inventory
raw-materials
new-category
inventory-list
inventory-details
new-inventory-item
spares-(details/create/update)
asset-(details/create/update)
(add/edit/delete)_component
component_details
(add/edit/delete)_machine
machine_details
(add/edit/delete)_subunit
subunit_details
(add/edit/delete)_machine
machine_details
(add/edit/delete)_subassembly
subassembly_details
(add/edit/delete)_section
section_details
order-(details/update/delete/list)
new-order


Forms
========
SparesForm
AssetForm
InventoryItemForm
OrderForm
MachineForm
SectionForm
SubUnitForm
SubAssyForm
ComponentForm
"""