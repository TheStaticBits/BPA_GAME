import src.follow_object
import src.constants as constants

def create_entity(entity, startPos, room, level, velocity = 0) -> "src.follow_object.FollowObject":
    """Creates a follow object with the default Corlen or Ellipse data"""
    if entity == "ellipse":
        followDist = constants.ELLIPSE_FOLLOW_DISTANCE
        anim = constants.ELLIPSE_ANIMATIONS
    
    elif entity == "corlen":
        followDist = constants.CORLEN_FOLLOW_DISTANCE
        anim = constants.CORLEN_ANIMATIONS

    return src.follow_object.FollowObject(startPos, room, level, followDist, anim, constants.TILE_SIZE, velocity)