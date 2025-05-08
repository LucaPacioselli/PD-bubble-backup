#!/opt/conda/bin/python3

import ROOT
import os
from dask.distributed import Client, PipInstall, WorkerPlugin, LocalCluster
import json
from samplesUL import *
import sys
from dask_jobqueue import SLURMCluster, HTCondorCluster
from distributed.diagnostics.plugin import UploadFile

import dask
from dask import delayed

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

distributed = True
MT = False
redirector = ""
#redirector = "root://t2-xrdcms.lnl.infn.it:7070/" # Legnaro - OK\
#redirector = "file:///shared-scratch/cms"
#redirector = "file:///shared/home/cms"
# Default in the txt chain files
#redirector = "file:///scratch/cms" # Local storage nvme
maxNfilespersample = 1 # 99999 #5 lower this number just for debugging purposes: 99999 prod.
nPartitions = 10*3  #used only in distributed mode (golden rule 3*Nworkers)

if distributed != True and MT == True:
    ROOT.ROOT.EnableImplicitMT()

# Workaround to CA verification
def https_get_file(file_path, name):
    try:
        import requests
    except:
        print("No import requests")
    response = requests.get(file_path, verify=False)
    with open(name, "wb") as f:
        f.write(response.content)

def set_proxy(dask_worker):
    import os
    import shutil
    working_dir = dask_worker.local_directory
    
    import requests
    response = requests.get("https://cmsdoc.cern.ch/~lpaciose/proxy", verify=False)
    with open("proxy", "wb") as f:
        f.write(response.content)
    
    os.environ['X509_USER_PROXY'] = working_dir + '/proxy'
    os.environ['X509_CERT_DIR']="/cvmfs/grid.cern.ch/etc/grid-security/certificates/"
    os.environ['EXTRA_CLING_ARGS'] = "-O2"
    try:
        shutil.copyfile(working_dir + '/proxy', working_dir + '/../../../proxy')
    except:
        pass
    try:
        os.chmod(working_dir + '/proxy', 0o400)
    except:
        pass
    try:
        os.chmod(working_dir + '/../../../proxy', 0o400)
    except:
        pass
        
    return os.environ.get("X509_USER_PROXY")

#from my_initialization_function_UL import *
text_file = open("preselection_UL.h", "r")
data = text_file.read()

text_file = open("preselection_part2_UL.h", "r")
data_2 = text_file.read()

