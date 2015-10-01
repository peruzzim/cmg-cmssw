import os
import csv
import sys
import ROOT

def parseCSV(infile):
    with open(infile,'rb') as f:
        reader = csv.reader(f,delimiter=',',quoting=csv.QUOTE_NONE)
        keys=next(reader)
        rows=[]
        for row in reader:
            rows.append(row)
        return keys,rows

def red(s,b=False):
    return '\x1b[%d;31m%s\x1b[0m'%(1 if b else 0,s)
def green(s,b=False):
    return '\x1b[%d;32m%s\x1b[0m'%(1 if b else 0,s)
def printred(s,b=False):
    print red(s,b)
def printgreen(s,b=False):
    print green(s,b)

def comparelines(r1,r2,n=-1):
    if r1==r2: return True
    if not n<0:
        eq = [False]*max(len(r1),len(r2))
        for i in xrange(min(len(r1),len(r2))):
            if r1[i]==r2[i]: eq[i]=True
        printred('Difference found on entry nr. %d'%n,b=True)
        print ', '.join([(r1[i] if eq[i] else red(r1[i])) for i in xrange(len(r1))])
        print ', '.join([(r2[i] if eq[i] else red(r2[i])) for i in xrange(len(r2))])
    return False

def compareCSV(j1,j2,stopAtError=False):
    if j1[0]!=j2[0]:
        print 'Different keys'
        return False
    bad=False
    if len(j1[1])!=len(j2[1]):
        printred('Different number of lines: %d vs. %d'%(len(j1[1]),len(j2[1])),b=True)
        bad=True
    if stopAtError and bad: return False
    for i in xrange(min(len(j1[1]),len(j2[1]))):
        if not comparelines(j1[1][i],j2[1][i],i): bad=True
        if stopAtError and bad: break
    if bad: return False
    printgreen('All ok',b=True)
    return True

def MuonPreselection(t,i):
    if not (abs(t.LepGood_pdgId[i])==13): return False
    if not (abs(t.LepGood_eta[i])<2.4): return False
    if not (abs(t.LepGood_dxy[i])<0.05): return False
    if not (abs(t.LepGood_dz[i])<0.1): return False
    if not (abs(t.LepGood_miniRelIso[i])<0.4): return False
    if not (t.LepGood_sip3d[i]<8): return False
    return True
def ElePreselection(t,i):
    if not (abs(t.LepGood_pdgId[i])==11): return False
    if not (abs(t.LepGood_eta[i])<2.5): return False
    if not (abs(t.LepGood_dxy[i])<0.05): return False
    if not (abs(t.LepGood_dz[i])<0.1): return False
    if not (abs(t.LepGood_miniRelIso[i])<0.4): return False
    if not (t.LepGood_sip3d[i]<8): return False
    eta = abs(t.LepGood_eta[i])
    if eta<0.8:
        if not (t.LepGood_mvaIdPhys14>0.73): return False
    elif eta<1.479:
        if not (t.LepGood_mvaIdPhys14>0.57): return False
    else:
        if not (t.LepGood_mvaIdPhys14>0.05): return False
    if not (t.LepGood_lostHits[i]<=1): return False
    return True

muonkeys=[('pt','LepGood_pt'),('eta','LepGood_eta'),('phi','LepGood_phi'),
        ('pdgID','LepGood_pdgId'),('charge','LepGood_charge'),('miniIso','LepGood_miniRelIso'),
        ('miniIsoCharged','LepGood_miniRelIsoCharged'),('miniIsoNeutral','LepGood_miniRelIsoNeutral'),
        ('jetPtRel','LepGood_jetPtRelv2'),('jetCSV','LepGood_jetBTagCSV'),('jetPtRatio','LepGood_jetPtRatio_LepAwareJECv2'),
        ('sip3D','LepGood_sip3d'),('dxy','LepGood_dxy'),('dz','LepGood_dz'),('segmentCompatibility','LepGood_segmentCompatibility')]
elekeys=muonkeys[:-1]+[('eleMVA','LepGood_mvaIdPhys14')]

if __name__=="__main__":

    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] tree.root")
    parser.add_option("-F", dest="friends", type="string", default=[], action="append",  help="Friend tree") 
    parser.add_option("-t", dest="test", type="string", default="muons", help="test name")
    parser.add_option("-n", dest="maxN", type="float", default="1e9", help="max entries")
    parser.add_option("-v", dest="verbose", default=False, action="store_true", help="print output")
    parser.add_option("-o", dest="outfile", default="outfile.txt", help="output file")
    parser.add_option("-c", dest="compare", default="", help="compare to this csv file")
    (options, args) = parser.parse_args()

    test = options.test
    fname = args[0]
    tfile = ROOT.TFile(fname)
    t = tfile.tree
    for fr in options.friends:
        f.AddFriend("sf/t",fr)
    maxN=int(options.maxN)
    N=0

    if test in ["muons","electrons"]:
        res=[['event#'],[]]
        keys = muonkeys if test=='muons' else elekeys
        psel = MuonPreselection if test=='muons' else ElePreselection
        res[0].extend([key[0] for key in keys])
        for ev in t:
            N+=1
            if N>maxN: break
            muons=[]
            for i in xrange(t.nLepGood):
                if not (psel(t,i)): continue
                muons.append(i)
            muons=muons[:1]
            for m in muons:
                out = []
                out.append(t.evt)
                for key in keys:
                    out.append(getattr(t,key[1])[m])
                res[1].append(out)

        outfilename = options.outfile
        with open(outfilename,'w') as outfile:
            outfile.write(','.join(res[0])+'\n')
            for row in res[1]:
                outfile.write('%d'%row[0]+','+','.join(['%.5f'%x for x in row[1:]])+'\n')
            outfile.close()
        print '%s entries found'%len(res[1])
        with open(outfilename,'r') as outfile:
            for line in outfile: print line.rstrip('\n')
        if options.compare!="":
            print 'Comparing to %s:'%options.compare
            oc=parseCSV(options.compare)
            oc2=parseCSV(outfilename)
            compareCSV(oc,oc2)
