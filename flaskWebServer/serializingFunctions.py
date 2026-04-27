# Convert list of coordinates in Json string format that can be packaged via jsonify
def serializeCoordinates(coordinates):
    return [{"x": float(coord[0]), "y": float(coord[1]), "rotation": float(coord[2])} for coord in coordinates]