def my_initialization_function():
    
    import ROOT
    import sys
    ROOT.EnableThreadSafety()
    #ROOT.gInterpreter.AddIncludePath("/cvmfs/cms.dodas.infn.it/boost_1_77_0")
    sys.path.append("/lib/python3.8/site-packages")
    ROOT.gInterpreter.AddIncludePath("/usr/lib/boost_1_77_0")
    ROOT.gInterpreter.AddIncludePath("/opt/conda/include")
    ROOT.gInterpreter.AddIncludePath("/scratch/jobs/dspiga")
    
    jec_prefix_MC = "Summer19UL17_V6_MC"
    jer_prefix_MC = "Summer19UL17_JRV3_MC"
    
    https_get_file("https://ttedesch.web.cern.ch/ttedesch/NEWERA/nanoAOD-tools/python/postprocessing/data/roccor.Run2.v5/RoccoR2017UL.txt", "RoccoR2017UL.txt")
    https_get_file("https://ttedesch.web.cern.ch/ttedesch/NEWERA/nanoAOD-tools/python/postprocessing/data/roccor.Run2.v5/RoccoR.cc", "RoccoR.cc")
    https_get_file("https://ttedesch.web.cern.ch/ttedesch/NEWERA/nanoAOD-tools/python/postprocessing/data/roccor.Run2.v5/RoccoR.h", "RoccoR.h")
    https_get_file("https://ttedesch.web.cern.ch/ttedesch/NEWERA/nanoAOD-tools/data/btagSF/DeepJet_106XUL17_v3_new.csv", "DeepJet_106XUL17_v3_new.csv")
    
    ROOT.gInterpreter.Declare(
        '''
        #ifndef ROCCOR
        #define ROCCOR
        #include "RoccoR.cc"
        #endif
        ''')

    https_get_file("https://ttedesch.web.cern.ch/ttedesch/NEWERA/nanoAOD-tools/data/jme/{}_L1FastJet_AK4PFchs.txt".format(jec_prefix_MC), "{}_L1FastJet_AK4PFchs.txt".format(jec_prefix_MC))
    https_get_file("https://ttedesch.web.cern.ch/ttedesch/NEWERA/nanoAOD-tools/data/jme/{}_L2Relative_AK4PFchs.txt".format(jec_prefix_MC), "{}_L2Relative_AK4PFchs.txt".format(jec_prefix_MC))
    https_get_file("https://ttedesch.web.cern.ch/ttedesch/NEWERA/nanoAOD-tools/data/jme/{}_L3Absolute_AK4PFchs.txt".format(jec_prefix_MC), "{}_L3Absolute_AK4PFchs.txt".format(jec_prefix_MC))
    https_get_file("https://ttedesch.web.cern.ch/ttedesch/NEWERA/nanoAOD-tools/data/jme/{}_L2L3Residual_AK4PFchs.txt".format(jec_prefix_MC), "{}_L2L3Residual_AK4PFchs.txt".format(jec_prefix_MC))
    https_get_file("https://ttedesch.web.cern.ch/ttedesch/NEWERA/nanoAOD-tools/data/jme/{}_UncertaintySources_AK4PFchs.txt".format(jec_prefix_MC), "{}_UncertaintySources_AK4PFchs.txt".format(jec_prefix_MC))
    https_get_file("https://ttedesch.web.cern.ch/ttedesch/NEWERA/nanoAOD-tools/data/jme/{}_PtResolution_AK4PFchs.txt".format(jer_prefix_MC), "{}_PtResolution_AK4PFchs.txt".format(jer_prefix_MC))
    https_get_file("https://ttedesch.web.cern.ch/ttedesch/NEWERA/nanoAOD-tools/data/jme/{}_SF_AK4PFchs.txt".format(jer_prefix_MC), "{}_SF_AK4PFchs.txt".format(jer_prefix_MC))
    
    
    ROOT.gInterpreter.Declare('{}'.format(data))

    ROOT.gInterpreter.ProcessLine('#ifndef LOADING')
    ROOT.gInterpreter.ProcessLine('#define LOADING')
    
    ROOT.gInterpreter.ProcessLine('reader_1_UL2017.load(calibration_UL2017, BTagEntry::FLAV_B, "comb");')
    ROOT.gInterpreter.ProcessLine('reader_1_UL2017.load(calibration_UL2017, BTagEntry::FLAV_C, "comb");')
    ROOT.gInterpreter.ProcessLine('reader_1_UL2017.load(calibration_UL2017, BTagEntry::FLAV_UDSG, "incl");')

    ROOT.gInterpreter.ProcessLine('#endif')
    
    ROOT.gInterpreter.Declare('{}'.format(data_2))
    

    from CMSJMECalculators import loadJMESystematicsCalculators
    loadJMESystematicsCalculators()

    
    ################################# JET #####################################################################################################
    
    ROOT.gROOT.ProcessLine("JetVariationsCalculator myJetVarCalc{};")
    calc = getattr(ROOT, "myJetVarCalc")

    # redo JEC, push_back corrector parameters for different levels
    jecParams = getattr(ROOT, "std::vector<JetCorrectorParameters>")()
    jecParams.push_back(ROOT.JetCorrectorParameters("./{}_L1FastJet_AK4PFchs.txt".format(jec_prefix_MC)))
    jecParams.push_back(ROOT.JetCorrectorParameters("./{}_L2Relative_AK4PFchs.txt".format(jec_prefix_MC)))
    #jecParams.push_back(ROOT.JetCorrectorParameters("./{}_L3Absolute_AK4PFchs.txt".format(jec_prefix_MC)))
    jecParams.push_back(ROOT.JetCorrectorParameters("./{}_L2L3Residual_AK4PFchs.txt".format(jec_prefix_MC)))
    calc.setJEC(jecParams)

    uncert_sources = ["Total"]
    #uncert_sources = []
    # calculate JES uncertainties
    with open("./{}_UncertaintySources_AK4PFchs.txt".format(jec_prefix_MC)) as f:
        lines = f.read().split("\n")
        sources = [
            x for x in lines if x.startswith("[") and x.endswith("]")
        ]
        sources = [x[1:-1] for x in sources]
        sources = list(filter(lambda source: source in uncert_sources, sources))

    for s in sources:
        jcp_unc = ROOT.JetCorrectorParameters("./{}_UncertaintySources_AK4PFchs.txt".format(jec_prefix_MC), s)
        calc.addJESUncertainty(s, jcp_unc)

    # Smear jets, with JER uncertainty
    calc.setSmearing("./{}_PtResolution_AK4PFchs.txt".format(jer_prefix_MC), "./{}_SF_AK4PFchs.txt".format(jer_prefix_MC), False, True, 0.2, 3.)  # use hybrid recipe, matching parameters

    jetvariations = [calc.available()[i] for i in range(0,calc.available().size())]
    
    ############################################ MET T1SMEAR ###########################################################################################
    
    ROOT.gROOT.ProcessLine("Type1METVariationsCalculator myType1SmearMETVarCalc{};")
    calc = getattr(ROOT, "myType1SmearMETVarCalc")

    # redo JEC, push_back corrector parameters for different levels
    jecParams = getattr(ROOT, "std::vector<JetCorrectorParameters>")()
    jecParams.push_back(ROOT.JetCorrectorParameters("./{}_L1FastJet_AK4PFchs.txt".format(jec_prefix_MC)))
    jecParams.push_back(ROOT.JetCorrectorParameters("./{}_L2Relative_AK4PFchs.txt".format(jec_prefix_MC)))
    jecParams.push_back(ROOT.JetCorrectorParameters("./{}_L2L3Residual_AK4PFchs.txt".format(jec_prefix_MC)))

    calc.setJEC(jecParams)

    jecParams = getattr(ROOT, "std::vector<JetCorrectorParameters>")()
    jecParams.push_back(ROOT.JetCorrectorParameters("./{}_L1FastJet_AK4PFchs.txt".format(jec_prefix_MC)))
    calc.setL1JEC(jecParams)

    calc.setIsT1SmearedMET(True)

    # calculate JES uncertainties
    with open("./{}_UncertaintySources_AK4PFchs.txt".format(jec_prefix_MC)) as f:
        lines = f.read().split("\n")
        sources = [
            x for x in lines if x.startswith("[") and x.endswith("]")
        ]
        sources = [x[1:-1] for x in sources]
        sources = list(filter(lambda source: source in uncert_sources, sources))


    for s in sources:
        jcp_unc = ROOT.JetCorrectorParameters("./{}_UncertaintySources_AK4PFchs.txt".format(jec_prefix_MC), s)
        calc.addJESUncertainty(s, jcp_unc)

    # Smear jets, with JER uncertainty
    calc.setSmearing("./{}_PtResolution_AK4PFchs.txt".format(jer_prefix_MC), "./{}_SF_AK4PFchs.txt".format(jer_prefix_MC), False, True, 0.2, 3.)  # use hybrid recipe, matching parameters

    mett1smearvariations = [calc.available()[i] for i in range(0, calc.available().size())]
    
    print(mett1smearvariations)

    #ROOT.gInterpreter.ProcessLine('#endif')

    
jetvariations = [
'nominal',
'jerUp',
'jerDown',
'jesTotalUp',
'jesTotalDown',
]

mett1smearvariations = jetvariations

if distributed == True:
    RDataFrame = ROOT.RDF.Experimental.Distributed.Dask.RDataFrame
    cluster = SLURMCluster(n_workers=10, cores=1, memory='2GB' nanny=True)
    client = Client(cluster) # n_workers=10, threads_per_worker=2, processes=False
    #client = Client(cluster) #address="tcp://127.0.0.1:"+str(sched_port))
    #client.restart()
    try:
        https_get_file("https://cmsdoc.cern.ch/~lpaciose/proxy", "proxy")
        current_path = os.path.abspath(os.getcwd())
        proxy_path = current_path + '/proxy'
        print(proxy_path)
        os.environ['X509_USER_PROXY'] = proxy_path
        client.register_plugin(UploadFile(proxy_path))
        print("after register plugin")
    except:
        print("no Upload file proxy")
    client.run(set_proxy)
    print("after set proxy")
    ROOT.RDF.Experimental.Distributed.initialize(my_initialization_function)
else:
    RDataFrame = ROOT.RDataFrame
    my_initialization_function()

