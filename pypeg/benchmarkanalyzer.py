from json import load
from random import randint  # i trust the "random" module to be random.
import sys


def readbenchmarks(filename):
    with open(filename, "r") as file:
        data = load(file)
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


def geo_mean(iterable):
    prod = 1.0
    for x in iterable:
        prod *= x
    return prod ** (1.0 / len(iterable))


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
    data = readbenchmarks(filename)
    outputfile = open(filename + "_analysis", "w")
    luaspeeddict = {}  # speed of lua file to compare pypeg to
    postanalysis = {}  # dict of lists of speedups
    #to build geometric mean of speedups for each file
    for benchmark in data:
        if benchmark["Name"] == "LUAFILE":
            analysis = analyzebenchmark(benchmark, bignumber)
            writeanalysis(outputfile, benchmark, analysis)
            luaspeeddict[benchmark["Used Input"]] = analysis[0]
            print(benchmark["Name"] + " analyzed with pattern "
                  + benchmark["Used Pattern"])
            #^touple of used inputfile (to identify benchmark) and mean value
    for benchmark in data:  # 2nd loop, this time only catching pypeg
        if benchmark["Name"] != "LUAFILE":
            if benchmark["Name"] not in postanalysis.keys():
                postanalysis[benchmark["Name"]] = []
            analysis = analyzebenchmark(benchmark, bignumber)
            if benchmark["Used Input"] in luaspeeddict.keys():
                luaspeed = luaspeeddict[benchmark["Used Input"]]
                pypegspeed = analysis[0]
                speedup = pypegspeed/luaspeed
                postanalysis[benchmark["Name"]].append(speedup)
            else:
                speedup = "Not Availabe"
            writeanalysis(outputfile, benchmark, analysis, is_lua=False,
                          speedup=speedup)
            print(benchmark["Name"] + " analyzed with pattern "
                  + benchmark["Used Pattern"])
    outputfile.close()
    postanalyze(filename, postanalysis)


def writeanalysis(outputfile, benchmark, analysis, is_lua=True, speedup=0):
    outputfile.write("Name : "+benchmark["Name"]+"\n")
    outputfile.write("Used Pattern : "+benchmark["Used Pattern"]+"\n")
    outputfile.write("Used Input : "+benchmark["Used Input"]+"\n")
    if not is_lua:
        outputfile.write("Speed relative to lua : " + str(speedup)+"\n")
    outputfile.write("Mean : " + str(analysis[0])+"\n")
    outputfile.write("Standard Deviation : " + str(analysis[1])+"\n")
    outputfile.write("5% Confident Interval:" + str(analysis[2])+"\n")
    outputfile.write("95% Confident Interval:" + str(analysis[3])+"\n\n")


def postanalyze(filename="benchmarks.txt", postanalysis={}):
    filename = filename + "_analysis"
    text = open(filename, "r").read()
    outputfile = open(filename, "w")
    for pypeg in postanalysis.keys():
        outputfile.write("Average Speedup of "+pypeg+" relative to lua : "
                         + str(geo_mean(postanalysis[pypeg])) + "\n")
    outputfile.write(text)
    outputfile.close()


def plotsamples(bignumber=20000):
    from matplotlib import pyplot as plt
    data = readbenchmarks("benchmarks.txt")
    for j in range(2):
        benchmark = data[j]
        xvals = []
        for i in range(bignumber):
            x = samplemean(benchmark)
            xvals.append(x)
            if i % (bignumber/10) == 0:
                print(str(i) + " means computed.")
        mycolor = "blue"
        if j > 0:
            mycolor = "red"
        wtf = plt.hist(xvals, 100, histtype="step", color=mycolor)
        plt.grid(False)
    plt.show()

