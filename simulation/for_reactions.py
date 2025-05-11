import itertools
import random
import simpy
import scipy

RANDOM_SEED = 22
SIM_TIME = 100000
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
nbData = 0

NORMAL = True


def random_float(left, right) -> float:
    if NORMAL:
        mean = (right - left) / 2 + left
        deviation = (right - left) / 4  # 95%
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
    def __init__(self, env, execTime, execJitter):
        self.env = env
        self.core = simpy.Resource(env, 1)
        self.exec_range = (execTime - execJitter, execTime + execJitter)

    def execute(self):
        with self.core.request() as request:
            yield request
            yield self.env.timeout(random_float(*self.exec_range))


def schedule_sensor(env, arrTrace, name, sen, con, conTaskCount):
    print(f"Sensor's {name} starts executing at {env.now:.2f}.")
    arrTrace.append(("s.s", env.now))
    yield env.process(sen.execute())
    print(f"Sensor's {name} finishes executing at {env.now:.2f}.")
    arrTrace.append(("s.f", env.now))
    env.process(schedule_controller(env, arrTrace, f'task {next(conTaskCount)}', con))


def schedule_controller(env, arrTrace, name, con):
    print(f"Controller's {name} starts executing at {env.now:.2f}.")
    arrTrace.append(("c.s", env.now))
    yield env.process(con.execute())
    print(f"Controller's {name} finishes executing at {env.now:.2f}.")
    arrTrace.append(("c.f", env.now))
    global nbData
    nbData = nbData + 1


def schedule_actuator(env, arrTrace, name, act):
    print(f"Actuator's {name} starts executing at {env.now:.2f}.")
    global nbData
    # if nbData == 0:
    # arrTrace.append("USELESS_ACTUATION")
    if nbData != 0:
        nbData = 0
    arrTrace.append(("a.s", env.now))
    yield env.process(act.execute())
    print(f"Actuator's {name} finishes executing at {env.now:.2f}.")
    arrTrace.append(("a.f", env.now))


def sensorPeriodic(env, arrTrace, sen1ExecTime, sen1ExecJitter, sen1PeriodicTime, senPeriodicJitter, con1ExecTime,
                   con1ExecJitter, res):
    sen1 = TaskNoResource(env, sen1ExecTime, sen1ExecJitter)
    if res:
        con1 = TaskWithResource(env, con1ExecTime, con1ExecJitter)
    else:
        con1 = TaskNoResource(env, con1ExecTime, con1ExecJitter)
    sensorTaskCount = itertools.count()
    controllerTaskCount = itertools.count()
    while True:
        env.process(schedule_sensor(env, arrTrace, f'task {next(sensorTaskCount)}', sen1, con1, controllerTaskCount))
        yield env.timeout(random_float(sen1PeriodicTime - senPeriodicJitter, sen1PeriodicTime + senPeriodicJitter))


def actuatorPeriodic(env, arrTrace, act1ExecTime, act1ExecJitter, act1PeriodicTime, actPeriodicJitter):
    act1 = TaskNoResource(env, act1ExecTime, act1ExecJitter)
    actuatorTaskCount = itertools.count()
    while True:
        env.process(schedule_actuator(env, arrTrace, f'task {next(actuatorTaskCount)}', act1))
        yield env.timeout(random_float(act1PeriodicTime - actPeriodicJitter, act1PeriodicTime + actPeriodicJitter))


if __name__ == '__main__':
    for n in [True, False]:
        for res in [True, False]:
            NORMAL = n
            env = simpy.Environment()
            arrTrace = []
            env.process(
                sensorPeriodic(env, arrTrace, S1_EXEC_TIME, S1_EXEC_JITTER, S1_PERIODIC_TIME, S1_PERIODIC_JITTER,
                               C1_EXEC_TIME,
                               C1_EXEC_JITTER, res))
            env.process(
                actuatorPeriodic(env, arrTrace, A1_EXEC_TIME, A1_EXEC_JITTER, A1_PERIODIC_TIME, A1_PERIODIC_JITTER))
            env.run(until=SIM_TIME)

            tracename = "simpy"
            dist = "normal" if NORMAL else "uniform"
            res = "1res" if res else "nores"
            with open(f"{tracename}_{dist}_{res}.txt", "w") as output:
                for a, t in arrTrace:
                    output.write(f"{a} {t}\n")

    # info = ("SIM_TIME = "+str(SIM_TIME)+
    #         "\nRANDOM_SEED = "+str(RANDOM_SEED)+
    #         "\nS1_EXEC_TIME = "+str(S1_EXEC_TIME)+
    #         "\nS1_EXEC_JITTER = "+str(S1_EXEC_JITTER)+
    #         "\nS1_PERIODIC_TIME = "+str(S1_PERIODIC_TIME)+
    #         "\nS1_PERIODIC_JITTER = "+str(S1_PERIODIC_JITTER)+
    #         "\nC1_EXEC_TIME = "+str(C1_EXEC_TIME)+
    #         "\nC1_EXEC_JITTER = "+str(C1_EXEC_JITTER)+
    #         "\nA1_EXEC_TIME = "+str(A1_EXEC_TIME)+
    #         "\nA1_EXEC_JITTER = "+str(A1_EXEC_JITTER)+
    #         "\nA1_PERIODIC_TIME = "+str(A1_PERIODIC_TIME)+
    #         "\nA1_PERIODIC_JITTER = "+str(A1_PERIODIC_JITTER))
    # with open(tracename + "-info.txt", "w") as myfile:
    #     myfile.write(info)