print("before chains")
sampleDict = {'ZZtoLep_UL2016APV': 0,'ZZTo2L2Nu_UL2016APV': 1,'ZZTo4L_UL2016APV': 2,'GluGluToContinToZZTo4e_UL2016APV': 3,'GluGluToContinToZZTo2e2mu_UL2016APV': 4,'GluGluToContinToZZTo2e2tau_UL2016APV': 5,'GluGluToContinToZZTo2mu2nu_UL2016APV': 6,'GluGluToContinToZZTo4mu_UL2016APV': 7,'GluGluToContinToZZTo2mu2tau_UL2016APV': 8,'GluGluToContinToZZTo2tau2nu_UL2016APV': 9,'GluGluToContinToZZTo4tau_UL2016APV': 10,'GluGluToContinToZZTo2e2nu_UL2016APV': 11,'TT_UL2016APV': 12,'TT_SemiLep_UL2016APV': 13,'TT_Had_UL2016APV': 14,'TTTo2L2Nu_UL2016APV': 15,'TT_beff_UL2016APV': 16,'TVX_UL2016APV': 17,'TTGJets_UL2016APV': 18,'TTZToQQ_UL2016APV': 19,'TTZToLLNuNu_UL2016APV': 20,'TTWJetsToQQ_UL2016APV': 21,'TTWJetsToLNu_UL2016APV': 22,'tZq_ll_4f_UL2016APV': 23,'VG_UL2016APV': 24,'ZG_UL2016APV': 25,'WG_UL2016APV': 26,'WrongSign_UL2016APV': 27,'WWto2L2Nu_UL2016APV': 28,'GluGluToWWToENEN_UL2016APV': 29,'GluGluToWWToENMN_UL2016APV': 30,'GluGluToWWToENTN_UL2016APV': 31,'GluGluToWWToMNEN_UL2016APV': 32,'GluGluToWWToMNMN_UL2016APV': 33,'GluGluToWWToMNTN_UL2016APV': 34,'GluGluToWWToTNEN_UL2016APV': 35,'GluGluToWWToTNMN_UL2016APV': 36,'GluGluToWWToTNTN_UL2016APV': 37,'ST_tW_top_UL2016APV': 38,'ST_tW_antitop_UL2016APV': 39,'GluGluHToWWTo2L2Nu_UL2016APV': 40,'GluGluHToWWToLNuQQ_UL2016APV': 41,'GluGluHToZZTo4L_UL2016APV': 42,'GluGluHToTauTau_UL2016APV': 43,'VBFHToWWTo2L2Nu_UL2016APV': 44,'VBFHToTauTau_UL2016APV': 45,'ttHToNonbb_UL2016APV': 46,'VHToNonbb_UL2016APV': 47,'Triboson_UL2016APV': 48,'WWTo2L2Nu_DoubleScattering_UL2016': 49,'WWW_4F_UL2016APV': 50,'WWZ_4F_UL2016APV': 51,'WZZ_UL2016APV': 52,'ZZZ_UL2016APV': 53,'WWG_UL2016APV': 54,'WJets_UL2016APV': 55,'WJetsHT70to100_UL2016APV': 56,'WJetsHT100to200_UL2016APV': 57,'WJetsHT200to400_UL2016APV': 58,'WJetsHT400to600_UL2016APV': 59,'WJetsHT600to800_UL2016APV': 60,'WJetsHT800to1200_UL2016APV': 61,'WJetsHT1200to2500_UL2016APV': 62,'WJetsHT2500toInf_UL2016APV': 63,'WZ_UL2016APV': 64,'DYJetsToLL_UL2016APV': 65,'DYJetsToLL_FxFx_UL2016APV': 65,'DYJetsToLL_M10to50_UL2016APV': 66,'DYJetsToLL_M50_UL2016APV': 67,'DYJetsToLL_M50_FxFx_UL2016APV': 67,'DYJetsToLL_M50_UL2016APV_ext': 67,'WpWpJJ_EWK_UL2016APV': 68,'WpWpJJ_QCD_UL2016APV': 69,'VBS_SSWW_SM_UL2016APV': 70,'VBS_SSWW_LL_SM_UL2016APV': 71,'VBS_SSWW_TL_SM_UL2016APV': 72,'VBS_SSWW_TT_SM_UL2016APV': 73,'VBS_SSWW_cW_UL2016APV': 74,'VBS_SSWW_cW_SM_UL2016APV': 75,'VBS_SSWW_cW_BSM_UL2016APV': 76,'VBS_SSWW_cW_INT_UL2016APV': 77,'VBS_SSWW_cHW_UL2016APV': 78,'VBS_SSWW_cHW_SM_UL2016APV': 79,'VBS_SSWW_cHW_BSM_UL2016APV': 80,'VBS_SSWW_cHW_INT_UL2016APV': 81,'VBS_SSWW_cW_cHW_UL2016APV': 82,'VBS_SSWW_DIM6_UL2016APV': 83,'VBS_SSWW_DIM6_SM_UL2016APV': 84,'ZZtoLep_UL2016': 85,'ZZTo2L2Nu_UL2016': 86,'ZZTo4L_UL2016': 87,'GluGluToContinToZZTo4e_UL2016': 88,'GluGluToContinToZZTo2e2mu_UL2016': 89,'GluGluToContinToZZTo2e2tau_UL2016': 90,'GluGluToContinToZZTo2mu2nu_UL2016': 91,'GluGluToContinToZZTo4mu_UL2016': 92,'GluGluToContinToZZTo2mu2tau_UL2016': 93,'GluGluToContinToZZTo2tau2nu_UL2016': 94,'GluGluToContinToZZTo4tau_UL2016': 95,'GluGluToContinToZZTo2e2nu_UL2016': 96,'TT_UL2016': 97,'TT_SemiLep_UL2016': 98,'TT_Had_UL2016': 99,'TTTo2L2Nu_UL2016': 100,'TT_beff_UL2016': 101,'TVX_UL2016': 102,'TTGJets_UL2016': 103,'TTZToQQ_UL2016': 104,'TTZToLLNuNu_UL2016': 105,'TTWJetsToQQ_UL2016': 106,'TTWJetsToLNu_UL2016': 107,'tZq_ll_4f_UL2016': 108,'VG_UL2016': 109,'ZG_UL2016': 110,'WG_UL2016': 111,'WrongSign_UL2016': 112,'WWto2L2Nu_UL2016': 113,'GluGluToWWToENEN_UL2016': 114,'GluGluToWWToENMN_UL2016': 115,'GluGluToWWToENTN_UL2016': 116,'GluGluToWWToMNEN_UL2016': 117,'GluGluToWWToMNMN_UL2016': 118,'GluGluToWWToMNTN_UL2016': 119,'GluGluToWWToTNEN_UL2016': 120,'GluGluToWWToTNMN_UL2016': 121,'GluGluToWWToTNTN_UL2016': 122,'ST_tW_top_UL2016': 123,'ST_tW_antitop_UL2016': 124,'GluGluHToWWTo2L2Nu_UL2016': 125,'GluGluHToWWToLNuQQ_UL2016': 126,'GluGluHToZZTo4L_UL2016': 127,'GluGluHToTauTau_UL2016': 128,'VBFHToWWTo2L2Nu_UL2016': 129,'VBFHToTauTau_UL2016': 130,'ttHToNonbb_UL2016': 131,'VHToNonbb_UL2016': 132,'Triboson_UL2016': 133,'WWW_4F_UL2016': 134,'WWZ_4F_UL2016': 135,'WZZ_UL2016': 136,'ZZZ_UL2016': 137,'WWG_UL2016': 138,'WJets_UL2016': 139,'WJetsHT70to100_UL2016': 140,'WJetsHT100to200_UL2016': 141,'WJetsHT200to400_UL2016': 142,'WJetsHT400to600_UL2016': 143,'WJetsHT600to800_UL2016': 144,'WJetsHT800to1200_UL2016': 145,'WJetsHT1200to2500_UL2016': 146,'WJetsHT2500toInf_UL2016': 147,'WZ_UL2016': 148,'DYJetsToLL_UL2016': 149,'DYJetsToLL_FxFx_UL2016': 149,'DYJetsToLL_M10to50_UL2016': 150,'DYJetsToLL_M50_UL2016': 151,'DYJetsToLL_M50_FxFx_UL2016': 151,'DYJetsToLL_M50_UL2016_ext': 151,'WpWpJJ_EWK_UL2016': 152,'WpWpJJ_QCD_UL2016': 153,'VBS_SSWW_SM_UL2016': 154,'VBS_SSWW_LL_SM_UL2016': 155,'VBS_SSWW_TL_SM_UL2016': 156,'VBS_SSWW_TT_SM_UL2016': 157,'VBS_SSWW_cW_UL2016': 158,'VBS_SSWW_cW_SM_UL2016': 159,'VBS_SSWW_cW_BSM_UL2016': 160,'VBS_SSWW_cW_INT_UL2016': 161,'VBS_SSWW_cHW_UL2016': 162,'VBS_SSWW_cHW_SM_UL2016': 163,'VBS_SSWW_cHW_BSM_UL2016': 164,'VBS_SSWW_cHW_INT_UL2016': 165,'VBS_SSWW_cW_cHW_UL2016': 166,'VBS_SSWW_DIM6_UL2016': 167,'VBS_SSWW_DIM6_SM_UL2016': 168,'ZZtoLep_UL2017': 169,'ZZTo2L2Nu_UL2017': 170,'ZZTo4L_UL2017': 171,'GluGluToContinToZZTo4e_UL2017': 172,'GluGluToContinToZZTo2e2mu_UL2017': 173,'GluGluToContinToZZTo2e2tau_UL2017': 174,'GluGluToContinToZZTo2mu2nu_UL2017': 175,'GluGluToContinToZZTo4mu_UL2017': 176,'GluGluToContinToZZTo2mu2tau_UL2017': 177,'GluGluToContinToZZTo2tau2nu_UL2017': 178,'GluGluToContinToZZTo4tau_UL2017': 179,'GluGluToContinToZZTo2e2nu_UL2017': 180,'TT_UL2017': 181,'TT_SemiLep_UL2017': 182,'TT_Had_UL2017': 183,'TTTo2L2Nu_UL2017': 184,'TT_beff_UL2017': 185,'TVX_UL2017': 186,'TTGJets_UL2017': 187,'TTZToQQ_UL2017': 188,'TTZToLLNuNu_UL2017': 189,'TTWJetsToQQ_UL2017': 190,'TTWJetsToLNu_UL2017': 191,'tZq_ll_4f_UL2017': 192,'VG_UL2017': 193,'ZG_UL2017': 194,'WG_UL2017': 195,'WrongSign_UL2017': 196,'WWto2L2Nu_UL2017': 197,'GluGluToWWToENEN_UL2017': 198,'GluGluToWWToENMN_UL2017': 199,'GluGluToWWToENTN_UL2017': 200,'GluGluToWWToMNEN_UL2017': 201,'GluGluToWWToMNMN_UL2017': 202,'GluGluToWWToMNTN_UL2017': 203,'GluGluToWWToTNEN_UL2017': 204,'GluGluToWWToTNMN_UL2017': 205,'GluGluToWWToTNTN_UL2017': 206,'ST_tW_top_UL2017': 207,'ST_tW_antitop_UL2017': 208,'GluGluHToWWTo2L2Nu_UL2017': 209,'GluGluHToWWToLNuQQ_UL2017': 210,'GluGluHToZZTo4L_UL2017': 211,'GluGluHToTauTau_UL2017': 212,'VBFHToWWTo2L2Nu_UL2017': 213,'VBFHToTauTau_UL2017': 214,'ttHToNonbb_UL2017': 215,'VHToNonbb_UL2017': 216,'Triboson_UL2017': 217,'WWTo2L2Nu_DoubleScattering_UL2017': 218,'WWW_4F_UL2017': 219,'WWZ_4F_UL2017': 220,'WZZ_UL2017': 221,'ZZZ_UL2017': 222,'WWG_UL2017': 223,'WJets_UL2017': 224,'WJetsHT70to100_UL2017': 225,'WJetsHT100to200_UL2017': 226,'WJetsHT200to400_UL2017': 227,'WJetsHT400to600_UL2017': 228,'WJetsHT600to800_UL2017': 229,'WJetsHT800to1200_UL2017': 230,'WJetsHT1200to2500_UL2017': 231,'WJetsHT2500toInf_UL2017': 232,'WZ_UL2017': 233,'DYJetsToLL_UL2017': 234,'DYJetsToLL_FxFx_UL2017': 234,'DYJetsToLL_M10to50_UL2017': 235,'DYJetsToLL_M50_UL2017': 236,'DYJetsToLL_M50_FxFx_UL2017': 236,'DYJetsToLL_M50_UL2017_ext': 236,'WpWpJJ_EWK_UL2017': 237,'WpWpJJ_QCD_UL2017': 238,'VBS_SSWW_SM_UL2017': 239,'VBS_SSWW_LL_SM_UL2017': 240,'VBS_SSWW_TL_SM_UL2017': 241,'VBS_SSWW_TT_SM_UL2017': 242,'VBS_SSWW_cW_UL2017': 243,'VBS_SSWW_cW_SM_UL2017': 244,'VBS_SSWW_cW_BSM_UL2017': 245,'VBS_SSWW_cW_INT_UL2017': 246,'VBS_SSWW_cHW_UL2017': 247,'VBS_SSWW_cHW_SM_UL2017': 248,'VBS_SSWW_cHW_BSM_UL2017': 249,'VBS_SSWW_cHW_INT_UL2017': 250,'VBS_SSWW_cW_cHW_UL2017': 251,'VBS_SSWW_DIM6_UL2017': 252,'VBS_SSWW_DIM6_SM_UL2017': 253,'ZZtoLep_UL2018': 254,'ZZTo2L2Nu_UL2018': 255,'ZZTo4L_UL2018': 256,'GluGluToContinToZZTo4e_UL2018': 257,'GluGluToContinToZZTo2e2mu_UL2018': 258,'GluGluToContinToZZTo2e2tau_UL2018': 259,'GluGluToContinToZZTo2mu2nu_UL2018': 260,'GluGluToContinToZZTo4mu_UL2018': 261,'GluGluToContinToZZTo2mu2tau_UL2018': 262,'GluGluToContinToZZTo2tau2nu_UL2018': 263,'GluGluToContinToZZTo4tau_UL2018': 264,'GluGluToContinToZZTo2e2nu_UL2018': 265,'TT_UL2018': 266,'TT_SemiLep_UL2018': 267,'TT_Had_UL2018': 268,'TTTo2L2Nu_UL2018': 269,'TT_beff_UL2018': 270,'TVX_UL2018': 271,'TTGJets_UL2018': 272,'TTZToQQ_UL2018': 273,'TTZToLLNuNu_UL2018': 274,'TTWJetsToQQ_UL2018': 275,'TTWJetsToLNu_UL2018': 276,'tZq_ll_4f_UL2018': 277,'VG_UL2018': 278,'ZG_UL2018': 279,'WG_UL2018': 280,'WrongSign_UL2018': 281,'WWto2L2Nu_UL2018': 282,'GluGluToWWToENEN_UL2018': 283,'GluGluToWWToENMN_UL2018': 284,'GluGluToWWToENTN_UL2018': 285,'GluGluToWWToMNEN_UL2018': 286,'GluGluToWWToMNMN_UL2018': 287,'GluGluToWWToMNTN_UL2018': 288,'GluGluToWWToTNEN_UL2018': 289,'GluGluToWWToTNMN_UL2018': 290,'GluGluToWWToTNTN_UL2018': 291,'ST_tW_top_UL2018': 292,'ST_tW_antitop_UL2018': 293,'GluGluHToWWTo2L2Nu_UL2018': 294,'GluGluHToWWToLNuQQ_UL2018': 295,'GluGluHToZZTo4L_UL2018': 296,'GluGluHToTauTau_UL2018': 297,'VBFHToWWTo2L2Nu_UL2018': 298,'VBFHToTauTau_UL2018': 299,'ttHToNonbb_UL2018': 300,'VHToNonbb_UL2018': 301,'Triboson_UL2018': 302,'WWTo2L2Nu_DoubleScattering_UL2018': 303,'WWW_4F_UL2018': 304,'WWZ_4F_UL2018': 305,'WZZ_UL2018': 306,'ZZZ_UL2018': 307,'WWG_UL2018': 308,'WJets_UL2018': 309,'WJetsHT70to100_UL2018': 310,'WJetsHT100to200_UL2018': 311,'WJetsHT200to400_UL2018': 312,'WJetsHT400to600_UL2018': 313,'WJetsHT600to800_UL2018': 314,'WJetsHT800to1200_UL2018': 315,'WJetsHT1200to2500_UL2018': 316,'WJetsHT2500toInf_UL2018': 317,'WZ_UL2018': 318,'DYJetsToLL_UL2018': 319,'DYJetsToLL_FxFx_UL2018': 319,'DYJetsToLL_M10to50_UL2018': 320,'DYJetsToLL_M50_UL2018': 321,'DYJetsToLL_M50_FxFx_UL2018': 321,'DYJetsToLL_M50_UL2018_ext': 321,'WpWpJJ_EWK_UL2018': 322,'WpWpJJ_QCD_UL2018': 323,'VBS_SSWW_SM_UL2018': 324,'VBS_SSWW_LL_SM_UL2018': 325,'VBS_SSWW_TL_SM_UL2018': 326,'VBS_SSWW_TT_SM_UL2018': 327,'VBS_SSWW_cW_UL2018': 328,'VBS_SSWW_cW_BSM_UL2018': 329,'VBS_SSWW_cW_SM_UL2018': 330,'VBS_SSWW_cW_INT_UL2018': 331,'VBS_SSWW_cHW_UL2018': 332,'VBS_SSWW_cHW_SM_UL2018': 333,'VBS_SSWW_cHW_BSM_UL2018': 334,'VBS_SSWW_cHW_INT_UL2018': 335,'VBS_SSWW_cW_cHW_UL2018': 336,'VBS_SSWW_DIM6_UL2018': 337,'VBS_SSWW_DIM6_SM_UL2018': 338,'DataMu_UL2016APV': 339,'DataMuB1_UL2016APV': 340,'DataMuB2_UL2016APV': 341,'DataMuC_UL2016APV': 342,'DataMuD_UL2016APV': 343,'DataMuE_UL2016APV': 344,'DataMuF_UL2016APV': 345,'DataMu_UL2016': 346,'DataMuF_UL2016': 347,'DataMuG_UL2016': 348,'DataMuH_UL2016': 349,'DataMu_UL2017': 350,'DataMuB_UL2017': 351,'DataMuC_UL2017': 352,'DataMuD_UL2017': 353,'DataMuE_UL2017': 354,'DataMuF_UL2017': 355,'DataMu_UL2018': 356,'DataMuA_UL2018': 357,'DataMuB_UL2018': 358,'DataMuC_UL2018': 359,'DataMuD_UL2018': 360,'DataEle_UL2016APV': 361,'DataEleB1_UL2016APV': 362,'DataEleB2_UL2016APV': 363,'DataEleC_UL2016APV': 364,'DataEleD_UL2016APV': 365,'DataEleE_UL2016APV': 366,'DataEleF_UL2016APV': 367,'DataEle_UL2016': 368,'DataEleF_UL2016': 369,'DataEleG_UL2016': 370,'DataEleH_UL2016': 371,'DataEle_UL2017': 372,'DataEleB_UL2017': 373,'DataEleC_UL2017': 374,'DataEleD_UL2017': 375,'DataEleE_UL2017': 376,'DataEleF_UL2017': 377,'DataEle_UL2018': 378,'DataEleA_UL2018': 379,'DataEleB_UL2018': 380,'DataEleC_UL2018': 381,'DataEleD_UL2018': 382,'DataHT_UL2016APV': 383,'DataHTB1_UL2016APV': 384,'DataHTB2_UL2016APV': 385,'DataHTC_UL2016APV': 386,'DataHTD_UL2016APV': 387,'DataHTE_UL2016APV': 388,'DataHTF_UL2016APV': 389,'DataHT_UL2016': 390,'DataHTF_UL2016': 391,'DataHTG_UL2016': 392,'DataHTH_UL2016': 393,'DataHT_UL2017': 394,'DataHTB_UL2017': 395,'DataHTC_UL2017': 396,'DataHTD_UL2017': 397,'DataHTE_UL2017': 398,'DataHTF_UL2017': 399,'DataHT_UL2018': 400,'DataHTA_UL2018': 401,'DataHTB_UL2018': 402,'DataHTC_UL2018': 403,'DataHTD_UL2018': 404,'SampleHTFake_UL2016APV': 405,'SampleHTFake_UL2016': 406,'SampleHTFake_UL2017': 407,'SampleHTFake_UL2018': 408,}

