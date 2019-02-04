# NEATWebserver
# Python, Flask.
This project is a server side code to run an API that takes a 'GET' input of three parameters to create a new population of NEAT genomes.
These can then be downloaded by any number of client machines to test them with any sort of application that has to be trained with the NEAT algorithm.
The client machine downloads the genomes(GET), tests them on the application, POST the tested genomes back to server and download more untested genomes
Once all genomes are tested, the server evolves the population to make a new generation based on the successful genomes from the previous generation
The success is measured by a fitness function or value, which the client has to return to the server along with a tested genome using POST mentioned above.
Tested with Super Mario World running on a lua based simulator(EmuHawk)
