#
# example on how to use this:
#
# eos cp /eos/cms/store/group/dpg_ecal/alca_ecalcalib/hardenbr/OPTIM_NTUPLES/MINBIAS_PIZERO_ALCARAW_NOUNCAL_NOL1FILTER_40bx50_WITHSELECTION_WITHGEN_WITHRECHIT/outputALCAP0_363_1_jme.root /tmp/amassiro/
# cmsRun example.py \
#        inputFiles=file:/tmp/amassiro/outputALCAP0_363_1_jme.root \
#        outputFile=/tmp/amassiro/
#    


useHLTFilter = False
correctHits = False

import FWCore.ParameterSet.Config as cms
import RecoLocalCalo.EcalRecProducers.ecalRecalibRecHit_cfi
import os, sys, imp, re
CMSSW_VERSION = os.getenv("CMSSW_VERSION")
process = cms.Process("analyzerFillEpsilon")
process.load("FWCore.MessageService.MessageLogger_cfi")



# manage input variables
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing ('analysis')
# add a list of strings for events to process
options.parseArguments()



process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = 'MCRUN2_74_V6A::All'
#RAW to DIGI'
#https://github.com/cms-sw/cmssw/blob/CMSSW_7_5_X/RecoLocalCalo/EcalRecProducers/test/testMultipleEcalRecoLocal_cfg.py
#process.load('Configuration.StandardSequences.RawToDigi_cff')
#process.raw2digi_step = cms.Sequence(process.RawToDigi)
#DIGI to UNCALIB
#https://github.com/cms-sw/cmssw/blob/CMSSW_7_5_X/RecoLocalCalo/EcalRecProducers/test/testMultipleEcalRecoLocal_cfg.py
process.load('Configuration.StandardSequences.Reconstruction_cff')
import RecoLocalCalo.EcalRecProducers.ecalMultiFitUncalibRecHit_cfi
process.ecalMultiFitUncalibRecHit =  RecoLocalCalo.EcalRecProducers.ecalMultiFitUncalibRecHit_cfi.ecalMultiFitUncalibRecHit.clone()
process.ecalMultiFitUncalibRecHit.activeBXs = cms.vint32(-5,-4,-3,-2,-1,0,1,2,3,4) #Are 10 (-5-5). For 50ns is (-4,-2,0,2,4) #Is .algoPSet. in latest release
#process.ecalMultiFitUncalibRecHit.algoPSet.activeBXs = cms.vint32(-5,-4,-3,-2,-1,0,1,2,3,4) #Are 10 (-5-5). For 50ns is (-4,-2,0,2,4) #Is .algoPSet. in latest release
process.ecalMultiFitUncalibRecHit.useLumiInfoRunHeader = cms.bool( False )

#process.ecalMultiFitUncalibRecHit.EBdigiCollection = cms.InputTag("hltAlCaEtaEBRechitsToDigis","etaEBDigis","TEST")
#process.ecalMultiFitUncalibRecHit.EEdigiCollection = cms.InputTag("hltAlCaEtaEERechitsToDigis","etaEEDigis","TEST")
process.ecalMultiFitUncalibRecHit.EBdigiCollection = cms.InputTag("hltAlCaPi0EBRechitsToDigis","pi0EBDigis","TEST")
process.ecalMultiFitUncalibRecHit.EEdigiCollection = cms.InputTag("hltAlCaPi0EERechitsToDigis","pi0EEDigis","TEST")

#UNCALIB to CALIB
#https://github.com/cms-sw/cmssw/blob/CMSSW_7_4_X/RecoLocalCalo/EcalRecProducers/python/ecalLocalRecoSequence_cff.py
from RecoLocalCalo.EcalRecProducers.ecalRecHit_cfi import *
process.ecalDetIdToBeRecovered =  RecoLocalCalo.EcalRecProducers.ecalDetIdToBeRecovered_cfi.ecalDetIdToBeRecovered.clone()
process.ecalRecHit.killDeadChannels = cms.bool( False )
process.ecalRecHit.recoverEBVFE = cms.bool( False )
process.ecalRecHit.recoverEEVFE = cms.bool( False )
process.ecalRecHit.recoverEBFE = cms.bool( False )
process.ecalRecHit.recoverEEFE = cms.bool( False )
process.ecalRecHit.recoverEEIsolatedChannels = cms.bool( False )
process.ecalRecHit.recoverEBIsolatedChannels = cms.bool( False )
process.ecalLocalRecoSequence = cms.Sequence(ecalRecHit)
### Recalibration Module to apply laser corrections on the fly
if correctHits:
    process.ecalPi0ReCorrected =  RecoLocalCalo.EcalRecProducers.ecalRecalibRecHit_cfi.ecalRecHit.clone(
        doEnergyScale = cms.bool(False),
        doIntercalib = cms.bool(False),
        doLaserCorrections = cms.bool(False),
        EBRecHitCollection = cms.InputTag("ecalRecHit","EcalRecHitsEB","analyzerFillEpsilon"),
        EERecHitCollection = cms.InputTag("ecalRecHit","EcalRecHitsEE","analyzerFillEpsilon"),
        EBRecalibRecHitCollection = cms.string("pi0EcalRecHitsEB"),
        EERecalibRecHitCollection = cms.string("pi0EcalRecHitsEE")
    )

