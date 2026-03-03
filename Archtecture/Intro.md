This folder contains the design documents for the overall system. I figured it would be helpful to keep it here to keep everything in the same place.

Messages:
React Front End -> [slice API calls] -> Raspberry PI backend
    These messages Json content that represents the state of the sliced object as processed on the React frontend. Each point represents a verticy that will be connected to the next verticy using a straight line. All of the data regarding verticies is to be handled on the frontend and sent over to the backend for processing within print bed space. Processing which includes ArUco marker placement, line reconstruction and sending to 3D printer slicer (line data -> GCode)
    Should be formated as shown below:
    {
        "Verticy":[
            {"x":0, "y":0},
            {"x":1, "y":1},
            {"x":2, "y":2}
        ]
    }

    How the slicer converts into print bed size:
    1. First locate where all the vertices are. This is done by checking where all the lines end and recording them as vertices. Then we add the vertices for the points where the lines gets bisected by the print bed limits and convert the line into a smaller bisection.
    2. Form line with the vertices, we get 3 points (Includign the vertices on both ends) of the line and wrap that up into a 

    The alternative is to give the 
        