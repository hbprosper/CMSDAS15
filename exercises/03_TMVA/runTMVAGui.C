void runTMVAGui(string rootfile="TMVA.root")
{
  TROOT::SetMacroPath("$HOME/CMSDAS15/tmva/test");
  gROOT->LoadMacro("$HOME/CMSDAS15/tmva/test/TMVAGui.C");
  TMVAGui(rootfile.c_str());
}
