import src.follow_object
import src.constants as constants

class Corlen(src.follow_object.FollowObject):
    def __init__(
        self, 
        startPos, 
        room, # Room the object is starting in 
        level, # Level the object is starting in
        velocity = 0
        ):
        super().__init__(
            startPos, 
            room, 
            level,
            constants.CORLEN_FOLLOW_DISTANCE,
            constants.CORLEN_ANIMATIONS,
            (16, 16), 
            velocity
        )