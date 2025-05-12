# if __name__ == '__main__':
#     import ROOT
#     import os
#     from dask.distributed import Client, LocalCluster

#     nmaxpartitions = 30

#     text_file = open("utils.h", "r")
#     data = text_file.read()


#     def my_initialization_function():
#         ROOT.gInterpreter.Declare('{}'.format(data))


    #client = Client(address="tcp://127.0.0.1:"+str(sched_port))
    # client = LocalCluster(threads_per_worker=1, n_workers=10).get_client() #, processes=False
    # ROOT.RDF.Experimental.Distributed.initialize(my_initialization_function)

    # chain = [
    #         #"root://eospublic.cern.ch//eos/root-eos/benchmark/CMSOpenDataHiggsTauTau/W1JetsToLNu.root",
    #         "root://eospublic.cern.ch//eos/root-eos/benchmark/CMSOpenDataHiggsTauTau/W2JetsToLNu.root",
    #         #"root://eospublic.cern.ch//eos/root-eos/benchmark/CMSOpenDataHiggsTauTau/W3JetsToLNu.root",
    #         ]

    # df = ROOT.RDF.Experimental.Distributed.Dask.RDataFrame("Events", chain, npartitions=nmaxpartitions, executor=client)   

    # df_varied = df.Vary("Muon_pt", "ROOT::VecOps::RVec<ROOT::VecOps::RVec<float>>{Muon_pt*0.8, Muon_pt*1.2}", variationTags=["down", "up"], variationName="dummyVariation")

    # df_atleast2Jets = df_varied.Filter("nJet>=2", "At least two jets")
    # df_GoodJets = df_atleast2Jets.Define("GoodJets_idx", "GoodJets(Jet_eta, Jet_pt, Jet_puId)")
    # df_atleast2GoodJets = df_GoodJets.Filter("atleast2GoodJets(GoodJets_idx)", "At least two good jets")
    # df_VBSjets = df_atleast2GoodJets.Define("VBSJet_idx", "SelectVBSJets_invmass(Jet_pt, Jet_eta, Jet_phi, Jet_mass, GoodJets_idx)")
    # df_2VBSjets = df_VBSjets.Filter("VBSJet_idx[0] != VBSJet_idx[1]", "2 VBS jets")
    # df_jetsDefinitions = df_2VBSjets.Define("leadjet_pt", "Jet_pt[VBSJet_idx[0]]")\
    #                                 .Define("leadjet_eta", "Jet_eta[VBSJet_idx[0]]")\
    #                                 .Define("leadjet_phi", "Jet_phi[VBSJet_idx[0]]")\
    #                                 .Define("leadjet_mass", "Jet_mass[VBSJet_idx[0]]")\
    #                                 .Define("subleadjet_pt", "Jet_pt[VBSJet_idx[1]]")\
    #                                 .Define("subleadjet_eta", "Jet_eta[VBSJet_idx[1]]")\
    #                                 .Define("subleadjet_phi", "Jet_phi[VBSJet_idx[1]]")\
    #                                 .Define("subleadjet_mass", "Jet_mass[VBSJet_idx[1]]")\

    # df_selectMuon = df_jetsDefinitions.Define("Muon_idx", "SelectMuon(Muon_pt, Muon_eta, Muon_phi, Jet_eta, Jet_phi, VBSJet_idx)")
    # df_compatibleLeptons = df_selectMuon.Filter("Muon_idx[1] != -1", "Filter on leptons")
    # df_leptonDefinitions = df_compatibleLeptons.Define("lepton_pt", "Muon_pt[Muon_idx[0]]")\
    #                                            .Define("lepton_eta", "Muon_eta[Muon_idx[0]]")\
    #                                            .Define("lepton_phi", " Muon_phi[Muon_idx[0]]")\
    #                                            .Define("lepton_mass", "Muon_mass[Muon_idx[0]]")\

    # df_selectTau = df_leptonDefinitions.Define("Tau_idx", "SelectAndVetoTaus(Tau_pt, Tau_eta, Tau_phi, Muon_idx, Muon_eta, Muon_phi, Jet_eta, Jet_phi, VBSJet_idx)")
    # df_1tau = df_selectTau.Filter("Tau_idx[1] != -1", "Exactly 1 Tau")
    # df_tauDefinitions = df_1tau.Define("tau_pt", "Tau_pt[Tau_idx[0]]")\
    #                            .Define("tau_eta", "Tau_eta[Tau_idx[0]]")\
    #                            .Define("tau_phi", "Tau_phi[Tau_idx[0]]")\
    #                            .Define("tau_mass", "Tau_mass[Tau_idx[0]]")\

    # df_selection = df_tauDefinitions.Define("m_jjtaulep","GetInvMass(leadjet_pt, leadjet_eta, leadjet_phi, leadjet_mass, subleadjet_pt, subleadjet_eta, subleadjet_phi, subleadjet_mass, tau_pt, tau_eta, tau_phi, tau_mass, lepton_pt, lepton_eta, lepton_phi, lepton_mass)")

    # h = df.Histo1D(("m_jjtaulep", "" , 10, 0, 3000), "nJet") #df_selection m_jjtaulep

    # h_varied = ROOT.RDF.Experimental.Distributed.VariationsFor(h)

    # c = ROOT.TCanvas()
    # h_varied["dummyVariation:up"].SetLineColor(1)
    # h_varied["dummyVariation:up"].Draw()
    # h_varied["nominal"].SetLineColor(2)
    # h_varied["nominal"].Draw('SAME')
    # h_varied["dummyVariation:down"].SetLineColor(3)
    # h_varied["dummyVariation:down"].Draw('SAME')
    # c.Draw()