aggregated_samples_UL2017 = {
    'VG':  [ZG_UL2017, WG_UL2017],
    'TVX': [TTGJets_UL2017, TTZToQQ_UL2017, TTZToLLNuNu_UL2017, TTWJetsToQQ_UL2017, TTWJetsToLNu_UL2017, tZq_ll_4f_UL2017],
    'Triboson': [WWW_4F_UL2017, WWZ_4F_UL2017, WZZ_UL2017, ZZZ_UL2017, WWG_UL2017],
    'TTTo2L2Nu': [TTTo2L2Nu_UL2017],
    'WZ': [WZ_UL2017],
    'DYJetsToLL_FxFx': [DYJetsToLL_M50_FxFx_UL2017],
    'WrongSign': [WWto2L2Nu_UL2017, GluGluToWWToENEN_UL2017, GluGluToWWToENMN_UL2017, GluGluToWWToENTN_UL2017, GluGluToWWToMNEN_UL2017, GluGluToWWToMNMN_UL2017, GluGluToWWToMNTN_UL2017, GluGluToWWToTNEN_UL2017,
                GluGluToWWToTNMN_UL2017,
                GluGluToWWToTNTN_UL2017, ST_tW_top_UL2017,
                ST_tW_antitop_UL2017,
                GluGluHToWWTo2L2Nu_UL2017,
                GluGluHToZZTo4L_UL2017, GluGluHToTauTau_UL2017, VBFHToWWTo2L2Nu_UL2017, VBFHToTauTau_UL2017, ttHToNonbb_UL2017, VHToNonbb_UL2017
    ],
    'ZZtoLep': [ZZTo2L2Nu_UL2017, ZZTo4L_UL2017, GluGluToContinToZZTo2e2nu_UL2017, GluGluToContinToZZTo2e2mu_UL2017, GluGluToContinToZZTo2e2tau_UL2017, GluGluToContinToZZTo2mu2nu_UL2017, GluGluToContinToZZTo2mu2tau_UL2017, GluGluToContinToZZTo4e_UL2017, GluGluToContinToZZTo4mu_UL2017, GluGluToContinToZZTo4tau_UL2017],
    'VBS_SSWW_SM': [VBS_SSWW_LL_SM_UL2017, VBS_SSWW_TL_SM_UL2017, VBS_SSWW_TT_SM_UL2017],
}