def boxplot(datasets, labels, colors):
    from pylab import (plot, show, savefig, xlim, figure,
                       hold, ylim, legend, boxplot, setp, axes)

    from matplotlib.patches import Rectangle
    from matplotlib import pyplot as plt
    def setBoxColors(bp):
        for i in range(len(datasets)):
            setp(bp["boxes"][i], color=colors[i])
            setp(bp["caps"][2*i], color=colors[i])
            setp(bp["caps"][2*i+1], color=colors[i])
            setp(bp["whiskers"][2*i], color=colors[i])
            setp(bp["whiskers"][2*i+1], color=colors[i])
            setp(bp["fliers"][2*i], color=colors[i])
            setp(bp["fliers"][2*i+1], color=colors[i])
            setp(bp["medians"][i], color=colors[i])
    fig = figure()
    ax = axes()
    hold(True)
    bp = boxplot(datasets, positions=range(1,len(datasets)+1),
                 widths=0.6,vert=False)
    setBoxColors(bp)
    myhandles, mylabels=[],[]
    for i in range(len(labels)):
        myhandles.append(Rectangle((0, 0), 1, 1,
                       color=colors[i], ec="k"))
        mylabels.append(labels[i])
    plt.legend(myhandles, mylabels)
    show()
    #return bp()
def plotinput(bignumber=20000, input="500_kb_urlinput", show=True, plottype="boxplot"):
    from matplotlib import pyplot as plt
    from matplotlib.patches import Rectangle
    colors = ["red", "blue", "green", "purple", "black", "orange", "brown"]
    data = readbenchmarks("benchmarks.txt")
    c = 0
    handles = []
    labels = []
    for benchmark in data:
        if benchmark["Used Input"] == input:
            handles.append(Rectangle((0, 0), 1, 1, color=colors[c], ec="k"))
            labels.append(benchmark["Name"])
            xvals = []
            for i in range(bignumber):
                x = samplemean(benchmark)
                xvals.append(x)
                if i % (bignumber / 10) == 0:
                    print(str(i)+" means computed.")
            if plottype == "boxplot":
                wtf = plt.boxplot(xvals)
            else:
                wtf = plt.hist(xvals, 100, histtype="step", color=colors[c])
            plt.grid(False)
            c += 1
    ax = plt.gca()
    top = ax.get_ylim()[1]
    right = ax.get_xlim()[1]
    ax.set_ylim(bottom=0, top=top)
    ax.set_xlim(left=0, right=right)
    plt.legend(handles, labels)
    plt.title("Sampled means for "+input)
    plt.savefig("./plots/plot_"+input+".png")
    plt.figure()
    if show:
        plt.show()

def plotraw(input="500_kb_urlinput", show=True):
    from matplotlib import pyplot as plt
    from matplotlib.patches import Rectangle
    colors = ["red", "blue", "green", "purple", "black", "orange", "brown"]
    data = readbenchmarks("benchmarks.txt")
    c = 0
    handles = []
    labels = []
    for benchmark in data:
        if benchmark["Used Input"] == input:
            handles.append(Rectangle((0, 0), 1, 1, color=colors[c], ec="k"))
            labels.append(benchmark["Name"])
            xvals = benchmark["raw values"]
            wtf = plt.hist(xvals, 50, histtype="step", color=colors[c])
            plt.grid(False)
            c += 1
    ax = plt.gca()
    top = ax.get_ylim()[1]
    right = ax.get_xlim()[1]
    ax.set_ylim(bottom=0, top=top)
    ax.set_xlim(left=0, right=right)
    plt.legend(handles, labels)
    plt.title("Raw values for "+input)
    plt.savefig("./plots/rawplot_"+input+".png")
    plt.figure()
    if show:
        plt.show()
def plotall(raw=False):
    inputs = []
    data = readbenchmarks("benchmarks.txt")
    for benchmark in data:
        input = benchmark["Used Input"]
        if input not in inputs:
            inputs.append(input)
    for input in inputs:
        print("Calculating plot for "+input)
        if raw:
            plotraw(input=input, show=False)
        else:
            plotinput(input=input, show=False)


if __name__ == "__main__":
    if "plot" in sys.argv:
        plotall("raw" in sys.argv)
    elif len(sys.argv) == 2:
        analyzebenchmarks(sys.argv[1])
    else:
        analyzebenchmarks()
