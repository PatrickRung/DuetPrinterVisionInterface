This folder holds the client interface portion for mobiPrint continuos printing for
debugging and potentially slicing purposes. The software is essentially a lighter weight
version of the official Valetudo software but with some additional tools for our usecase.

.env should contains variables as followed (Should match .env for DuetVisionInterface top level folder):
NEXT_PUBLIC_API_KEY={put api key here}
NEXT_PUBLIC_IP_ADDRESS={put ip address here}

Duet specific functionality builds heavily off of the codebase mainly providing abstractions for MobiPrint specific
movement functions. Below is a list of modified or new files that help identify where these modificataions are located
These files below

GoToActionsMultiple.tsx
- GoToActionsMultiple has been modified to performed multiple consecutive go to locations based on a queue stored within it's
state, rather than the single point that it was originall programmed to use

### RobotPositionMapStrcuture is one of the most important file as it will also contain the const until I figure out a better place to put it
RobotPositionMapStrcuture.ts 
- Modified to display print space relative the Roborocks current orientation

CustomClient.ts
- Custom functions for Roborock specific movmenet such as:
    - Rotate to designated rotation