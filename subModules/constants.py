# File containing tunable parameters/ constants for use in other scripts

class constants:

    CAMERA_ARUCO_RECOGNIZING_RANGE = 60     # Approximate range of view from the furthest left
                                            # the roborock cam can recognize a aruco marker to
                                            # the furthest right.

    CAMERA_RANGE_LIMIT_ARUCO_DISTANCE = 10  # Approximate distance that the roborock needs to
                                            # move forward after the aruco marker is the closest
                                            # it can be to the roborock
                                            # This distance is used for when the roborock approaches
                                            # the aruco marker and needs to estimate how much further
                                            # to travel to be over the aruco marker