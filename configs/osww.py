import hist
import awkward as ak
import numpy as np


name = "owss"
xs = 0.20933649499999987
lumi = 100.0  # fb^-1
reweight_card = "/gwpool/users/santonellini/eft/genproductions/bin/MadGraph5_aMCatNLO/folder_osww_dim6_cpodd/osww_dim6_cpodd_reweight_card.dat"
files_pattern = "/gwteras/cms/store/user/gpizzati/PrivateMC/triennali/osww/OSWW_dim6_cpodd/RunIISummer20UL18NanoAODv9_106X_upgrade2018_realistic_v11_nanoGEN_NANOAODSIM/240508_084113/*/*root"
limit_files = 5  # Use `None` to not limit files
nevents_per_file = 10000
nevents_per_job = 100000
ops = ["cWtil", "cHWtil", "cHWBtil", "cHBtil", "ctBIm", "ctWIm"]

particle_branches = ["pt", "eta", "phi", "mass", "pdgId", "status"]
branches = [f"LHEPart_{k}" for k in particle_branches] + [
    "genWeight",
    "LHEReweightingWeight",
]


def object_definitions(events):
    Particle = ak.zip(
        {k: events[f"LHEPart_{k}"] for k in particle_branches}, with_name="Momentum4D"
    )
    Particle = Particle[Particle.status == 1]
    events["Particle"] = Particle

    # Define MET
    neutrinos_gen = events.Particle[
        (
            (abs(events.Particle.pdgId) == 12)
            | (abs(events.Particle.pdgId) == 14)
            | (abs(events.Particle.pdgId) == 16)
        )
    ]
    # events["MET"] = neutrinos_gen[:, 0] + neutrinos_gen[:, 1]
    events["MET"] = ak.sum(neutrinos_gen, axis=1)

    # Remove neutrinos from particle
    events["Particle"] = events.Particle[
        (
            (abs(events.Particle.pdgId) != 12)
            & (abs(events.Particle.pdgId) != 14)
            & (abs(events.Particle.pdgId) != 16)
        )
    ]

    # Define leptons no tau
    events["Lepton"] = events.Particle[
        (abs(events.Particle.pdgId) == 11) | (abs(events.Particle.pdgId) == 13)
    ]
    # Remove events where nleptons != 2
    events = events[ak.num(events.Lepton) == 2]

    # Define Jets
    # Everything that is not Lepton or Neutrino
    events["Jet"] = events.Particle[
        (
            (abs(events.Particle.pdgId) != 11)
            & (abs(events.Particle.pdgId) != 12)
            & (abs(events.Particle.pdgId) != 13)
            & (abs(events.Particle.pdgId) != 14)
            & (abs(events.Particle.pdgId) != 15)
            & (abs(events.Particle.pdgId) != 16)
        )
    ]
    return events


def get_variables():
    return {
        "mjj": {
            "func": lambda events: (events.Jet[:, 0] + events.Jet[:, 1]).mass,
            "axis": hist.axis.Regular(15, 500, 3000, name="mjj"),
            "formatted": "m_{jj} \; [GeV]",
        },
        "mll": {
            "func": lambda events: (events.Lepton[:, 0] + events.Lepton[:, 1]).mass,
            "axis": hist.axis.Regular(30, 20, 3000, name="mll"),
            "formatted": "m_{ll} \; [GeV]",
        },
        "mjj:ptj1": {
            "func1": lambda events: (events.Jet[:, 0] + events.Jet[:, 1]).mass,
            "axis1": hist.axis.Regular(10, 200, 3000, name="mjj"),
            "func2": lambda events: events.Jet[:, 0].pt,
            "axis2": hist.axis.Regular(6, 30, 150, name="ptj1"),
            "formatted": "m_{jj}\,:\,p^T_{j1}",
        },
        "detajj": {
            "func": lambda events: abs(events.Jet[:, 0].deltaeta(events.Jet[:, 1])),
            "axis": hist.axis.Regular(15, 2.5, 8, name="detajj"),
            "formatted": "\Delta\eta_{jj}",
        },
        "dphijj": {
            "func": lambda events: abs(events.Jet[:, 0].deltaphi(events.Jet[:, 1])),
            "axis": hist.axis.Regular(30, 0, np.pi, name="dphijj"),
            "formatted": "\Delta\phi_{jj}",
        },
        "ptj1": {
            "func": lambda events: events.Jet[:, 0].pt,
            "axis": hist.axis.Regular(30, 30, 150, name="ptj1"),
            "formatted": "p^T_{j1} \; [GeV]",
        },
        "ptj2": {
            "func": lambda events: events.Jet[:, 1].pt,
            "axis": hist.axis.Regular(30, 30, 150, name="ptj2"),
            "formatted": "p^T_{j2} \; [GeV]",
        },
        "ptl1": {
            "func": lambda events: events.Lepton[:, 0].pt,
            "axis": hist.axis.Regular(30, 25, 150, name="ptl1"),
            "formatted": "p^T_{l1} \; [GeV]",
        },
        "ptl2": {
            "func": lambda events: events.Lepton[:, 1].pt,
            "axis": hist.axis.Regular(30, 20, 150, name="ptl2"),
            "formatted": "p^T_{l2} \; [GeV]",
        },
        "ptll": {
            "func": lambda events: (events.Lepton[:, 0] + events.Lepton[:, 1]).pt,
            "axis": hist.axis.Regular(30, 20, 2000, name="ptll"),
            "formatted": "p^T_{ll} \; [GeV]",
        },
        "etaj1": {
            "func": lambda events: events.Jet[:, 0].eta,
            "axis": hist.axis.Regular(30, 0, 5, name="etaj1"),
            "formatted": "\eta_{j1}",
        },
        "etaj2": {
            "func": lambda events: events.Jet[:, 1].eta,
            "axis": hist.axis.Regular(30, 0, 5, name="etaj2"),
            "formatted": "\eta_{j2}",
        },
        "etal1": {
            "func": lambda events: events.Lepton[:, 0].eta,
            "axis": hist.axis.Regular(30, 0, 2.5, name="etal1"),
            "formatted": "\eta_{l1}",
        },
        "etal2": {
            "func": lambda events: events.Lepton[:, 1].eta,
            "axis": hist.axis.Regular(30, 0, 2.5, name="etal2"),
            "formatted": "\eta_{l2}",
        },
        "phij1": {
            "func": lambda events: events.Jet[:, 0].phi,
            "axis": hist.axis.Regular(30, 0, np.pi, name="phij1"),
            "formatted": "\phi_{j1}",
        },
        "phij2": {
            "func": lambda events: events.Jet[:, 1].phi,
            "axis": hist.axis.Regular(30, 0, np.pi, name="phij2"),
            "formatted": "\phi_{j2}",
        },
        "events": {
            "func": lambda events: ak.ones_like(events.genWeight),
            "axis": hist.axis.Regular(1, 0, 2, name="events"),
        },
    }


def selections(events):
    return events[
        ((events.Jet[:, 0].pt > 30.0) & (events.Jet[:, 1].pt > 30.0))
        & (abs(events.detajj) >= 2.5)
        & (events.mjj >= 500)
        & (events.mll >= 20)
        & (events.ptl1 >= 25)
        & (events.ptl2 >= 20)
        & (events.ptj1 >= 30)
        & (events.ptj2 >= 30)
        & (abs(events.Jet[:, 0].eta) < 5)
        & (abs(events.Jet[:, 1].eta) < 5)
        & (abs(events.Lepton[:, 0].eta) < 2.5)
        & (abs(events.Lepton[:, 1].eta) < 2.5)
    ]
