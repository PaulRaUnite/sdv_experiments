import itertools
import random
from functools import wraps
from typing import TextIO, Optional

import simpy
import scipy
from simpy import Event

RANDOM_SEED = 22
SIM_TIME = 100000

random.seed(RANDOM_SEED)
nbData = 0

NORMAL = True


def random_float(left, right) -> float:
    if left == right:
        return left
    if NORMAL:
        mean = (right - left) / 2 + left
        deviation = (right - left) / 4  # 95%
        dist = scipy.stats.truncnorm(
            (left - mean) / deviation, (right - mean) / deviation, loc=mean, scale=deviation)
        return dist.rvs()
    else:
        return random.uniform(left, right)


class Dist:
    def sample(self) -> float:
        pass


class NormalDist(Dist):
    def __init__(self, mean: float, deviation: float, bounds: tuple[float, float] | None):
        (lower, upper) = bounds
        assert lower > 0
        assert lower < upper
        self.mean = mean
        self.deviation = deviation
        self.bounds = bounds
        self.dist = scipy.stats.truncnorm(
            (lower - mean) / deviation, (upper - mean) / deviation, loc=mean, scale=deviation)

    @staticmethod
    def from_95_interval(left, right):
        mean = (right - left) / 2 + left
        deviation = (right - left) / 4  # 95%
        return NormalDist(mean, deviation, (left, right))

    @staticmethod
    def from_99_interval(left, right):
        mean = (right - left) / 2 + left
        deviation = (right - left) / 6  # 99.7%
        return NormalDist(mean, deviation, (left, right))

    def sample(self) -> float:
        return self.dist.rvs()


class UniformDist(Dist):
    def __init__(self, lower, upper):
        assert lower > 0
        assert lower < upper
        self.lower = lower
        self.upper = upper

    def sample(self) -> float:
        return random.uniform(self.lower, self.lower)

class NamedEvent(Event):
    def __init__(self, env: simpy.Environment, category: str, *namespace: str):
        super().__init__(env)
        self.category = category
        self.namespaces = namespace


class TaskNoResource:
    def __init__(self, env, name, exec_time: Dist):
        self.env = env
        self.exec_time = exec_time
        self.name = name

    def execute(self, instance: int):
        yield self.env.timeout(self.exec_time.sample())


class TaskWithResource:
    def __init__(self, env, cpu: simpy.Resource, name, exec_time: Dist):
        self.env = env
        self.cpu = cpu
        self.name = name
        self.exec_time = exec_time

    def execute(self, instance: int):
        with self.cpu.request() as request:
            yield request
            yield env.event()
            yield self.env.timeout(self.exec_time.sample())



class Monitor:
    def monitor(self, timestamp, event: Event):
        pass

class CADPMonitor:
    def __init__(self, file: TextIO):
        self.file = file

    def monitor(self, timestamp, event: NamedEvent):
        prefix = "_".join(event.namespaces)
        self.file.write(f"{prefix}_{event.category},".upper())


class MRTCCSLMonitor:
    def __init__(self, file: TextIO):
        self.file = file

    def monitor(self, timestamp, event: NamedEvent):
        prefix = ".".join(x[0] for x in event.namespaces)
        self.file.write(f"{prefix}.{event.category[0]} {timestamp}\n")


def env_monitor(env: simpy.Environment, monitor: Monitor) -> simpy.Environment:
    @wraps(env.step)
    def wrapper():
        if len(env._queue):
            t, prio, eid, event = env._queue[0]
            if isinstance(event, NamedEvent):
                monitor.monitor(t, event)
        return env.step()

    env.step = wrapper
    return env

def periodic_scheduler(env: simpy.Environment, offset: Dist, period: Dist, process_factory):
    count = 0
    yield env.timeout(offset.sample())
    while True:
        env.process(process_factory(count))
        count += 1
        yield env.timeout(period.sample())


def schedule_sensor(env, arrTrace, sen, con):
    # print(f"Sensor's {name} starts executing at {env.now:.2f}.")
    arrTrace.append(("s.s", "SENSOR_START", env.now))
    yield env.process(sen.execute())
    # print(f"Sensor's {name} finishes executing at {env.now:.2f}.")
    arrTrace.append(("s.f", "SENSOR_FINISH", env.now))
    env.process(schedule_controller(env, arrTrace, f'task {next(conTaskCount)}', con))


def schedule_controller(env, arrTrace, name, con):
    # print(f"Controller's {name} starts executing at {env.now:.2f}.")
    arrTrace.append(("c.s", "CONTROLLER_START", env.now))
    yield env.process(con.execute())
    # print(f"Controller's {name} finishes executing at {env.now:.2f}.")
    arrTrace.append(("c.f", "CONTROLLER_FINISH", env.now))
    global nbData
    nbData = nbData + 1


