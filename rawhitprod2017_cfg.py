import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing

import os,sys

options = VarParsing.VarParsing('standard') # avoid the options: maxEvents, files, secondaryFiles, output, secondaryOutput because they are already defined in 'standard'
#Change the data folder appropriately to where you wish to access the files from:
options.register('dataFolder',
                 './',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 'folder containing raw input')

options.register('runNumber',
                 106,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 'Input run to process')

options.register('outputFolder',
                 '/afs/cern.ch/work/r/rchatter/TestBeam_July_Fix/CMSSW_8_0_21/src/HGCal/',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 'Output folder where analysis output are stored')

options.register('electronicMap',
                 'HGCal/CondObjects/data/map_CERN_Hexaboard_September_17Sensors_7EELayers_10FHLayers_V1.txt',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 'path to the electronic map')
# Available options: 
# "HGCal/CondObjects/data/map_CERN_Hexaboard_July_6Layers.txt"
# "HGCal/CondObjects/data/map_CERN_Hexaboard_September_17Sensors_7EELayers_10FHLayers_V1.txt" # end of september
# "HGCal/CondObjects/data/map_CERN_Hexaboard_October_17Sensors_5EELayers_6FHLayers_V1.txt" # october 18-22, 1st conf
# "HGCal/CondObjects/data/map_CERN_Hexaboard_October_20Sensors_5EELayers_7FHLayers_V1.txt" # october 18-22, 2nd conf

options.register('hgcalLayout',
                 'HGCal/CondObjects/data/layerGeom_oct2017_h2_17layers.txt',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 'path to hgcal layout file')
# Available options: 
# "HGCal/CondObjects/data/layerGeom_oct2017_h2_17layers.txt"
# "HGCal/CondObjects/data/layerGeom_oct2017_h6_17layers.txt"
# "HGCal/CondObjects/data/layerGeom_oct2017_h6_20layers.txt"

options.maxEvents = -1
options.output = "cmsswEvents.root"

options.parseArguments()
print options
if not os.path.isdir(options.dataFolder):
    sys.exit("Error: Data folder not found or inaccessible!")



pedestalHighGain="pedestalHG_"+str(options.runNumber)+".txt"
pedestalLowGain="pedestalLG_"+str(options.runNumber)+".txt"
noisyChannels="noisyChannels_"+str(options.runNumber)+".txt"

################################
process = cms.Process("rawhitprod")
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents)
)

####################################

process.source = cms.Source("PoolSource",
                            fileNames=cms.untracked.vstring("file:%s/cmsswEvents_Run%d.root"%(options.dataFolder,options.runNumber))
)

filename = options.outputFolder+"/HexaOutput_"+str(options.runNumber)+".root"
process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string(filename)
)
process.output = cms.OutputModule("PoolOutputModule",
                                  fileName = cms.untracked.string(options.output),
                                  outputCommands = cms.untracked.vstring('drop *',
                                                                         'keep *_*_HGCALTBRAWHITS_*')
)

process.rawhitproducer = cms.EDProducer("HGCalTBRawHitProducer",
                                        InputCollection=cms.InputTag("source","skiroc2cmsdata"),
                                        OutputCollectionName=cms.string("HGCALTBRAWHITS"),
                                        ElectronicMap=cms.untracked.string(options.electronicMap),
                                        SubtractPedestal=cms.untracked.bool(True),
                                        MaskNoisyChannels=cms.untracked.bool(True),
                                        HighGainPedestalFileName=cms.untracked.string(pedestalHighGain),
                                        LowGainPedestalFileName=cms.untracked.string(pedestalLowGain),
                                        ChannelsToMaskFileName=cms.untracked.string(noisyChannels)
)

process.rawhitplotter = cms.EDAnalyzer("RawHitPlotter",
                                       InputCollection=cms.InputTag("rawhitproducer","HGCALTBRAWHITS"),
                                       ElectronicMap=cms.untracked.string(options.electronicMap),
                                       DetectorLayout=cms.untracked.string(options.hgcalLayout),
                                       SensorSize=cms.untracked.int32(128),
                                       EventPlotter=cms.untracked.bool(False),
                                       SubtractCommonMode=cms.untracked.bool(True)
)

process.pulseshapeplotter = cms.EDAnalyzer("PulseShapePlotter",
                                           InputCollection=cms.InputTag("rawhitproducer","HGCALTBRAWHITS"),
                                           ElectronicMap=cms.untracked.string(options.electronicMap)
)


process.p = cms.Path( process.rawhitproducer*process.rawhitplotter )

process.end = cms.EndPath(process.output)
