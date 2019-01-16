from simplejson import load
from random import randint  # i trust the "random" module to be random.
from matplotlib import pyplot as plt


def readbenchmarks(filename="benchmarks.txt"):
    file = open(filename, "r")
    data = load(file)
    file.close()
    return data  # list of dicts. 1 dict is the benchmark for 1 file.


def samplevalues(benchmark):  # "ziehen mit zuruecklegen"
    rawvals = benchmark["raw values"]
    size = benchmark["# of repeats"]
    samples = []
    for i in range(size):
        randomnumber = randint(0, len(rawvals) - 1)
        sample = rawvals[randomnumber]
        samples.append(sample)
    return samples


def samplemean(benchmark):  # "ziehen mit zuruecklegen" + mittelwert
    samples = samplevalues(benchmark)
    return mean(samples)


def mean(iterable):
    return float(sum(iterable)) / len(iterable)


def standarddeviation(iterable):
    samplemean = mean(iterable)
    samplelen = len(iterable)
    zaehler = sum([(sample - samplemean)**2 for sample in iterable])
    nenner = samplelen-1
    return float(zaehler)/nenner  # formula for sample standard deviation


def confidentinterval(iterable, percentage):
    sortedlist = iterable[:]  # dont want to mess up the actual list
    sortedlist.sort()
    index = int(float(percentage)/100 * len(sortedlist))+1
    return sortedlist[index]


def analyzebenchmark(benchmark, bignumber, debug=False):
    resamples = []
    for i in range(bignumber):
        resample = samplemean(benchmark)
        resamples.append(resample)
        if debug and i % (bignumber / 5) == 0:
            print(str(i)+" means computed")
    resamplemean = mean(resamples)
    std = standarddeviation(resamples)
    confident5 = confidentinterval(resamples, 5)
    confident95 = confidentinterval(resamples, 95)
    return (resamplemean, std, confident5, confident95)


def analyzebenchmarks(filename="benchmarks.txt", bignumber=50000):
    data = readbenchmarks()
    outputfile = open(filename + "_analysis", "w")
    for benchmark in data:
        analysis = analyzebenchmark(benchmark, bignumber)
        outputfile.write("Name : "+benchmark["Name"]+"\n")
        outputfile.write("Used Pattern : "+benchmark["Used Pattern"]+"\n")
        outputfile.write("Used Input : "+benchmark["Used Input"]+"\n")
        outputfile.write("Mean : " + str(analysis[0])+"\n")
        outputfile.write("Standard Deviation : " + str(analysis[1])+"\n")
        outputfile.write("5% Confident Interval:" + str(analysis[2])+"\n")
        outputfile.write("95% Confident Interval:" + str(analysis[3])+"\n\n")
        print(benchmark["Name"] + " analyzed with pattern "
              + benchmark["Used Pattern"])
    outputfile.close()


def plotraw():
    data = readbenchmarks()
    benchmark = data[0]
    rawvals = benchmark["raw values"]
    wtf = plt.hist(rawvals, 100)
    plt.show()


def plotsamples(bignumber=50000):
    data = readbenchmarks()
    benchmark = data[0]
    xvals = []
    for i in range(bignumber):
        x = samplemean(benchmark)
        xvals.append(x)
        if i % (bignumber/10) == 0:
            print(str(i)+" means computed.")
    wtf = plt.hist(xvals, 100)
    plt.grid(True)
    plt.show()
analyzebenchmarks()
