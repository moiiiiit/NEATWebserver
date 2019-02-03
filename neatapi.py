from __future__ import print_function
from neat.six_util import iteritems, itervalues
from json import JSONEncoder

import neat
import os
import random
import sys
#import StringIO
import json

class SingleGenPopulation:
	def __init__(self, numInputs, numOutputs, popSize):
		self.createNewPop(numInputs, numOutputs, popSize)
		self.dirtyNetworks = []

	def modifyConfig(self, nInput, nOutput, nPop):
		self.nInput = nInput
		self.nOutput = nOutput
		with open('config-feedforward') as configFile:
			with open('config-feedforwardNew', 'w') as newConfig:
				for line in configFile:
					if 'num_inputs' in line:
						newConfig.write('num_inputs=' + str(nInput) + '\n')
					elif 'num_outputs' in line:
						newConfig.write('num_outputs=' + str(nOutput) + '\n')
					elif 'pop_size' in line:
						newConfig.write('pop_size=' + str(nPop) + '\n')
					else:
						newConfig.write(line)
		configFile.close()

	def createNewPop(self, nInput, nOutput, nPop):
		self.modifyConfig(nInput, nOutput, nPop)
		# Load configuration.
		config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     'config-feedforwardNew')
		# Create the population, which is the top-level object for a NEAT run.
		self.p = neat.Population(config)

	def loadExistingPop(self, genomes, nInput, nOutput):
		createNewPop(nInput, nOutput, len(genomes))
		self.p.population = {}
		for genome in genomes:
			self.p.append()
		self.p.species = config.species_set_type(config.species_set_config, self.reporters)
		self.p.generation = 0
		self.p.species.speciate(config, self.population, self.generation)

	def mutate(self):
		self.p.population = self.p.reproduction.reproduce(self.p.config, self.p.species, self.p.config.pop_size, self.p.generation)
		
		# Check for complete extinction.
		if not self.p.species.species:
			self.p.reporters.complete_extinction()

			# If requested by the user, create a completely new population,
			# otherwise raise an exception.
			if self.p.config.reset_on_extinction:
				self.p.population = self.p.reproduction.create_new(self.p.config.genome_type,
															self.p.config.genome_config,
															self.p.config.pop_size)
			else:
				raise CompleteExtinctionException()
		# Divide the new population into species.
		self.p.species.speciate(self.p.config, self.p.population, self.p.generation)
		self.dirtyNetworks = []
		for genome_id, genome in list(iteritems(self.p.population)):
			genome.fitness = None

	def getPopulation(self, untestedNetworks):
		genomeLists = []
		networksRemaining = untestedNetworks
		for genome_id, genome in list(iteritems(self.p.population)):
			if ((networksRemaining > 0) and (genome.fitness is None) and not (genome_id in self.dirtyNetworks)):
				self.dirtyNetworks.append(genome_id)
				network = self.createSerializableGenome(genome)
				genomeLists.append(network)
				networksRemaining -= 1
		return json.dumps(genomeLists, cls=ComplexEncoder)

	def createGenome(self, nodeList, connectionList, key):
		g = genome(key)
		g.nodes = nodeList
		g.connections = connectionList
		return g

	def createSerializableGenome(self, genome):
		startNodes = StartNodes(self.nInput)
		endNodes = EndNodes(self.nOutput)
		connections = Connections(genome)
		allNodes = AllNodes(genome, connections.connections, self.nInput)
		return Network(startNodes, endNodes, connections.connections, allNodes, genome.key)

	def updateFitness(self, id, fitness):
		self.p.population[id].fitness = fitness

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)


class Network:
	def __init__(self, startNodes, endNodes, connections, allNodes, id):
		self.startNodes = startNodes
		self.endNodes = endNodes
		self.connections = connections
		self.allNodes = allNodes
		self.id = id
	def reprJSON(self):
		return self.__dict__

#list of all connections
class Connections:
	def __init__(self, genome):
		self.connections = []
		for connection in genome.connections:
			newsNode = connection[0]
			neweNode = connection[1]
			newWeight = genome.connections[connection].weight
			newEnabled = genome.connections[connection].enabled
			self.connections.append(Connection(newsNode, neweNode, newWeight, newEnabled))
	def reprJSON(self):
		print(self.connections)
		return self.__list__

class Connection:
	def __init__(self, sNode, eNode, weight, enabled):
		self.sNode = sNode
		self.eNode = eNode
		self.weight = weight
		self.enabled = enabled
	def reprJSON(self):
		return self.__dict__

#dictionary of all nodes
class AllNodes:
	def __init__(self, genome, connections, numInputs):
		self.nodes = {}
		for i in range(-numInputs, 0):
			self.nodes[i] = Node(i, 0, 0)
		for node in genome.nodes:
			self.nodes[node] = Node(node, 0, genome.nodes[node].bias)
		for connection in connections:
			self.nodes[connection.eNode].totalInputs += 1
	def reprJSON(self):
		return self.__dict__

#list of start node keys in the dictionary
class StartNodes:
	def __init__(self, numInputs):
		self.startNodeKeys = []
		for i in range(-numInputs, 0):
			self.startNodeKeys.append(i)
	def reprJSON(self):
		return self.__dict__


#list of end node keys in the dictionary
class EndNodes:
	def __init__(self, numOutputs):
		self.endNodeKeys = []
		for i in range(0, numOutputs):
			self.endNodeKeys.append(i)
	def reprJSON(self):
		return self.__dict__


class Node:
	def __init__(self, id, totalInputs, bias):
		self.id = id
		self.totalInputs = totalInputs
		self.bias = bias
	def __str__(self):
		return(str(self.id) + ' ' + str(self.bias))
	def reprJSON(self):
		return self.__dict__