####################################################################################################
# Questa analisi dummy funziona
# if __name__ == '__main__':
#     import requests
#     import json
#     from dask.distributed import Client, LocalCluster
#     import dask

#     # Start Dask cluster
#     client = Client(LocalCluster(threads_per_worker=1, n_workers=4, memory_limit='2GB'))

#     df = dask.datasets.timeseries()
#     print(df)
#     print(df.dtypes)

#     # This sets some formatting parameters for displayed data.
#     import pandas as pd

#     pd.options.display.precision = 2
#     pd.options.display.max_rows = 10
#     print(df.head(3))

#     df2 = df[df.y > 0]
#     df3 = df2.groupby("name").x.std()

#     computed_df = df3.compute()
#     print(type(computed_df))

#     print(computed_df)

if __name__ == '__main__':
    import ROOT
    import os
    from dask.distributed import Client, LocalCluster, PipInstall, WorkerPlugin
    import json
    # from samplesUL import *
    import sys 
    from dask_jobqueue import HTCondorCluster
    from distributed.diagnostics.plugin import UploadFile

    distributed = True
    MT = False

    maxNfilespersample = 1 #5 lower this number just for debugging purposes: 99999 prod.
    nPartitions = 1*3  #used only in distributed mode (golden rule 3*Nworkers)

    file = ROOT.TFile("/shared-scratch/cms/store/mc/RunIISummer20UL17NanoAODv9/ZGToLLG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_mc2017_realistic_v9-v1/70000/AF4D5462-30E8-EA43-AA8A-A1EADA9796BC.root")

    # Access the TTree in the ROOT file
    tree = file.Get("Events")

    branchesss = tree.GetListOfBranches()
    branchlist = []

    # Edit to change number of branches read
    branches_size = 1

    for i, b in enumerate(branchesss):
        #if b.GetName() == "Muon_mass":
        #    branchlist.append(b.GetName())
        #    break
        if i <= branches_size:
            branchlist.append(b.GetName())
        else:
            break
            #continue

    print(len(branchlist))
    print(branchlist)

    RDataFrame = ROOT.RDF.Experimental.Distributed.Dask.RDataFrame
    client = LocalCluster(threads_per_worker=1, n_workers=1, processes=False).get_client()

    chain = ["/shared-scratch/cms/store/mc/RunIISummer20UL17NanoAODv9/ZGToLLG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_mc2017_realistic_v9-v1/70000/AF4D5462-30E8-EA43-AA8A-A1EADA9796BC.root"]

    def execute_MC(chain, branchlist_, outFilePath = "./preselectionUL.root", outTreeName = "Events",  nPart = nPartitions, useFlag_BadPFMuonDzFilter = True, LHE = True, label = "distrdf" ):
        if distributed == True:
            #df = RDataFrame("Events", chain, npartitions=nPart, daskclient=client, monitor_label = label)  #when using root version with monitoring features (/cvmfs/images.dodas.infn.it/registry.hub.docker.com/dodasts/root-in-docker:ubuntu22-kernel-v1-monitoring)
            df = RDataFrame("Events", chain, npartitions=nPart, daskclient=client)  #when using standard root versions
        
        df_new = df.Define("x", "27")

        ### book snapshot ####
        opts = ROOT.RDF.RSnapshotOptions()
        opts.fLazy = True

        if LHE == False:
            branches = branchlist_[4:]
        else:
            branches = branchlist_
        if distributed == True:
            df_lazy = df_new.Snapshot(outTreeName, outFilePath, branches, opts)
        
        return df_lazy

    df_sn = execute_MC(chain, branchlist, outFilePath = "./preselectionUL.root", outTreeName = "Events", label = "main") 

    if distributed == True:
        RunGraphs = ROOT.RDF.Experimental.Distributed.RunGraphs

    proxies = [
    df_sn
    ]

    RunGraphs(proxies)
    dfs = [df_.GetKeys() for df_ in proxies]

    # print(dfs.head(5))