aggregated_samples = aggregated_samples_UL2017

# The txt files are "file:///scratch/cms/"...
def read_lines_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

chain = read_lines_from_file('chain.txt')
chain_gluglu = read_lines_from_file('chain_gluglu.txt')
chain_WZ = read_lines_from_file('chain_WZ.txt')

if redirector != "":
    chain = [path.replace("file:///scratch/cms/", redirector) for path in chain]
    chain_gluglu = [path.replace("file:///scratch/cms/", redirector) for path in chain_gluglu]
    chain_WZ = [path.replace("file:///scratch/cms/", redirector) for path in chain_WZ]

print(chain[0])
print(chain_gluglu[0])
print(chain_WZ[0])

branchlist = [
    
    "nLHEPdfWeight",
    "LHEPdfWeight",
    "nLHEScaleWeight",
    "LHEScaleWeight",
    
    "Generator_weight",
    "nPSWeight",
    "PSWeight",
    
    "Sample",
    
    "HLT_IsoMu27",
    "HLT_Ele35_WPTight_Gsf",
    "HLT_Mu50",
    "HLT_Ele32_WPTight_Gsf_L1DoubleEG",
    "HLT_Photon200",
    "HLT_PFHT250",
    "HLT_PFHT350",
    
    "nJet",
    "Jet_jetId",
    "Jet_eta",
    "Jet_pt",
    "Jet_puId",
    "Jet_phi",
    "Jet_mass",
    "Jet_partonFlavour",
    "Jet_btagDeepFlavB",
    "Jet_btagSF_deepjet_M_up",
    "Jet_btagSF_deepjet_M_down",
    "Jet_btagSF_deepjet_M",
    "Jet_btagDeepB",
    
    "nElectron",
    "Electron_pt",
    "Electron_eta",
    "Electron_phi",
    "Electron_mass",
    "Electron_jetRelIso",
    "Electron_mvaFall17V2Iso_WPL",
    "Electron_mvaFall17V2Iso_WP90",
    "Electron_pdgId",
    "Electron_genPartFlav",
    "Electron_charge",
    
    "nMuon",
    "Muon_corrected_pt",
    "Muon_eta",
    "Muon_phi",
    "Muon_mass",
    "Muon_tightId",
    "Muon_looseId",
    "Muon_pfRelIso04_all",
    "Muon_pdgId",
    "Muon_genPartFlav",
    "Muon_charge",
    
    "nTau",
    "Tau_pt",
    "Tau_eta",
    "Tau_phi",
    "Tau_idDeepTau2017v2p1VSjet",
    "Tau_idDeepTau2017v2p1VSe",
    "Tau_idDeepTau2017v2p1VSmu",
    "Tau_mass",
    "Tau_charge",
    "Tau_leadTkPtOverTauPt",
    "Tau_decayMode",
    "Tau_neutralIso",
    "Tau_genPartFlav",
    "Tau_jetIdx",
    
    "Electron_effSF",
    "Muon_effSF",
    "Electron_effSF_errUp",
    "Muon_effSF_errUp",
    "Electron_effSF_errDown",
    "Muon_effSF_errDown",
    
    "Jet_pt_nom",
    "Jet_pt_jerDown",
    "Jet_pt_jerUp",
    "Jet_pt_jesTotalDown",
    "Jet_pt_jesTotalUp",
    "Jet_mass_nom",
    "Jet_mass_jerDown",
    "Jet_mass_jerUp",
    "Jet_mass_jesTotalDown",
    "Jet_mass_jesTotalUp",
    
    "MET_T1Smear_pt",
    "MET_T1Smear_pt_jerDown",
    "MET_T1Smear_pt_jerUp",
    "MET_T1Smear_pt_jesTotalDown",
    "MET_T1Smear_pt_jesTotalUp",
    "MET_T1Smear_phi",
    "MET_T1Smear_phi_jerDown",
    "MET_T1Smear_phi_jerUp",
    "MET_T1Smear_phi_jesTotalDown",
    "MET_T1Smear_phi_jesTotalUp",
    
    "PrefireWeight",
    "PrefireWeight_Down",
    "PrefireWeight_Up",
    "puWeight",
    "puWeightDown",
    "puWeightUp",
    
    "Tau_rawDeepTau2017v2p1VSjet",
    "Tau_rawDeepTau2017v2p1VSe",
    "Tau_rawDeepTau2017v2p1VSmu",
    "Tau_leadTkDeltaPhi",
]