### Running on AlcaRAW requires filtering AlcaPi0 events from AlcaEta events
if useHLTFilter:
    import copy
    from HLTrigger.HLTfilters.hltHighLevel_cfi import *
    process.AlcaP0Filter = copy.deepcopy(hltHighLevel)
    process.AlcaP0Filter.throw = cms.bool(False)
    process.AlcaP0Filter.HLTPaths = ["AlCa_EcalPi0_*"]

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
process.MessageLogger.cerr.FwkReport.reportEvery = 1000000
process.MessageLogger.cerr = cms.untracked.PSet(
        threshold  = cms.untracked.string('WARNING'),
        ERROR      = cms.untracked.PSet (
                                         limit = cms.untracked.int32(1)
        )
)
process.options = cms.untracked.PSet(
   wantSummary = cms.untracked.bool(True),
   SkipEvent = cms.untracked.vstring('ProductNotFound')
)
process.source = cms.Source('PoolSource',
    fileNames = cms.untracked.vstring(
        options.inputFiles
        #'root://eoscms//eos/cms/store/group/dpg_ecal/alca_ecalcalib/hardenbr/STREAM_OUTPUT/NEU_GUN_40bx25_WITH_SELECTION_NOL1/outputALCAP0_1000_1_0jE.root',
        #'root://eoscms//eos/cms/store/group/dpg_ecal/alca_ecalcalib/hardenbr/STREAM_OUTPUT/NEU_GUN_40bx25_WITH_SELECTION_NOL1/outputALCAP0_1001_1_LqC.root',
        #'root://eoscms//eos/cms/store/group/dpg_ecal/alca_ecalcalib/hardenbr/STREAM_OUTPUT/NEU_GUN_40bx25_WITH_SELECTION_NOL1/outputALCAP0_1002_1_8A8.root',
        #'root://eoscms//eos/cms/store/group/dpg_ecal/alca_ecalcalib/hardenbr/STREAM_OUTPUT/NEU_GUN_40bx25_WITH_SELECTION_NOL1/outputALCAP0_1003_1_SJA.root',
        #'root://eoscms//eos/cms/store/group/dpg_ecal/alca_ecalcalib/hardenbr/STREAM_OUTPUT/NEU_GUN_40bx25_WITH_SELECTION_NOL1/outputALCAP0_1004_1_2Id.root',
        #'root://eoscms//eos/cms/store/group/dpg_ecal/alca_ecalcalib/hardenbr/STREAM_OUTPUT/NEU_GUN_40bx25_WITH_SELECTION_NOL1/outputALCAP0_1005_1_q7J.root'
    )
)


