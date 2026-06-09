from models.schema import EngineeringSchema
import math

class NozzleEngine:
    @staticmethod
    def compute_nozzle_positions(schema: EngineeringSchema, center_x: float, center_y: float) -> list:
        """
        Computes the Cartesian coordinates for nozzles on the TOP VIEW.
        Input angles are in degrees. 0 degrees = right side (3 o'clock).
        """
        radius = schema.equipment.dimensions.diameter / 2
        positions = []
        
        for nozzle in schema.nozzles:
            rad = math.radians(nozzle.angle)
            nx = center_x + radius * math.cos(rad)
            ny = center_y + radius * math.sin(rad)
            
            positions.append({
                "nozzle": nozzle,
                "x": nx,
                "y": ny
            })
            
        return positions
