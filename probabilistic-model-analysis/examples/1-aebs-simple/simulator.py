import itertools
import random
import simpy
import scipy
import os
import itertools
import math

SIM_NUM = 10
SIM_TIME = 1000
controllerData = 0
NORMAL = True

def random_float(left, right):
    if left == right:
        return left
    if NORMAL:
        mean = (right - left) / 2 + left
        deviation = (right - left) / 4 
        dist = scipy.stats.truncnorm(
            (left - mean) / deviation, (right - mean) / deviation, loc=mean, scale=deviation)
        return dist.rvs()
    else:
        return random.uniform(left, right)

class TaskNoResource:
    def __init__(self, env, execTime, execJitter):
        self.env = env
        self.exec_range = (execTime - execJitter, execTime + execJitter)

    def execute(self):
        yield self.env.timeout(random_float(*self.exec_range))

class TaskWithResource:
    def __init__(self, env, cpu, execTime, execJitter):
        self.env = env
        self.cpu = cpu
        self.exec_range = (execTime - execJitter, execTime + execJitter)

    def execute(self):
        with self.cpu.request() as request:
            yield request
            yield self.env.timeout(random_float(*self.exec_range))


def executor(env, arrTrace, task, periodicJitter, first, cont):
    if first != True:
        yield env.timeout(random_float(0, periodicJitter * 2))
    arrTrace.append(("Sensor.s", "S_START", env.now))
    yield env.process(task.execute())
    arrTrace.append(("Sensor.f", "S_FINISH", env.now))
    env.process(controller(env, arrTrace, cont))

def sensor(env, cpu, arrTrace, off, periodicTime, periodicJitter, execTime, execJitter, controllerExec, controllerExecJitter):
    sens = TaskWithResource(env, cpu, execTime, execJitter)
    controller = TaskWithResource(env, cpu, controllerExec, controllerExecJitter)
    yield env.timeout(off)
    env.process(executor(env, arrTrace,  sens, periodicJitter, True, controller))
    yield env.timeout(periodicTime - periodicJitter)
    env.process(executor(env, arrTrace, sens, periodicJitter, False, controller))
    while True:
        yield env.timeout(periodicTime)
        env.process(executor(env, arrTrace, sens, periodicJitter, False, controller))

def controller(env, arrTrace, cont):
    global controllerData
    arrTrace.append(("Controller.s", "C_START", env.now))
    yield env.process(cont.execute())
    arrTrace.append(("Controller.f", "C_FINISH", env.now))
    controllerData = controllerData + 1

def actuatorExec(env, arrTrace, task, periodicJitter, first):
    global controllerData
    if first != True:
        yield env.timeout(random_float(0, periodicJitter * 2))
    if controllerData == 0:
        arrTrace.append(("Actuator.s", "USELESS_ACT", env.now))
    else:
        arrTrace.append(("Actuator.s", "USEFUL_ACT", env.now))
        controllerData = 0
    yield env.process(task.execute())
    arrTrace.append(("Actuator.f", "A_FINISH", env.now))

def actuator(env, cpu, arrTrace, off, periodicTime, periodicJitter, execTime, execJitter):
    actuator = TaskWithResource(env, cpu, execTime, execJitter)
    yield env.timeout(off)
    env.process(actuatorExec(env, arrTrace,  actuator, periodicJitter, True))
    yield env.timeout(periodicTime - periodicJitter)
    env.process(actuatorExec(env, arrTrace, actuator, periodicJitter, False))
    while True:
        yield env.timeout(periodicTime)
        env.process(actuatorExec(env, arrTrace, actuator, periodicJitter, False))


if __name__ == '__main__':
    components = "sa"
    orders = [''.join(p) for p in itertools.permutations(components)]

    configurations = [
        ("C1", 0, 15, 1, 2, 1,
               5, 3,
               0, 15, 1, 2, 1),
        ("C2", 0, 15, 1, 2, 1,
               5, 3,
               0, 5, 1, 2, 1),
        ("C3", 0, 15, 1, 2, 1,
               3, 1,
               0, 15, 1, 2, 1),
        ("C4", 0, 15, 1, 2, 1,
               3, 1,
               0, 5, 1, 2, 1)
    ]
    
    directory_name = "configurations"
    for cft in configurations:
        try:
            os.mkdir(f"{directory_name}/{cft[0]}/trace")
            print(f"Directory '{directory_name}/'{cft[0]}'/trace created successfully.")
        except FileExistsError:
            print(f"Directory '{directory_name}'/'{cft[0]}'/trace already exists.")

    seed = 0
    for sim in range(SIM_NUM):
        for order in orders:
            seed = seed + 1
            random.seed(seed)
            for (
                    conf_name,
                    S_OFF, S_PERIODIC, S_PERIODIC_JITTER, S_DELAY, S_DELAY_JITTER,
                    C_EXEC, C_EXEC_JITTER,
                    A_OFF, A_PERIODIC, A_PERIODIC_JITTER, A_PROCESS, A_PROCESS_JITTER,
                    ) in configurations:
                for normal in [True]: 
                    for res in [16]:
                        NORMAL = normal
                        dist = "normal" if NORMAL else "uniform"
                        print(f"started {seed}_{conf_name}_{dist}_{res}cores")
                        env = simpy.Environment()
                        arrTrace = []
                        cpu = simpy.Resource(env, res)
                        controllerData = 0
                        
                        for comp in order:
                            match comp:
                                case "s":
                                    env.process(sensor(env, cpu, arrTrace, S_OFF, S_PERIODIC, S_PERIODIC_JITTER, S_DELAY, S_DELAY_JITTER, C_EXEC, C_EXEC_JITTER))
                                case "a":
                                    env.process(actuator(env, cpu, arrTrace, A_OFF, A_PERIODIC, A_PERIODIC_JITTER, A_PROCESS, A_PROCESS_JITTER))
                        
                        env.run(until=SIM_TIME)
                        
                        with open(f"configurations/{conf_name}/trace/T{seed}.txt", "w") as output2:
                            delim = ""
                            prevTime = 0
                            for mrtccsl_action, cadp_action, t in arrTrace:
                                timedif = int(round(t, 0)) - prevTime
                                prevTime = int(round(t, 0))
                                output2.write(f"{delim}{cadp_action} {timedif}")
                                delim = ","
