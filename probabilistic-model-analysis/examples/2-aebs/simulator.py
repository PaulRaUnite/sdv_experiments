import itertools
import random
import simpy
import scipy
import os
import itertools

SIM_NUM = 1
SIM_TIME = 10000
camData = 0
lidData = 0
radData = 0
aebData = 0
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


def executor(env, arrTrace, name, number, task, periodicJitter, first):
    global camData
    global lidData
    global radData
    if first != True:
        yield env.timeout(random_float(0, periodicJitter * 2))
    arrTrace.append((name + ".s", name + "_START", env.now))
    yield env.process(task.execute())
    arrTrace.append((name + ".f", name + "_FINISH", env.now))
    if name == "Camera":
        camData = camData + 1
    if name == "Lidar":
        lidData = lidData + 1
    if name == "Radar":
        radData = radData + 1

def camera(env, cpu, arrTrace, off, periodicTime, periodicJitter, execTime, execJitter):
    cam = TaskWithResource(env, cpu, execTime, execJitter)
    camTaskCount = itertools.count()
    name = "Camera"
    number = f'task {next(camTaskCount)}'
    yield env.timeout(off)
    env.process(executor(env, arrTrace, name, number,  cam, periodicJitter, True))
    number = f'task {next(camTaskCount)}'
    yield env.timeout(periodicTime - periodicJitter)
    env.process(executor(env, arrTrace, name, number, cam, periodicJitter, False))
    while True:
        number = f'task {next(camTaskCount)}'
        yield env.timeout(periodicTime)
        env.process(executor(env, arrTrace, name, number, cam, periodicJitter, False))

def lidar(env, cpu, arrTrace, off, periodicTime, periodicJitter, execTime, execJitter):
    lid = TaskWithResource(env, cpu, execTime, execJitter)
    lidTaskCount = itertools.count()
    name = "Lidar"
    number = f'task {next(lidTaskCount)}'
    yield env.timeout(off)
    env.process(executor(env, arrTrace, name, number,  lid, periodicJitter, True))
    number = f'task {next(lidTaskCount)}'
    yield env.timeout(periodicTime - periodicJitter)
    env.process(executor(env, arrTrace, name, number, lid, periodicJitter, False))
    while True:
        number = f'task {next(lidTaskCount)}'
        yield env.timeout(periodicTime)
        env.process(executor(env, arrTrace, name, number, lid, periodicJitter, False))

def radar(env, cpu, arrTrace, off, periodicTime, periodicJitter, execTime, execJitter):
    rad = TaskWithResource(env, cpu, execTime, execJitter)
    radTaskCount = itertools.count()
    name = "Radar"
    number = f'task {next(radTaskCount)}'
    yield env.timeout(off)
    env.process(executor(env, arrTrace, name, number,  rad, periodicJitter, True))
    number = f'task {next(radTaskCount)}'
    yield env.timeout(periodicTime - periodicJitter)
    env.process(executor(env, arrTrace, name, number, rad, periodicJitter, False))
    while True:
        number = f'task {next(radTaskCount)}'
        yield env.timeout(periodicTime)
        env.process(executor(env, arrTrace, name, number, rad, periodicJitter, False))

def fusion_executor(env, arrTrace, name, number, task, periodicJitter, first, numberAeb, ae, numberAla, ala):
    global camData
    global lidData
    global radData
    useful = True
    if first != True:
        yield env.timeout(random_float(0, periodicJitter * 2))
    if camData == 0 and lidData == 0 and radData == 0:
        arrTrace.append((name + ".s", "Fusion_USELESS_PROCESS", env.now))
        useful = False
    else:
        arrTrace.append((name + ".s", "Fusion_USEFUL_PROCESS", env.now))
        camData = 0
        lidData = 0
        radData = 0
    yield env.process(task.execute())
    arrTrace.append((name + ".f", name + "_FINISH", env.now))
    if useful == True:
        env.process(aeb(env, arrTrace, numberAeb, ae, numberAla, ala))

def fusion(env, cpu, arrTrace, off, periodicTime, periodicJitter, execTime, execJitter, aebExecTime, aebExecJitter, alaExecTime, alaExecJitter):
    fus = TaskWithResource(env, cpu, execTime, execJitter)
    ae = TaskWithResource(env, cpu, aebExecTime, aebExecJitter)
    ala = TaskWithResource(env, cpu, alaExecTime, alaExecJitter)
    fusTaskCount = itertools.count()
    aebTaskCount = itertools.count()
    alaTaskCount = itertools.count()
    name = "Fusion"
    number = f'task {next(fusTaskCount)}'
    numberAeb = f'task {next(aebTaskCount)}'
    numberAla = f'task {next(alaTaskCount)}'
    yield env.timeout(off)
    env.process(fusion_executor(env, arrTrace, name, number,  fus, periodicJitter, True, numberAeb, ae, numberAla, ala))
    number = f'task {next(fusTaskCount)}'
    yield env.timeout(periodicTime - periodicJitter)
    env.process(fusion_executor(env, arrTrace, name, number, fus, periodicJitter, False, numberAeb, ae, numberAla, ala))
    while True:
        number = f'task {next(fusTaskCount)}'
        yield env.timeout(periodicTime)
        env.process(fusion_executor(env, arrTrace, name, number, fus, periodicJitter, False, numberAeb, ae, numberAla, ala))

