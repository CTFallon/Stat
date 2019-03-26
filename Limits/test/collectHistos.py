
import ROOT
import os, sys
import optparse 
import copy
from Stat.Limits.settings import processes, histos


usage = 'usage: %prog -p histosPath -o outputFile'
parser = optparse.OptionParser(usage)
parser.add_option('-p', '--path', dest='path', type='string', default= "/t3home/decosa/SVJ/CMSSW_8_1_0/src/Stat/Limits/test/histos2016v6/",help='Where can I find input histos?')
parser.add_option("-o","--outputFile",dest="output",type="string",default="histos.root",help="Name of the output file collecting histos in Combine user frieldy schema. Default is histos.root")

(opt, args) = parser.parse_args()
sys.argv.append('-b')


path_ = opt.path
ofilename = opt.output

# Creating output file

ofile = ROOT.TFile(ofilename,"RECREATE")
ofile.Close()


# Getting list of files in histos
print os.listdir(path_)
sampFiles = [f for f in os.listdir(path_) if (os.path.isfile(os.path.join(path_, f)) and f.endswith(".root") and f!=ofilename )]
year = ""
if("2016" in path_): year = "2016"
elif("2017" in path_): year = "2017"
elif("2018" in path_): year = "2018"

#*******************************************************#
#                                                       #
#     FILLING IN THE INPUT ROOT FILE FOR COMBINE        #
#                                                       #
#*******************************************************#

for f in sampFiles: 

    try:
        ifile = ROOT.TFile.Open(path_ + f)
    except IOError:
        print "Cannot open ", f
    else:
        print "Opening file ",  f
        ifile.cd()
        

    samp = f.replace(".root", "")         
    
    print "We are looking into file: ", f
    ofile = ROOT.TFile(ofilename,"UPDATE")

    for k_, h_ in histos.iteritems():    

        h = ifile.Get(h_)
        if not os.path.isdir( k_+ "_" + year):
            newsubdir = ofile.mkdir(k_ + "_" +year)
        ofile.cd(k_+ "_" +year)
        if(samp.startswith("Data")): samp = "data_obs"
        print "We are looking for histo %s for samp %s in %s" % (h_, samp, f)
        h.SetName(samp)
        h.Write(samp, ROOT.TObject.kWriteDelete)
        nBinsX = h.GetNbinsX()
        print "SAMP ",samp



        if k_ in samp: samp = samp.replace("_" + k_, "")         
        elif "cat" in samp: samp = samp.replace("cat_", "")         
        print "SAMP after channel removal ",samp
        if(samp.startswith("data")): samp = "Data"
        #        h_ = h_[:4]
        for n in xrange(nBinsX):
            hNameUp = "%s_mcstat_%s_bin%d_Up" % ( h_, samp, n+1)
            hNameDown = "%s_mcstat_%s_bin%d_Down" % ( h_, samp, n+1)
            #hNameUp = "%s_%s" % (h_, NameUp)
            #hNameDown = "%s_%s" % (h_, NameDown)
            print "Histogram: ", hNameUp              
            h_mcStatUp = ifile.Get(hNameUp)
            h_mcStatDown = ifile.Get(hNameDown)
            h_mcStatUp.SetName("%s_mcstat_%s_%s_%s_bin%dUp" % (samp, k_, year, samp, n+1))
            h_mcStatUp.Write("%s_mcstat_%s_%s_%s_bin%dUp" % (samp, k_, year, samp, n+1), ROOT.TObject.kWriteDelete)
            h_mcStatDown.SetName("%s_mcstat_%s_%s_%s_bin%dDown" % (samp, k_, year,  samp, n+1))
            h_mcStatDown.Write("%s_mcstat_%s_%s_%s_bin%dDown" % (samp, k_, year, samp, n+1), ROOT.TObject.kWriteDelete)

    ofile.Write()
    ofile.Close()



#*******************************************************#
#                                                       #
#           CREATING TOTAL BACKGORUND HISTOS            #
#                                                       #
#*******************************************************#


histData = dict(zip(histos.keys(), [None]*len(histos.keys())))

for p in processes:

    try:
        ifile = ROOT.TFile.Open(path_ + p +".root")
    except IOError:
        print "Cannot open ", p +".root"
    else:
        print "Opening file ",  p +".root"
        ifile.cd()

        
    for k_, h_ in histos.iteritems():    
        tmphist = ifile.Get( h_)
        if histData[k_] is None: 
            histData[k_] = copy.deepcopy(tmphist)
        else: histData[k_].Add(tmphist)
    


ofile = ROOT.TFile(ofilename,"UPDATE")    

for k_ in histos.keys():    
    if not os.path.isdir( k_ + "_" + year):
        newsubdir = ofile.mkdir(k_+"_" + year)
    ofile.cd(k_+ "_" + year)
    histData[k_].SetName("Bkg")
    histData[k_].Write("Bkg", ROOT.TObject.kWriteDelete)


ofile.Write()
ofile.Close()
