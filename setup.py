import cx_Freeze
import sys
import matplotlib
import requests.certs
import pytz
## Currently True Skill Plots aren't working on the build.
base = None
if sys.platform == 'win32':
    base = "Win32GUI"

executables = [cx_Freeze.Executable("SacaSuRecord.py",
                                    base=base,
                                    icon = 'ngcc.ico')]

cx_Freeze.setup(
    name = "SacaSuRecord",
    options = {"build_exe":{
                            "packages":["tkinter",
                                        "requests",
                                        "os",
                                        "sys",
                                        "re",
                                        "bs4",
                                        "urllib",
                                        "matplotlib",
                                        "numpy",
                                        "scipy",
                                        "pytz",
                                        "datetime"],
                            "include_files":["LoadIn.txt",
                                             "TournamentClass.py",
                                             "ngcc.ico",
                                             "scraping_functions.py",
                                             "TrueSkillStart.py",
                                             "calcs.py",
                                             "smash_rankings_calculator.py",
                                             "MeleeDates.txt",
                                             "MeleeTournaments.txt",
                                             "names.txt",
                                             "update.py",
                                             'hmc_urllib.py',
                                             'MeleeResults/',
                                             'MeleeUrls/',
                                             requests.certs.where(),
                                             (pytz.__path__[0])]}},
    version = "0.06",
    description = "Smash.gg tournament sets extractor",
    executables = executables
    )
    
