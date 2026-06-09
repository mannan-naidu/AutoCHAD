from pydantic import BaseModel, Field
from typing import List, Dict

class GeometrySchema(BaseModel):
    shape: str = Field(default="cylindrical")
    bottom: str = Field(default="dished")
    top: str = Field(default="dished")

class DimensionsSchema(BaseModel):
    height: float = Field(default=1000.0)
    diameter: float = Field(default=500.0)

class EquipmentSchema(BaseModel):
    type: str = Field(default="process_system")
    capacity: float = Field(default=0.0)
    geometry: GeometrySchema = Field(default_factory=GeometrySchema)
    dimensions: DimensionsSchema = Field(default_factory=DimensionsSchema)

class NozzleSchema(BaseModel):
    id: str
    type: str
    connection: str = "TC"
    angle: float = 0.0
    height: float = 0.0

class PortSchema(BaseModel):
    """
    Named connection point on a piece of equipment.
    side: top | bottom | left | right
    purpose: process | utility | instrument | safety
    """
    id: str
    side: str = "right"
    purpose: str = "process"

class NodeSchema(BaseModel):
    id: str
    type: str = Field(description="tank | pump | valve | sensor | spray_ball | filter | relief_valve | vent")
    role: str = "process"   # source | process | control | instrument | utility | safety | sink
    ports: List[PortSchema] = Field(default_factory=list)
    attributes: Dict = Field(default_factory=dict)

class EdgeSchema(BaseModel):
    from_id: str
    to_id: str
    from_port: str = "default_out"   # named port on from_id node
    to_port: str = "default_in"      # named port on to_id node
    type: str = "pipe"
    relation: str = "inline"         # inline | branch | drain | utility | instrument | loop
    medium: str = "product"          # product | water | steam | air

class EngineeringSchema(BaseModel):
    equipment: EquipmentSchema = Field(default_factory=EquipmentSchema)
    nozzles: List[NozzleSchema] = Field(default_factory=list)
    material: str = "SS316L"
    nodes: List[NodeSchema] = Field(default_factory=list)
    edges: List[EdgeSchema] = Field(default_factory=list)
    attributes: Dict = Field(default_factory=dict)