process.analyzerFillEpsilon = cms.EDAnalyzer('FillEpsilonPlot')
process.analyzerFillEpsilon.OutputDir = cms.untracked.string(options.outputFile)
process.analyzerFillEpsilon.OutputFile = cms.untracked.string('EcalNtp_0.root')
process.analyzerFillEpsilon.ExternalGeometry = cms.untracked.string('CalibCode/FillEpsilonPlot/data/caloGeometry.root')
#process.analyzerFillEpsilon.calibMapPath = cms.untracked.string('CalibCode/FillEpsilonPlot/data/calibMap.root')
process.analyzerFillEpsilon.calibMapPath = cms.untracked.string('EMPTY')
process.analyzerFillEpsilon.useEBContainmentCorrections = cms.untracked.bool(True)
process.analyzerFillEpsilon.useEEContainmentCorrections = cms.untracked.bool(False)
process.analyzerFillEpsilon.EBContainmentCorrections = cms.untracked.string('CalibCode/FillEpsilonPlot/data/totNewPi0TupleMB_fillingTot.fittedcorrectionsEB.root')
process.analyzerFillEpsilon.MVAEBContainmentCorrections_01  = cms.untracked.string('CalibCode/FillEpsilonPlot/data/JOSH_MVA_pi01_Mediumtrain.root')
process.analyzerFillEpsilon.MVAEBContainmentCorrections_02  = cms.untracked.string('CalibCode/FillEpsilonPlot/data/JOSH_MVA_pi02_Mediumtrain.root')
process.analyzerFillEpsilon.MVAEEContainmentCorrections_01  = cms.untracked.string('CalibCode/FillEpsilonPlot/data/JOSH_MVA_pi01_Mediumtrain_EE.root')
process.analyzerFillEpsilon.MVAEEContainmentCorrections_02  = cms.untracked.string('CalibCode/FillEpsilonPlot/data/JOSH_MVA_pi02_Mediumtrain_EE.root')
process.analyzerFillEpsilon.MVAEBContainmentCorrections_eta01  = cms.untracked.string('CalibCode/FillEpsilonPlot/data/JOSH_MVA_eta1_Mediumtrain.root')
process.analyzerFillEpsilon.MVAEBContainmentCorrections_eta02  = cms.untracked.string('CalibCode/FillEpsilonPlot/data/JOSH_MVA_eta2_Mediumtrain.root')
process.analyzerFillEpsilon.Endc_x_y                        = cms.untracked.string('CalibCode/FillEpsilonPlot/data/Endc_x_y_ring.txt')
process.analyzerFillEpsilon.EBPHIContainmentCorrections = cms.untracked.string('CalibCode/FillEpsilonPlot/data/correctionsEB_PHI.root')
process.analyzerFillEpsilon.EEContainmentCorrections    = cms.untracked.string('CalibCode/FillEpsilonPlot/data/totNewPi0TupleMB_fillingTot.fittedcorrectionsEE.root')
process.analyzerFillEpsilon.ContCorr_EB                 = cms.untracked.string('CalibCode/FillEpsilonPlot/data/correctionsEB.root')
process.analyzerFillEpsilon.HLTResults                  = cms.untracked.bool(False)
process.analyzerFillEpsilon.RemoveDead_Flag             = cms.untracked.bool(True)
process.analyzerFillEpsilon.RemoveDead_Map              = cms.untracked.string('')
process.analyzerFillEpsilon.EtaRingCalibEB    = cms.untracked.bool(True)
process.analyzerFillEpsilon.EtaRingCalibEE    = cms.untracked.bool(True)
process.analyzerFillEpsilon.CalibMapEtaRing = cms.untracked.string('CalibCode/FillEpsilonPlot/data/calibMap.root')
process.analyzerFillEpsilon.Are_pi0                 = cms.untracked.bool(True)
process.analyzerFillEpsilon.useOnlyEEClusterMatchedWithES = cms.untracked.bool(True)

### choosing proper input tag (recalibration module changes the collection names)
if correctHits:
    process.analyzerFillEpsilon.EBRecHitCollectionTag = cms.untracked.InputTag('ecalPi0ReCorrected','pi0EcalRecHitsEB')
    process.analyzerFillEpsilon.EERecHitCollectionTag = cms.untracked.InputTag('ecalPi0ReCorrected','pi0EcalRecHitsEE')
else:
    process.analyzerFillEpsilon.EBRecHitCollectionTag = cms.untracked.InputTag("ecalRecHit","EcalRecHitsEB","analyzerFillEpsilon")
    process.analyzerFillEpsilon.EERecHitCollectionTag = cms.untracked.InputTag("ecalRecHit","EcalRecHitsEE","analyzerFillEpsilon")
