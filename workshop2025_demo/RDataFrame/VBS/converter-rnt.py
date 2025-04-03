import ROOT
import sys

# Ensure the script is run with the correct number of arguments
if len(sys.argv) != 4:
    print("Usage: python convert.py <input_file> <tree_name> <output_file>")
    sys.exit(1)

# Retrieve input arguments
input_file = sys.argv[1]
treename = sys.argv[2]
output_file = sys.argv[3]

# Reset the interpreter (optional, but helps avoid conflicts)
ROOT.gInterpreter.ProcessLine("gInterpreter->Reset()")

# Load the C++ function and header file in ROOT
ROOT.gInterpreter.Declare("""
#include <ROOT/RNTupleDS.hxx>
#include <ROOT/RNTupleImporter.hxx>
#include <ROOT/RNTupleReader.hxx>
#include <ROOT/RPageStorageFile.hxx>
#include <TFile.h>
#include <TROOT.h>
#include <TSystem.h>
#include <iostream>

using RNTupleImporter = ROOT::Experimental::RNTupleImporter;
using RNTupleReader = ROOT::Experimental::RNTupleReader;

void ConvertTTreeToRNTuple(const std::string &inputFileName, const std::string &treeName,
                           const std::string &outputFileName, const std::string &ntupleName = "Events"){
   gSystem->Unlink(outputFileName.c_str()); // Remove existing output file

   auto importer = RNTupleImporter::Create(inputFileName.c_str(), treeName.c_str(), outputFileName.c_str());
   importer->Import();

   auto file = std::unique_ptr<TFile>(TFile::Open(outputFileName.c_str()));
   if (!file || file->IsZombie()) {
      std::cerr << "cannot open " << outputFileName << std::endl;
      return;
   }

   auto ntpl = std::unique_ptr<ROOT::RNTuple>(file->Get<ROOT::RNTuple>("Events"));
   auto reader = RNTupleReader::Open(*ntpl);
   reader->PrintInfo();
}
""")

# Run the conversion function with the passed arguments
ROOT.ConvertTTreeToRNTuple(input_file, treename, output_file)

