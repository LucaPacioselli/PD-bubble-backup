import ROOT

# Define function to convert TTree to RNTuple
def ConvertTTreeToRNTuple(output_file_name="/scratch/cms/store/mcrnt//RunIISummer20UL17NanoAODv9/ZGToLLG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_mc2017_realistic_v9-v1/70000/5A4F28C9-C890-DD47-9104-AE667C1623E1.root", ntuple_name="Events"):
    file = ROOT.TFile.Open(output_file_name)
    if not file or file.IsZombie():
        print(f"Cannot open {output_file_name}")
        return
    
    ntpl = file.Get("Events")
    if not ntpl:
        print(f"No NTuple named '{ntuple_name}' found in file {output_file_name}")
        return
    
    reader = ROOT.ROOT.Experimental.RNTupleReader.Open(ntpl)
    reader.PrintInfo()

# Run the function
ConvertTTreeToRNTuple()