def execute_MC(chain, branchlist_, outFilePath = "./preselectionUL.root", outTreeName = "Events",  nPart = nPartitions, useFlag_BadPFMuonDzFilter = True, LHE = True, label = "distrdf" ):
    if distributed == True:
        #df = RDataFrame("Events", chain, npartitions=nPart, daskclient=client, monitor_label = label)  #when using root version with monitoring features (/cvmfs/images.dodas.infn.it/registry.hub.docker.com/dodasts/root-in-docker:ubuntu22-kernel-v1-monitoring)
        df = RDataFrame("Events", chain, npartitions=nPart, daskclient=client)  #when using standard root versions

    else:
        #df = delayed(RDataFrame)("Events", chain)
        df = RDataFrame("Events", chain) #to run on all
        #df = RDataFrame("Events", chain[0])

    df_year = df.DefinePerSample("Year","GetYear(rdfslot_, rdfsampleinfo_)")
    df_sample = df_year.DefinePerSample("Sample", "GetSample(rdfslot_, rdfsampleinfo_)")

    if useFlag_BadPFMuonDzFilter == True:
        df_METHLTFilter = df_sample.Define("METHLTFilter", "MET_HLT_Filter_UL2017(Year, Flag_goodVertices, Flag_HBHENoiseFilter, Flag_HBHENoiseIsoFilter, Flag_EcalDeadCellTriggerPrimitiveFilter, Flag_BadPFMuonFilter, Flag_globalSuperTightHalo2016Filter, HLT_IsoMu27, HLT_Mu50, HLT_OldMu100, HLT_TkMu100,  HLT_Ele35_WPTight_Gsf, HLT_Ele32_WPTight_Gsf_L1DoubleEG, HLT_Photon200, Flag_ecalBadCalibFilter, Flag_BadPFMuonDzFilter, L1_SingleIsoEG30er2p1, L1_SingleIsoEG32, L1_SingleEG40, Flag_eeBadScFilter)")\
                                .Filter("METHLTFilter == true", "MET HLT Filter")
        
    else:
        df_METHLTFilter = df_sample.Define("METHLTFilter", "MET_HLT_Filter_UL2017_nodz(Year, Flag_goodVertices, Flag_HBHENoiseFilter, Flag_HBHENoiseIsoFilter, Flag_EcalDeadCellTriggerPrimitiveFilter, Flag_BadPFMuonFilter, Flag_globalSuperTightHalo2016Filter, HLT_IsoMu27, HLT_Mu50, HLT_OldMu100, HLT_TkMu100,  HLT_Ele35_WPTight_Gsf, HLT_Ele32_WPTight_Gsf_L1DoubleEG, HLT_Photon200, Flag_ecalBadCalibFilter, L1_SingleIsoEG30er2p1, L1_SingleIsoEG32, L1_SingleEG40, Flag_eeBadScFilter)")\
                                .Filter("METHLTFilter == true", "MET HLT Filter")
    #### preselection #####
    df_preselection = df_METHLTFilter.Filter("PV_ndof> 4 && abs(PV_z) < 24 && hypot(PV_x, PV_y)<2", "Good vertex")\
                                    .Define("HT_eventHT", "GetEventHT(Jet_pt, Jet_eta, Jet_phi, Jet_mass)")\
                                    .Define("PassMinReq", "Pass_min_req(Muon_looseId, Muon_pt, Muon_pfRelIso04_all, Muon_eta, Electron_mvaFall17V2Iso_WPL, Electron_jetRelIso, Electron_pt, Electron_eta, Tau_idDeepTau2017v2p1VSjet, Tau_idDeepTau2017v2p1VSe, Tau_idDeepTau2017v2p1VSmu, Tau_pt, Tau_eta, Jet_pt, Jet_eta, Jet_puId)")\
                                    .Filter("PassMinReq == true", "Minimum requests")

    #### lepSF #####
    df_LepSF = df_preselection.Define("ElectronSFs", "ElectronSFs(Electron_pt, Electron_eta, Electron_pdgId, Year)")\
                            .Define("Electron_effSF", "getFlattenedMatrixColumn(ElectronSFs, 3, 0)")\
                            .Define("Electron_effSF_errUp", "getFlattenedMatrixColumn(ElectronSFs, 3, 1)")\
                            .Define("Electron_effSF_errDown", "getFlattenedMatrixColumn(ElectronSFs, 3, 2)")\
                            .Define("MuonSFs", "MuonSFs(Muon_pt, Muon_eta, Muon_pdgId, Year)")\
                            .Define("Muon_effSF", "getFlattenedMatrixColumn(MuonSFs, 3, 0)")\
                            .Define("Muon_effSF_errUp", "getFlattenedMatrixColumn(MuonSFs, 3, 1)")\
                            .Define("Muon_effSF_errDown", "getFlattenedMatrixColumn(MuonSFs, 3, 2)")

    #### puWeight #####
    #df_puWeight = df_mht
    df_puWeight = df_LepSF.Define("puWeights", "puWeight(Year, Pileup_nTrueInt)")\
                        .Define("puWeight", "puWeights[0]")\
                        .Define("puWeightUp", "puWeights[1]")\
                        .Define("puWeightDown", "puWeights[2]")

    #### prefCorr ####
    df_prefCorr = df_puWeight.Define("prefCorrs","PrefCorr(Photon_pt, Photon_eta, Photon_jetIdx, Photon_electronIdx, Electron_pt, Electron_eta, Electron_jetIdx, Electron_photonIdx, Jet_pt, Jet_eta)")\
                            .Define("PrefireWeight", "prefCorrs[0]")\
                            .Define("PrefireWeight_Up", "prefCorrs[1]")\
                            .Define("PrefireWeight_Down", "prefCorrs[2]")



    #### btagSF ##### preselection part2
    df_btagSF = df_prefCorr.Define("btagSFs",  'btagSF(Jet_pt, Jet_eta, Jet_hadronFlavour, Jet_btagDeepFlavB, Year, \"M\")')\
                    .Define("Jet_btagSF_deepjet_M", "getMatrixColumn(btagSFs, 0)")\
                    .Define("Jet_btagSF_deepjet_M_up", "getMatrixColumn(btagSFs, 1)")\
                    .Define("Jet_btagSF_deepjet_M_down", "getMatrixColumn(btagSFs, 2)")


    #### muonScaleRes ####
    df_muonScaleRes = df_btagSF.Define("muonCorrectedPTs", "muonScaleRes(Muon_pt, Muon_eta, Muon_phi, Muon_charge, Muon_nTrackerLayers, Muon_genPartIdx, GenPart_pt, Year)")\
                            .Define("Muon_corrected_pt", "getFlattenedMatrixColumn(muonCorrectedPTs, 3, 0)")\
                            .Define("Muon_correctedUp_pt", "getFlattenedMatrixColumn(muonCorrectedPTs, 3, 1)")\
                            .Define("Muon_correctedDown_pt", "getFlattenedMatrixColumn(muonCorrectedPTs, 3, 2)")


    #### metCorrector and fatJetCorrector #### ####
    df_jme = df_muonScaleRes.Define("jetVars", "myJetVarCalc.produce(Jet_pt, Jet_eta, Jet_phi, Jet_mass, Jet_rawFactor, Jet_area, Jet_partonFlavour, Jet_jetId, fixedGridRhoFastjetAll, (run<<20) + (luminosityBlock<<10) + event + 1 + int(Jet_eta[0]/.01), GenJet_pt, GenJet_eta, GenJet_phi, GenJet_mass)")\
                            .Define("Jet_pt_nom", "jetVars.pt(0)")\
                            .Define("Jet_mass_nom", "jetVars.mass(0)")\
                            .Define("metsVars", "myType1SmearMETVarCalc.produce(Jet_pt, Jet_eta, Jet_phi, Jet_mass, Jet_rawFactor, Jet_area, Jet_partonFlavour, Jet_muonSubtrFactor, Jet_neEmEF, Jet_chEmEF, Jet_jetId, fixedGridRhoFastjetAll, (run<<20) + (luminosityBlock<<10) + event + 1 + int(Jet_eta[0]/.01), GenJet_pt, GenJet_eta, GenJet_phi, GenJet_mass, RawMET_phi , RawMET_pt, MET_MetUnclustEnUpDeltaX, MET_MetUnclustEnUpDeltaY, CorrT1METJet_rawPt, CorrT1METJet_eta, CorrT1METJet_phi, CorrT1METJet_area, CorrT1METJet_muonSubtrFactor, {}, {})")\
                            .Define("MET_T1Smear_pt", "metsVars.pt(0)")\
                            .Define("MET_T1Smear_phi", "metsVars.phi(0)")

    #jetvariations = variations
    variations = jetvariations
    for n,v in enumerate(jetvariations[1:]):
        #print("Jet_pt_{}".format(v))
        if v in variations:
            #print("Jet_pt_{}".format(v))
            df_jme = df_jme.Define("Jet_pt_{}".format(v), "jetVars.pt({})".format(1+n)).Define("Jet_mass_{}".format(v), "jetVars.mass({})".format(1+n))
    for n,v in enumerate(mett1smearvariations[1:]):
        if v in variations:
            df_jme = df_jme.Define("MET_T1Smear_pt_{}".format(v), "metsVars.pt({})".format(1+n)).Define("MET_T1Smear_phi_{}".format(v), "metsVars.phi({})".format(1+n))
    
    ### book snapshot ####
    opts = ROOT.RDF.RSnapshotOptions()
    opts.fLazy = True

    if LHE == False:
        branches = branchlist_[4:]
    else:
        branches = branchlist_
    if distributed == True:
        df_jme_lazy = df_jme.Snapshot(outTreeName, outFilePath, branches, opts)
    else:
        df_jme_lazy = df_jme.Snapshot(outTreeName, outFilePath, branches, opts)
    counting = df_jme.Count()

    return df_jme_lazy

df_sn = execute_MC(chain, branchlist, outFilePath = "./preselectionUL.root", outTreeName = "Events", label = "main")
df_sn_gluglu = execute_MC(chain_gluglu, branchlist, outFilePath = "./preselectionUL_GluGlu.root",  outTreeName = "Events", nPart = 5, useFlag_BadPFMuonDzFilter = False, label = "gluglu")
df_sn_WZ = execute_MC(chain_WZ, branchlist, outFilePath = "./preselectionUL_WZ.root", outTreeName = "Events", nPart = 5,  useFlag_BadPFMuonDzFilter = True, LHE = False, label = "WZ")

if distributed == True:
    RunGraphs = ROOT.RDF.Experimental.Distributed.RunGraphs
else:
    RunGraphs = ROOT.RDF.RunGraphs

proxies = [
    df_sn,
    df_sn_gluglu,
    df_sn_WZ
]

RunGraphs(proxies)

dfs = [df_.GetValue() for df_ in proxies]
client.close()
