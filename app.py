import json

from flask import Flask,request
from neatapi import SingleGenPopulation
app = Flask(__name__)       #numInputs, numOutputs, populationSize

population1 = None     #class object?


@app.route('/new', methods=['GET'])
def new():
    global population1
    if request.method == "GET":
        numInputs = request.args.get('numInputs')
        numOutputs = request.args.get('numOutputs')
        populationSize = request.args.get('populationSize')
        population1 = SingleGenPopulation(int(numInputs), int(numOutputs), int(populationSize))
        return "success"

@app.route('/evolve', methods=['POST'])
def evolve():
    global population1
    if request.method == "POST":
        population1.mutate()
        return("evolved")

@app.route('/get/untested', methods=['GET'])
def untested():
    global population1
    if request.method == "GET":
        num = request.args.get('numGenomes')
        untestedData = population1.getPopulation(num)
        return untestedData
    
@app.route('/fit', methods=['POST'])
def fit():
    global population1
    if request.method == "POST":
        print(request.data)   
        genomes = request.get_json()  
        print(genomes)          #gets json
        print(genomes['networks'])
        for network in genomes['networks']:
            population1.updateFitness(network['id'], network['fitness'])
        return("success")

@app.route('/get/status', methods=['GET'])
def status():
    global population1
    if request.method == "GET":
        return("this is the status method")


# class FitList:
#     def __init__(self,):