def schedule_actuator(env, arrTrace, name, act):
    # print(f"Actuator's {name} starts executing at {env.now:.2f}.")
    global nbData
    if nbData == 0:
        arrTrace.append(("a.s", "USELESS_ACTUATION", env.now))
    else:
        arrTrace.append(("a.s", "USEFUL_ACTUATION", env.now))
    nbData = 0
    yield env.process(act.execute())
    # print(f"Actuator's {name} finishes executing at {env.now:.2f}.")
    arrTrace.append(("a.f", "ACTUATOR_FINISH", env.now))


def sensorPeriodic(env, cpu, arrTrace, sen_exec_time, sen_exec_jitter, period, period_jitter, con1_exec_time,
                   con1_exec_jitter):
    sen1 = TaskWithResource(env, cpu, sen_exec_time, sen_exec_jitter)
    con1 = TaskWithResource(env, cpu, con1_exec_time, con1_exec_jitter)
    sensorTaskCount = itertools.count()
    controllerTaskCount = itertools.count()
    while True:
        env.process(schedule_sensor(env, arrTrace, f'task {next(sensorTaskCount)}', sen1, con1, controllerTaskCount))
        yield env.timeout(random_float(period - period_jitter, period + period_jitter))


def actuatorPeriodic(env, arrTrace, exec_time, exec_jitter, period, period_jitter):
    act1 = TaskWithResource(env, cpu, exec_time, exec_jitter)
    actuatorTaskCount = itertools.count()
    while True:
        env.process(schedule_actuator(env, arrTrace, f'task {next(actuatorTaskCount)}', act1))
        yield env.timeout(random_float(period - period_jitter, period + period_jitter))


if __name__ == '__main__':
    configurations = [
        # ("c1", 2, 0, 15, 0, 5, 0, 2, 1, 5, 0),
        ("c2", 2, 1, 15, 1, 5, 3, 2, 1, 5, 1),
        # ("c3", 2, 1, 15, 1, 5, 3, 2, 1, 15, 1),
        # ("c4", 2, 1, 5, 1, 5, 3, 2, 1, 15, 1),
        # ("c5", 2, 1, 15, 1, 3, 1, 2, 1, 5, 1),
    ]
    for (
            conf_name,
            S1_EXEC_TIME,
            S1_EXEC_JITTER,
            S1_PERIODIC_TIME,
            S1_PERIODIC_JITTER,
            C1_EXEC_TIME,
            C1_EXEC_JITTER,
            A1_EXEC_TIME,
            A1_EXEC_JITTER,
            A1_PERIODIC_TIME,
            A1_PERIODIC_JITTER) in configurations:
        for normal in [True]:
            for res in [16]:
                dist = "normal" if NORMAL else "uniform"
                print(f"started {conf_name}_{dist}_{res}cores.txt")

                NORMAL = normal
                nbData = 0

                env = simpy.Environment()
                cpu = simpy.Resource(env, res)
                arrTrace = []
                env.process(
                    actuatorPeriodic(env, arrTrace, A1_EXEC_TIME, A1_EXEC_JITTER, A1_PERIODIC_TIME, A1_PERIODIC_JITTER))
                env.process(
                    sensorPeriodic(env, cpu, arrTrace, S1_EXEC_TIME, S1_EXEC_JITTER, S1_PERIODIC_TIME,
                                   S1_PERIODIC_JITTER,
                                   C1_EXEC_TIME,
                                   C1_EXEC_JITTER))
                env.run(until=SIM_TIME)

                with open(f"{conf_name}_{dist}_{res}cores.txt", "w") as output1, open(
                        f"{conf_name}_{dist}_{res}cores.cadp.txt", "w") as output2:
                    delim = ""
                    for mrtccsl_action, cadp_action, t in arrTrace:
                        delim = ","
                        output1.write(f"{mrtccsl_action} {t}\n")
                        output2.write(f"{cadp_action}{delim}")

                info = ("SIM_TIME = " + str(SIM_TIME) +
                        "\nRANDOM_SEED = " + str(RANDOM_SEED) +
                        "\nS1_EXEC_TIME = " + str(S1_EXEC_TIME) +
                        "\nS1_EXEC_JITTER = " + str(S1_EXEC_JITTER) +
                        "\nS1_PERIODIC_TIME = " + str(S1_PERIODIC_TIME) +
                        "\nS1_PERIODIC_JITTER = " + str(S1_PERIODIC_JITTER) +
                        "\nC1_EXEC_TIME = " + str(C1_EXEC_TIME) +
                        "\nC1_EXEC_JITTER = " + str(C1_EXEC_JITTER) +
                        "\nA1_EXEC_TIME = " + str(A1_EXEC_TIME) +
                        "\nA1_EXEC_JITTER = " + str(A1_EXEC_JITTER) +
                        "\nA1_PERIODIC_TIME = " + str(A1_PERIODIC_TIME) +
                        "\nA1_PERIODIC_JITTER = " + str(A1_PERIODIC_JITTER))
                with open(f"{conf_name}_{dist}_{res}cores-info.txt", "w") as file:
                    file.write(info)
