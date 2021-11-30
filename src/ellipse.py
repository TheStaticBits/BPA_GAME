import src.follow_object

class Ellipse(src.follow_object.FollowObject):
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
            constants.ELLIPSE_FOLLOW_DISTANCE,
            constants.ELLIPSE_ANIMATIONS,
            (16, 16), 
            velocity
        )