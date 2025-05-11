import itertools
import random
import simpy
import sys
RANDOM_SEED = 22
SIM_TIME = 1000000
S1_EXEC_TIME = 2
S1_EXEC_JITTER = 1
S1_PERIODIC_TIME = 15
S1_PERIODIC_JITTER = 1
C1_EXEC_TIME = 5
C1_EXEC_JITTER = 3
A1_EXEC_TIME = 2
A1_EXEC_JITTER = 1
A1_PERIODIC_TIME = 5
A1_PERIODIC_JITTER = 1

random.seed(RANDOM_SEED)
tracename = sys.argv[1]
nbData=0

class Sensor:
    def __init__(self, env, execTime, execJitter):
        self.env = env
        self.execTime = execTime
        self.execJitter = execJitter
    def execute(self):
        yield self.env.timeout(random.randint(self.execTime - self.execJitter, self.execTime + self.execJitter))
        
class Controller:
    def __init__(self, env, execTime, execJitter):
        self.env = env
        self.core = simpy.Resource(env, 1)
        self.execTime = execTime
        self.execJitter = execJitter
    def execute(self):
        yield self.env.timeout(random.randint(self.execTime - self.execJitter, self.execTime + self.execJitter))

class Actuator:
    def __init__(self, env, execTime, execJitter):
        self.env = env
        self.execTime = execTime
        self.execJitter = execJitter
    def execute(self):
        yield self.env.timeout(random.randint(self.execTime - self.execJitter, self.execTime + self.execJitter))

def sensorTask(env, arrTrace, name, sen, con, conTaskCount):
    print(f"Sensor's {name} starts executing at {env.now:.2f}.")
    arrTrace.append("SENSOR_START")
    yield env.process(sen.execute())
    print(f"Sensor's {name} finishes executing at {env.now:.2f}.")
    arrTrace.append("SENSOR_FINISH")
    env.process(controllerTask(env, arrTrace, f'task {next(conTaskCount)}', con))

def controllerTask(env, arrTrace, name, con):
    with con.core.request() as request:
        yield request
        print(f"Controller's {name} starts executing at {env.now:.2f}.")
        arrTrace.append("CONTROLLER_START")
        yield env.process(con.execute())
        print(f"Controller's {name} finishes executing at {env.now:.2f}.")
        arrTrace.append("CONTROLLER_FINISH")
        global nbData
        nbData = nbData + 1

def actuatorTask(env, arrTrace, name, act):
    print(f"Actuator's {name} starts executing at {env.now:.2f}.")
    global nbData
    if nbData == 0:
        arrTrace.append("USELESS_ACTUATION")
    else:
        nbData = 0
        arrTrace.append("USEFUL_ACTUATION")
    yield env.process(act.execute())
    print(f"Actuator's {name} finishes executing at {env.now:.2f}.")
    arrTrace.append("ACTUATOR_FINISH")

def sensorPeriodic(env, arrTrace, sen1ExecTime, sen1ExecJitter, sen1PeriodicTime, senPeriodicJitter, con1ExecTime, con1ExecJitter):
    sen1 = Sensor(env, sen1ExecTime, sen1ExecJitter)
    con1 = Controller(env, con1ExecTime, con1ExecJitter)
    sensorTaskCount = itertools.count()
    controllerTaskCount = itertools.count()
    env.process(sensorTask(env, arrTrace, f'task {next(sensorTaskCount)}', sen1, con1, controllerTaskCount))
    while True:
        yield env.timeout(random.randint(sen1PeriodicTime - senPeriodicJitter, sen1PeriodicTime + senPeriodicJitter))
        env.process(sensorTask(env, arrTrace, f'task {next(sensorTaskCount)}', sen1, con1, controllerTaskCount))

def actuatorPeriodic(env, arrTrace, act1ExecTime, act1ExecJitter, act1PeriodicTime, actPeriodicJitter):
    act1 = Actuator(env, act1ExecTime, act1ExecJitter)
    actuatorTaskCount = itertools.count()
    env.process(actuatorTask(env, arrTrace, f'task {next(actuatorTaskCount)}', act1))
    while True:
        yield env.timeout(random.randint(act1PeriodicTime - actPeriodicJitter, act1PeriodicTime + actPeriodicJitter))
        env.process(actuatorTask(env, arrTrace, f'task {next(actuatorTaskCount)}', act1))

env = simpy.Environment()
arrTrace=[]
env.process(sensorPeriodic(env, arrTrace, S1_EXEC_TIME, S1_EXEC_JITTER, S1_PERIODIC_TIME, S1_PERIODIC_JITTER, C1_EXEC_TIME, C1_EXEC_JITTER))
env.process(actuatorPeriodic(env, arrTrace, A1_EXEC_TIME, A1_EXEC_JITTER, A1_PERIODIC_TIME, A1_PERIODIC_JITTER))
env.run(until=SIM_TIME)

with open(tracename + ".txt", "w") as myfile:
    myfile.write("")
delimit=""
for t in arrTrace:
    with open(tracename + ".txt", "a") as myfile:
        myfile.write(delimit + t)
        delimit=","

info = ("SIM_TIME = "+str(SIM_TIME)+
        "\nRANDOM_SEED = "+str(RANDOM_SEED)+
        "\nS1_EXEC_TIME = "+str(S1_EXEC_TIME)+
        "\nS1_EXEC_JITTER = "+str(S1_EXEC_JITTER)+
        "\nS1_PERIODIC_TIME = "+str(S1_PERIODIC_TIME)+
        "\nS1_PERIODIC_JITTER = "+str(S1_PERIODIC_JITTER)+
        "\nC1_EXEC_TIME = "+str(C1_EXEC_TIME)+
        "\nC1_EXEC_JITTER = "+str(C1_EXEC_JITTER)+
        "\nA1_EXEC_TIME = "+str(A1_EXEC_TIME)+
        "\nA1_EXEC_JITTER = "+str(A1_EXEC_JITTER)+
        "\nA1_PERIODIC_TIME = "+str(A1_PERIODIC_TIME)+
        "\nA1_PERIODIC_JITTER = "+str(A1_PERIODIC_JITTER))
with open(tracename + "-info.txt", "w") as myfile:
    myfile.write(info)