process.analyzerFillEpsilon.ESRecHitCollectionTag = cms.untracked.InputTag('hltAlCaPi0RecHitsFilterEEonlyRegional','pi0EcalRecHitsES','TEST')
process.analyzerFillEpsilon.L1TriggerTag = cms.untracked.InputTag('simGtDigis','','TEST')
process.analyzerFillEpsilon.triggerTag   = cms.untracked.InputTag("TriggerResults","","TEST")
process.analyzerFillEpsilon.hltL1GtObjectMap   = cms.untracked.InputTag("hltL1GtObjectMap","","TEST")
process.analyzerFillEpsilon.CalibType    = cms.untracked.string('xtal')
process.analyzerFillEpsilon.CurrentIteration = cms.untracked.int32(0) # ---> first!
process.analyzerFillEpsilon.EB_Seed_E = cms.untracked.double(0.5)
process.analyzerFillEpsilon.useEE_EtSeed = cms.untracked.bool(False)
process.analyzerFillEpsilon.EE_Seed_E = cms.untracked.double(1.5)
process.analyzerFillEpsilon.EE_Seed_Et = cms.untracked.double(0.5)
process.analyzerFillEpsilon.Pi0PtCutEB_low = cms.untracked.double(1)
process.analyzerFillEpsilon.Pi0PtCutEB_high = cms.untracked.double(1.0)
process.analyzerFillEpsilon.Pi0PtCutEE_low = cms.untracked.double(1.0)
process.analyzerFillEpsilon.Pi0PtCutEE_high = cms.untracked.double(1.0)
process.analyzerFillEpsilon.gPtCutEB_low = cms.untracked.double(.4)
process.analyzerFillEpsilon.gPtCutEB_high = cms.untracked.double(.4)
process.analyzerFillEpsilon.gPtCutEE_low = cms.untracked.double(.4)
process.analyzerFillEpsilon.gPtCutEE_high = cms.untracked.double(0.4)
process.analyzerFillEpsilon.Pi0IsoCutEB_low = cms.untracked.double(0.0)
process.analyzerFillEpsilon.Pi0IsoCutEB_high = cms.untracked.double(0.0)
process.analyzerFillEpsilon.Pi0IsoCutEE_low = cms.untracked.double(.0)
process.analyzerFillEpsilon.Pi0IsoCutEE_high = cms.untracked.double(0.0)
process.analyzerFillEpsilon.CutOnHLTIso = cms.untracked.bool(False)
process.analyzerFillEpsilon.Pi0HLTIsoCutEB_low = cms.untracked.double(999)
process.analyzerFillEpsilon.Pi0HLTIsoCutEB_high = cms.untracked.double(999)
process.analyzerFillEpsilon.Pi0HLTIsoCutEE_low = cms.untracked.double(999)
process.analyzerFillEpsilon.Pi0HLTIsoCutEE_high = cms.untracked.double(999)
process.analyzerFillEpsilon.nXtal_1_EB_low = cms.untracked.double(0)
process.analyzerFillEpsilon.nXtal_1_EB_high = cms.untracked.double(0)
process.analyzerFillEpsilon.nXtal_2_EB_low = cms.untracked.double(0)
process.analyzerFillEpsilon.nXtal_2_EB_high = cms.untracked.double(0)
process.analyzerFillEpsilon.nXtal_1_EE_low = cms.untracked.double(0)
process.analyzerFillEpsilon.nXtal_1_EE_high = cms.untracked.double(0)
process.analyzerFillEpsilon.nXtal_2_EE_low = cms.untracked.double(0)
process.analyzerFillEpsilon.nXtal_2_EE_high = cms.untracked.double(0)
process.analyzerFillEpsilon.S4S9_EB_low = cms.untracked.double(0.6)
process.analyzerFillEpsilon.S4S9_EB_high = cms.untracked.double(0.6)
process.analyzerFillEpsilon.S4S9_EE_low = cms.untracked.double(0.6)
process.analyzerFillEpsilon.S4S9_EE_high = cms.untracked.double(0.6)
process.analyzerFillEpsilon.Barrel_orEndcap = cms.untracked.string('ALL_PLEASE')

process.analyzerFillEpsilon.isMC = cms.untracked.bool(True)
process.analyzerFillEpsilon.MC_Asssoc = cms.untracked.bool(True)

process.analyzerFillEpsilon.MakeNtuple4optimization = cms.untracked.bool(True)

       
process.p = cms.Path()
if useHLTFilter:
    process.p *= process.AlcaP0Filter
if correctHits:
    print 'ADDING RECALIB RECHIT MODULE WITH PARAMETERS'
    print 'ENERGY SCALE '+str(process.ecalPi0ReCorrected.doEnergyScale)
    print 'INTERCALIBRATION '+str(process.ecalPi0ReCorrected.doIntercalib)
    print 'LASER '+str(process.ecalPi0ReCorrected.doLaserCorrections)
    process.p *= process.ecalPi0ReCorrected
process.p *= process.ecalMultiFitUncalibRecHit
process.p *= process.ecalLocalRecoSequence
process.p *= process.analyzerFillEpsilon
