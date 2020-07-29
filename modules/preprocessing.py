import numpy as np
import pandas as pd

import pubchempy as pcp
from chemdataextractor import Document

from mat2vec.processing.process import MaterialsTextProcessor

class PreProcessor():
    def __init__(self, type):
        """
        Parameters:
            type (str, required): type of text to be processed (abstracts or
                                  full text)
        """
    self.type = type
    self.ELEMENTS = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K",
                     "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr",
                     "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I",
                     "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
                     "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr",
                     "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr", "Rf",
                     "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og", "Uue"]

    self.ELEMENT_NAMES = ["hydrogen", "helium", "lithium", "beryllium", "boron", "carbon", "nitrogen", "oxygen", "fluorine",
                          "neon", "sodium", "magnesium", "aluminium", "silicon", "phosphorus", "sulfur", "chlorine", "argon",
                          "potassium", "calcium", "scandium", "titanium", "vanadium", "chromium", "manganese", "iron",
                          "cobalt", "nickel", "copper", "zinc", "gallium", "germanium", "arsenic", "selenium", "bromine",
                          "krypton", "rubidium", "strontium", "yttrium", "zirconium", "niobium", "molybdenum", "technetium",
                          "ruthenium", "rhodium", "palladium", "silver", "cadmium", "indium", "tin", "antimony", "tellurium",
                          "iodine", "xenon", "cesium", "barium", "lanthanum", "cerium", "praseodymium", "neodymium",
                          "promethium", "samarium", "europium", "gadolinium", "terbium", "dysprosium", "holmium", "erbium",
                          "thulium", "ytterbium", "lutetium", "hafnium", "tantalum", "tungsten", "rhenium", "osmium",
                          "iridium", "platinum", "gold", "mercury", "thallium", "lead", "bismuth", "polonium", "astatine",
                          "radon", "francium", "radium", "actinium", "thorium", "protactinium", "uranium", "neptunium",
                          "plutonium", "americium", "curium", "berkelium", "californium", "einsteinium", "fermium",
                          "mendelevium", "nobelium", "lawrencium", "rutherfordium", "dubnium", "seaborgium", "bohrium",
                          "hassium", "meitnerium", "darmstadtium", "roentgenium", "copernicium", "nihonium", "flerovium",
                          "moscovium", "livermorium", "tennessine", "oganesson", "ununennium"]

    def clean_abstract(self, abstract, return_type=False):
        abstract = abstract.split('\n')
        info = []
        for line in abstract:
            line = line.strip()
            if line != '':
                info.append(line)
        if len(info) == 2:
            abstract_type = info[0]
            clean_abstract = info[1]
        elif len(info) == 1:
            if info[0].split()[0].lower() == 'abstract':
                abstract_type = 'Abstract'
                clean_abstract = ' '.join(info[0].split()[1:])
            elif info[0].split()[0].lower() == 'summary':
                abstract_type = 'Summary'
                clean_abstract = ' '.join(info[0].split()[1:])
            elif 'objective' in info[0].split()[0].lower():
                abstract_type = 'Objective'
                clean_abstract = ' '.join(info[0].split()[1:])
            else:
                abstract_type = ''
                clean_abstract = info[0]
        else:
            info_lower = [x.lower() for x in info]
            section_titles = ['introduction',
                              'purpose',
                              'background',
                              'scope and approach',
                              'objective',
                              'objectives',
                              'materials and methods',
                              'results',
                              'conclusion',
                              'conclusions',
                              'key findings',
                              'key findings and conclusions',
                              'methodology',
                              'methods',
                              'study design',
                              'clinical implications']
            sectioned = False
            for section_title in section_titles:
                if section_title in info_lower:
                    sectioned = True
            if sectioned:
                if info[0].lower() == 'abstract':
                    abstract_type = 'Abstract'
                    text = []
                    for entry in info[1:]:
                        if entry.lower() in section_titles:
                            pass
                        else:
                            text.append(entry)
                    clean_abstract = ' '.join(text)
                elif info[0].lower() == 'summary':
                    abstract_type = 'Summary'
                    text = []
                    for entry in info[1::]:
                        if entry.lower() in section_titles:
                            pass
                        else:
                            text.append(entry)
                    clean_abstract = ' '.join(text)
                else:
                    abstract_type = ''
                    text = []
                    for entry in info:
                        if entry.lower() in section_titles:
                            pass
                        else:
                            text.append(entry)
                    clean_abstract = ' '.join(text)
            else:
                if info[0].lower() == 'abstract' or info[0].lower() == 'absract' or info[0].lower() == 'abstact' or info[0].lower() == 'abstractt':
                    abstract_type = 'Abstract'
                    clean_abstract = ' '.join(info[1:])
                elif info[0].lower() == 'summary' or info[0].lower() == 'publisher summary' or info[0].lower() == '1. summary':
                    abstract_type = 'Summary'
                    clean_abstract = ' '.join(info[1:])
                elif info[0] == 'This article has been retracted: please see Elsevier Policy on Article Withdrawal (https://www.elsevier.com/about/our-business/policies/article-withdrawal).':
                    abstract_type = 'Retracted'
                    clean_abstract = 'Retracted'
                else:
                    abstract_type = ''
                    clean_abstract = ' '.join(info)
        return clean_abstract, abstract_type
