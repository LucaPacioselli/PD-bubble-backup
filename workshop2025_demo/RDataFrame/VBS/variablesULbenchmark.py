# updated by hand
from array import array

'''
class variable(object):
    def __init__(self, name, title, nbins, xmin, xmax=None):
        self._name=name
        self._title=title
        self._nbins=nbins
        self._xmin=xmin
        if xmax==None:
            self._xmax=xmin[nbins]
            self._iscustom = True
        else:
            self._xmax=xmax
            self._iscustom = False
    def __str__(self):
        return  '\"'+str(self._name)+'\",\"'+str(self._title)+'\",\"'+str(self._taglio)+'\",'+str(self._nbins)+','+str(self._xmin)+','+str(self._xmax)
'''

class variable(object):
    def __init__(self, name, title, nbins, bins):
        self._name=name
        self._title=title
        self._nbins=nbins
        self._bins=bins
        self._iscustom = True
        self._xmin=bins
        self._xmax=bins[nbins] 
        
variables = {}

variables["SR"] = []
variables["SR"].append(variable('lepton_pt',  'Lepton p_{T} [GeV]', 7 , array("f", [0.,30., 45., 60., 80., 100., 150, 250.]) ))
variables["SR"].append(variable('tau_pt',  'Tau p_{T} [GeV]', 3 , array("f", [30., 45., 60., 100.])))
variables["SR"].append(variable('m_jj', 'Invarant mass JJ',  4, array("f", [500., 700., 1000., 1500., 2500.])))

variables["fakes_CR"] = []
variables["fakes_CR"].append(variable('lepton_pt',  'Lepton p_{T} [GeV]', 7 , array("f", [0., 30., 45., 60., 80., 100., 150, 250.]) ))
variables["fakes_CR"].append(variable('tau_pt',  'Tau p_{T} [GeV]', 3 , array("f", [30., 45., 60., 100.])))
variables["fakes_CR"].append(variable('m_jj', 'Invarant mass JJ',  6, array("f",  [0., 300., 500., 700., 1000., 1500., 2000.])))

variables["ttbar_CR"] = []
variables["ttbar_CR"].append(variable('lepton_pt',  'Lepton p_{T} [GeV]', 9 , array("f", [0., 30., 45., 60., 80., 100., 125., 150, 200., 250.]) ))
variables["ttbar_CR"].append(variable('tau_pt',  'Tau p_{T} [GeV]', 8 , array("f", [30., 45., 60., 80., 100., 125., 150, 200., 250.])))
variables["ttbar_CR"].append(variable('m_jj', 'Invarant mass JJ',  6, array("f", [0., 300., 500., 700., 1000., 1500., 2000.])))

variables["OS_CR_bvetoL"] = []
variables["OS_CR_bvetoL"].append(variable('lepton_pt',  'Lepton p_{T} [GeV]', 9 , array("f",  [0., 30., 45., 60., 80., 100., 125., 150, 200., 250.]) ))
variables["OS_CR_bvetoL"].append(variable('tau_pt',  'Tau p_{T} [GeV]', 8 , array("f", [30., 45., 60., 80., 100., 125., 150, 200., 250.])))
variables["OS_CR_bvetoL"].append(variable('m_jj', 'Invarant mass JJ',  6, array("f", [0., 300., 500., 700., 1000., 1500., 2000.])))