def aeb(env, arrTrace, numberAeb, ae, numberAla, ala):
    global aebData
    arrTrace.append(("Controller.s", "Controller_START", env.now))
    yield env.process(ae.execute())
    arrTrace.append(("Controller.f", "Controller_FINISH", env.now))
    aebData = aebData + 1
    env.process(alarm(env, arrTrace, numberAla, ala))

def alarm(env, arrTrace, number, ala):
    arrTrace.append(("Alarm.s", "Alarm_START", env.now))
    yield env.process(ala.execute())
    arrTrace.append(("Alarm.f", "Alarm_FINISH", env.now))

def actuator(env, arrTrace, number, task, periodicJitter, first):
    global aebData
    if first != True:
        yield env.timeout(random_float(0, periodicJitter * 2))
    if aebData == 0:
        arrTrace.append(("Brake.s", "Brake_USELESS_ACTUATION", env.now))
    else:
        arrTrace.append(("Brake.s", "Brake_USEFUL_ACTUATION", env.now))
        aebData = 0
    yield env.process(task.execute())
    arrTrace.append(("Brake.f", "Brake_FINISH", env.now))

def brake(env, cpu, arrTrace, off, periodicTime, periodicJitter, execTime, execJitter):
    brake = TaskWithResource(env, cpu, execTime, execJitter)
    brakeTaskCount = itertools.count()
    number = f'task {next(brakeTaskCount)}'
    yield env.timeout(off)
    env.process(actuator(env, arrTrace, number,  brake, periodicJitter, True))
    number = f'task {next(brakeTaskCount)}'
    yield env.timeout(periodicTime - periodicJitter)
    env.process(actuator(env, arrTrace, number, brake, periodicJitter, False))
    while True:
        number = f'task {next(brakeTaskCount)}'
        yield env.timeout(periodicTime)
        env.process(actuator(env, arrTrace, number, brake, periodicJitter, False))


if __name__ == '__main__':
    components = "clrfb"
    orders = [''.join(p) for p in itertools.permutations(components)]

    configurations = [
        # ("C1", 0, 15, 1, 2, 1,
        #        0, 15, 1, 2, 1,
        #        0, 15, 1, 2, 1,
        #        0, 15, 1, 2, 1,
        #        8, 3,
        #        2, 1,
        #        0, 15, 1, 2, 1),
        ("C2", 0, 15, 1, 2, 1,
               0, 15, 1, 2, 1,
               0, 15, 1, 2, 1,
               0, 10, 1, 2, 1,
               3, 1,
               2, 1,
               0, 10, 1, 2, 1)
    ]
    
    directory_name = "configurations"
    for cft in configurations:
        try:
            os.mkdir(f"{directory_name}/{cft[0]}/trace")
            print(f"Directory '{directory_name}'/'{cft[0]}'/trace created successfully.")
        except FileExistsError:
            print(f"Directory '{directory_name}'/'{cft[0]}'/trace already exists.")

    seed = 0
    for sim in range(SIM_NUM):
        for order in orders:
            seed = seed + 1
            random.seed(seed)
            for (
                    conf_name,
                    SC_OFF, SC_SP, SC_SPJ, SC_DL, SC_DLJ,
                    SL_OFF, SL_SP, SL_SPJ, SL_DL, SL_DLJ,
                    SR_OFF, SR_SP, SR_SPJ, SR_DL, SR_DLJ,
                    CF_OFF, CF_PA, CF_PAJ, CF_ET, CF_ETJ,
                    CA_ET, CA_ETJ,
                    AA_AD, AA_ADJ,
                    AB_OFF, AB_AP, AB_APJ, AB_AD, AB_ADJ,
                    ) in configurations:
                for normal in [True]: 
                    for res in [16]:
                        NORMAL = normal
                        dist = "normal" if NORMAL else "uniform"
                        print(f"started {seed}_{conf_name}_{dist}_{res}cores.txt")
                        env = simpy.Environment()
                        arrTrace = []
                        cpu = simpy.Resource(env, res)
                        camData = 0
                        lidData = 0
                        radData = 0
                        aebData = 0
                        
                        for comp in order:
                            match comp:
                                case "c":
                                    env.process(camera(env, cpu, arrTrace, SC_OFF, SC_SP, SC_SPJ, SC_DL, SC_DLJ))
                                case "l":
                                    env.process(lidar(env, cpu, arrTrace, SL_OFF, SL_SP, SL_SPJ, SL_DL, SL_DLJ))
                                case "r":
                                    env.process(radar(env, cpu, arrTrace, SR_OFF, SR_SP, SR_SPJ, SR_DL, SR_DLJ))
                                case "f":
                                    env.process(fusion(env, cpu, arrTrace, CF_OFF, CF_PA, CF_PAJ, CF_ET, CF_ETJ, CA_ET, CA_ETJ, AA_AD, AA_ADJ))
                                case "b":
                                    env.process(brake(env, cpu, arrTrace, AB_OFF, AB_AP, AB_APJ, AB_AD, AB_ADJ))
                        
                        env.run(until=SIM_TIME)
                        
                        with open(f"configurations/{conf_name}/trace/T{seed}.txt", "w") as output2:
                            delim = ""
                            prevTime = 0
                            for mrtccsl_action, cadp_action, t in arrTrace:
                                timedif = int(round(t, 0)) - prevTime
                                prevTime = int(round(t, 0))
                                output2.write(f"{delim}{cadp_action} {timedif}")
                                delim = ","
