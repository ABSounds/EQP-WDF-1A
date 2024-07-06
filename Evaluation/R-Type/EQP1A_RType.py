from pywdf.core.wdf import *
from pywdf.core.circuit import Circuit
from pywdf.core.rtype import RTypeAdaptor

class PultecEQP1A (Circuit):
    def __init__(self, fs, LoBoost, LoCut, HiBoost, HiCut, HiBQ, LoFreq, HiBoostFreq, HiCutFreq) -> None:
        # Max value of the potentiometers
        self.RBOOSTHI_MAX = 10e3
        self.RQ_MAX = 2.5e3
        self.RCUTHI_MAX = 1e3
        self.RBOOSTLO_MAX = 9.1e3
        self.RCUTLO_MAX = 110e3

        self.fs = fs
        self.LoBoost = LoBoost
        self.LoCut = LoCut
        self.HiBoost = HiBoost
        self.HiCut = HiCut
        self.HiBQ = HiBQ
        self.LoFreq = LoFreq
        self.HiBoostFreq = HiBoostFreq
        self.HiCutFreq = HiCutFreq

        # Port B
        self.RBoostHi1 = Resistor((1 - HiBoost) * self.RBOOSTHI_MAX)
        self.B = self.RBoostHi1

        # Port C
        self.C1 = Capacitor(self.get_CompValuesHiBoost(HiBoostFreq)[0], self.fs)
        self.L1 = Inductor(self.get_CompValuesHiBoost(HiBoostFreq)[1], self.fs)
        self.RQ = Resistor(HiBQ * self.RQ_MAX)
        self.SCLc = SeriesAdaptor(self.C1, self.L1)
        self.C = SeriesAdaptor(self.SCLc, self.RQ)

        # Port D
        self.RBoostHi2 = Resistor(HiBoost * self.RBOOSTHI_MAX)
        self.D = self.RBoostHi2

        # Port E
        self.RCutHi1 = Resistor((1 - HiCut) * self.RCUTHI_MAX)
        self.E = self.RCutHi1

        # Port F
        self.RCutHi2 = Resistor(HiCut * self.RCUTHI_MAX)
        self.CHiCut = Capacitor(self.get_CapValueHiCut(HiCutFreq), self.fs)
        self.R1 = Resistor(91)
        self.sR1C = SeriesAdaptor(self.CHiCut, self.R1)
        self.F = ParallelAdaptor(self.RCutHi2, self.sR1C)

        # Port G
        self.LoFreqC1 = Capacitor(self.get_CapValuesLoFreq(LoFreq)[0], self.fs)
        self.RCutLo = Resistor(LoCut * self.RCUTLO_MAX)
        self.G = ParallelAdaptor(self.LoFreqC1, self.RCutLo)

        # Port H
        self.R2 = Resistor(1e3)
        self.R3 = Resistor(10e3)
        self.H = SeriesAdaptor(self.R2, self.R3)

        #Port I
        self.RBoostLo = Resistor(LoBoost * self.RBOOSTLO_MAX)
        self.LoFreqC2 = Capacitor(self.get_CapValuesLoFreq(LoFreq)[1], self.fs)
        self.I = ParallelAdaptor(self.RBoostLo, self.LoFreqC2)

        self.R_adaptor = RTypeAdaptor([self.B, self.C, self.D, self.E, self.F, self.G, self.H, self.I], self.impedance_calc, 0)

        # Port A
        self.Vin = IdealVoltageSource(self.R_adaptor)

        self.set_LoBoost(LoBoost)
        self.set_LoCut(LoCut)
        self.set_HiBoost(HiBoost)
        self.set_HiCut(HiCut)
        self.set_HiBQ(HiBQ)
        self.set_LoFreq(LoFreq)
        self.set_HiBoostFreq(HiBoostFreq)
        self.set_HiCutFreq(HiCutFreq)

        super().__init__(self.Vin, self.Vin, None)

    ## The scattering matrix below can be computed from the netlist. In this case I used Jatin Chowdhury's R-Solver for that.
    def impedance_calc(self,R):
        Rb, Rc, Rd, Re, Rf, Rg, Rh, Ri = R.get_port_impedances()
        R.set_S_matrix (  [[0,-1,-Rd/(Rc+Rd),-Rc/(Rc+Rd),-(Rg+Rh)/(Re+Rf+Rg+Rh),-(Rg+Rh)/(Re+Rf+Rg+Rh),-(Re+Rf)/(Re+Rf+Rg+Rh),-(Re+Rf)/(Re+Rf+Rg+Rh),-1],
                          [-((Rb*Rc+Rb*Rd)*Re+(Rb*Rc+Rb*Rd)*Rf+(Rb*Rc+Rb*Rd)*Rg+(Rb*Rc+Rb*Rd)*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),(Rc*Rd*Re+Rc*Rd*Rf+(Rc*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rc*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rb*Rd*Re+Rb*Rd*Rf+Rb*Rd*Rg+Rb*Rd*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rb*Rc*Re+Rb*Rc*Rf+Rb*Rc*Rg+Rb*Rc*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-((Rb*Rc+Rb*Rd)*Rg+(Rb*Rc+Rb*Rd)*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-((Rb*Rc+Rb*Rd)*Rg+(Rb*Rc+Rb*Rd)*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-((Rb*Rc+Rb*Rd)*Re+(Rb*Rc+Rb*Rd)*Rf)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-((Rb*Rc+Rb*Rd)*Re+(Rb*Rc+Rb*Rd)*Rf)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-((Rb*Rc+Rb*Rd)*Re+(Rb*Rc+Rb*Rd)*Rf+(Rb*Rc+Rb*Rd)*Rg+(Rb*Rc+Rb*Rd)*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri)],
                          [-(Rc*Rd*Re+Rc*Rd*Rf+Rc*Rd*Rg+Rc*Rd*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rc*Rd*Re+Rc*Rd*Rf+Rc*Rd*Rg+Rc*Rd*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-((Rb*Rc*Rc+Rc*Rc*Rd-Rb*Rd*Rd)*Re+(Rb*Rc*Rc+Rc*Rc*Rd-Rb*Rd*Rd)*Rf+(Rb*Rc*Rc+Rc*Rc*Rd-Rb*Rd*Rd+(Rc*Rc-Rd*Rd)*Re+(Rc*Rc-Rd*Rd)*Rf)*Rg+(Rb*Rc*Rc+Rc*Rc*Rd-Rb*Rd*Rd+(Rc*Rc-Rd*Rd)*Re+(Rc*Rc-Rd*Rd)*Rf)*Rh+((Rc*Rc-Rd*Rd)*Re+(Rc*Rc-Rd*Rd)*Rf+(Rc*Rc-Rd*Rd)*Rg+(Rc*Rc-Rd*Rd)*Rh)*Ri)/((Rb*Rc*Rc+(Rb+Rc)*Rd*Rd+(2*Rb*Rc+Rc*Rc)*Rd)*Re+(Rb*Rc*Rc+(Rb+Rc)*Rd*Rd+(2*Rb*Rc+Rc*Rc)*Rd)*Rf+(Rb*Rc*Rc+(Rb+Rc)*Rd*Rd+(2*Rb*Rc+Rc*Rc)*Rd+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Re+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rf)*Rg+(Rb*Rc*Rc+(Rb+Rc)*Rd*Rd+(2*Rb*Rc+Rc*Rc)*Rd+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Re+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rf)*Rh+((Rc*Rc+2*Rc*Rd+Rd*Rd)*Re+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rf+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rg+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rh)*Ri),((2*Rb*Rc*Rc+(2*Rb*Rc+Rc*Rc)*Rd)*Re+(2*Rb*Rc*Rc+(2*Rb*Rc+Rc*Rc)*Rd)*Rf+(2*Rb*Rc*Rc+(2*Rb*Rc+Rc*Rc)*Rd+2*(Rc*Rc+Rc*Rd)*Re+2*(Rc*Rc+Rc*Rd)*Rf)*Rg+(2*Rb*Rc*Rc+(2*Rb*Rc+Rc*Rc)*Rd+2*(Rc*Rc+Rc*Rd)*Re+2*(Rc*Rc+Rc*Rd)*Rf)*Rh+2*((Rc*Rc+Rc*Rd)*Re+(Rc*Rc+Rc*Rd)*Rf+(Rc*Rc+Rc*Rd)*Rg+(Rc*Rc+Rc*Rd)*Rh)*Ri)/((Rb*Rc*Rc+(Rb+Rc)*Rd*Rd+(2*Rb*Rc+Rc*Rc)*Rd)*Re+(Rb*Rc*Rc+(Rb+Rc)*Rd*Rd+(2*Rb*Rc+Rc*Rc)*Rd)*Rf+(Rb*Rc*Rc+(Rb+Rc)*Rd*Rd+(2*Rb*Rc+Rc*Rc)*Rd+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Re+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rf)*Rg+(Rb*Rc*Rc+(Rb+Rc)*Rd*Rd+(2*Rb*Rc+Rc*Rc)*Rd+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Re+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rf)*Rh+((Rc*Rc+2*Rc*Rd+Rd*Rd)*Re+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rf+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rg+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rh)*Ri),-(Rc*Rd*Rg+Rc*Rd*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rc*Rd*Rg+Rc*Rd*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rc*Rd*Re+Rc*Rd*Rf)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rc*Rd*Re+Rc*Rd*Rf)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rc*Rd*Re+Rc*Rd*Rf+Rc*Rd*Rg+Rc*Rd*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri)],
                          [-(Rc*Rd*Re+Rc*Rd*Rf+Rc*Rd*Rg+Rc*Rd*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rc*Rd*Re+Rc*Rd*Rf+Rc*Rd*Rg+Rc*Rd*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),((2*Rb*Rc*Rd+(2*Rb+Rc)*Rd*Rd)*Re+(2*Rb*Rc*Rd+(2*Rb+Rc)*Rd*Rd)*Rf+(2*Rb*Rc*Rd+(2*Rb+Rc)*Rd*Rd+2*(Rc*Rd+Rd*Rd)*Re+2*(Rc*Rd+Rd*Rd)*Rf)*Rg+(2*Rb*Rc*Rd+(2*Rb+Rc)*Rd*Rd+2*(Rc*Rd+Rd*Rd)*Re+2*(Rc*Rd+Rd*Rd)*Rf)*Rh+2*((Rc*Rd+Rd*Rd)*Re+(Rc*Rd+Rd*Rd)*Rf+(Rc*Rd+Rd*Rd)*Rg+(Rc*Rd+Rd*Rd)*Rh)*Ri)/((Rb*Rc*Rc+(Rb+Rc)*Rd*Rd+(2*Rb*Rc+Rc*Rc)*Rd)*Re+(Rb*Rc*Rc+(Rb+Rc)*Rd*Rd+(2*Rb*Rc+Rc*Rc)*Rd)*Rf+(Rb*Rc*Rc+(Rb+Rc)*Rd*Rd+(2*Rb*Rc+Rc*Rc)*Rd+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Re+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rf)*Rg+(Rb*Rc*Rc+(Rb+Rc)*Rd*Rd+(2*Rb*Rc+Rc*Rc)*Rd+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Re+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rf)*Rh+((Rc*Rc+2*Rc*Rd+Rd*Rd)*Re+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rf+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rg+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rh)*Ri),((Rb*Rc*Rc-(Rb+Rc)*Rd*Rd)*Re+(Rb*Rc*Rc-(Rb+Rc)*Rd*Rd)*Rf+(Rb*Rc*Rc-(Rb+Rc)*Rd*Rd+(Rc*Rc-Rd*Rd)*Re+(Rc*Rc-Rd*Rd)*Rf)*Rg+(Rb*Rc*Rc-(Rb+Rc)*Rd*Rd+(Rc*Rc-Rd*Rd)*Re+(Rc*Rc-Rd*Rd)*Rf)*Rh+((Rc*Rc-Rd*Rd)*Re+(Rc*Rc-Rd*Rd)*Rf+(Rc*Rc-Rd*Rd)*Rg+(Rc*Rc-Rd*Rd)*Rh)*Ri)/((Rb*Rc*Rc+(Rb+Rc)*Rd*Rd+(2*Rb*Rc+Rc*Rc)*Rd)*Re+(Rb*Rc*Rc+(Rb+Rc)*Rd*Rd+(2*Rb*Rc+Rc*Rc)*Rd)*Rf+(Rb*Rc*Rc+(Rb+Rc)*Rd*Rd+(2*Rb*Rc+Rc*Rc)*Rd+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Re+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rf)*Rg+(Rb*Rc*Rc+(Rb+Rc)*Rd*Rd+(2*Rb*Rc+Rc*Rc)*Rd+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Re+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rf)*Rh+((Rc*Rc+2*Rc*Rd+Rd*Rd)*Re+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rf+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rg+(Rc*Rc+2*Rc*Rd+Rd*Rd)*Rh)*Ri),-(Rc*Rd*Rg+Rc*Rd*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rc*Rd*Rg+Rc*Rd*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rc*Rd*Re+Rc*Rd*Rf)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rc*Rd*Re+Rc*Rd*Rf)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rc*Rd*Re+Rc*Rd*Rf+Rc*Rd*Rg+Rc*Rd*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri)],
                          [-((Rc+Rd)*Re*Rg+(Rc+Rd)*Re*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-((Rc+Rd)*Re*Rg+(Rc+Rd)*Re*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rd*Re*Rg+Rd*Re*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rc*Re*Rg+Rc*Re*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-((Rb*Rc+(Rb+Rc)*Rd)*Re*Re-(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf-(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Rf)*Rg*Rg-(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re-(Rc+Rd)*Rf*Rf-2*(Rb*Rc+(Rb+Rc)*Rd)*Rf)*Rg+((Rc+Rd)*Re*Re-(Rc+Rd)*Rf*Rf-2*(Rb*Rc+(Rb+Rc)*Rd)*Rf-2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Rf)*Rg)*Rh+((Rc+Rd)*Re*Re-(Rc+Rd)*Rf*Rf-2*(Rc+Rd)*Rf*Rg-(Rc+Rd)*Rg*Rg-(Rc+Rd)*Rh*Rh-2*((Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri)/((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+2*((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri),-((Rc+Rd)*Re*Rg*Rg+(Rc+Rd)*Re*Rh*Rh+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+2*((Rc+Rd)*Re*Re+(Rc+Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Re)*Rg+2*((Rc+Rd)*Re*Re+(Rc+Rd)*Re*Rf+(Rc+Rd)*Re*Rg+(Rb*Rc+(Rb+Rc)*Rd)*Re)*Rh+2*((Rc+Rd)*Re*Re+(Rc+Rd)*Re*Rf+(Rc+Rd)*Re*Rg+(Rc+Rd)*Re*Rh)*Ri)/((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+2*((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri),(2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+((Rc+Rd)*Re*Re+(Rc+Rd)*Re*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Re*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re)*Rh+2*((Rc+Rd)*Re*Re+(Rc+Rd)*Re*Rf+(Rc+Rd)*Re*Rg+(Rc+Rd)*Re*Rh)*Ri)/((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+2*((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri),(2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+((Rc+Rd)*Re*Re+(Rc+Rd)*Re*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Re*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re)*Rh+2*((Rc+Rd)*Re*Re+(Rc+Rd)*Re*Rf+(Rc+Rd)*Re*Rg+(Rc+Rd)*Re*Rh)*Ri)/((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+2*((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri),-((Rc+Rd)*Re*Rg+(Rc+Rd)*Re*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri)],
                          [-((Rc+Rd)*Rf*Rg+(Rc+Rd)*Rf*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-((Rc+Rd)*Rf*Rg+(Rc+Rd)*Rf*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rd*Rf*Rg+Rd*Rf*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rc*Rf*Rg+Rc*Rf*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-((Rc+Rd)*Rf*Rg*Rg+(Rc+Rd)*Rf*Rh*Rh+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+2*((Rc+Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+2*((Rc+Rd)*Rf*Rf+(Rc+Rd)*Rf*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rh+2*((Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rf*Rg+(Rc+Rd)*Rf*Rh)*Ri)/((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+2*((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri),((Rb*Rc+(Rb+Rc)*Rd)*Re*Re-(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rh*Rh+((Rc+Rd)*Re*Re-(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re)*Rg+((Rc+Rd)*Re*Re-(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rg)*Rh+((Rc+Rd)*Re*Re-(Rc+Rd)*Rf*Rf+2*(Rc+Rd)*Re*Rg+(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rg)*Rh)*Ri)/((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+2*((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri),(2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+((Rc+Rd)*Rf*Rf+(2*Rb*Rc+2*(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Rf*Rf+(2*Rb*Rc+2*(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rh+2*((Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rf*Rg+(Rc+Rd)*Rf*Rh)*Ri)/((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+2*((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri),(2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+((Rc+Rd)*Rf*Rf+(2*Rb*Rc+2*(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Rf*Rf+(2*Rb*Rc+2*(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rh+2*((Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rf*Rg+(Rc+Rd)*Rf*Rh)*Ri)/((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+2*((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri),-((Rc+Rd)*Rf*Rg+(Rc+Rd)*Rf*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri)],
                          [-((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rd*Re+Rd*Rf)*Rg/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rc*Re+Rc*Rf)*Rg/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),((2*Rb*Rc+2*(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(2*Rb*Rc+2*(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rh+2*((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf)*Rg+2*((Rc+Rd)*Rg*Rg+(Rc+Rd)*Rg*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Ri)/((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+2*((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri),((2*Rb*Rc+2*(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(2*Rb*Rc+2*(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rh+2*((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf)*Rg+2*((Rc+Rd)*Rg*Rg+(Rc+Rd)*Rg*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Ri)/((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+2*((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri),((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf-(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rh+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf-(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh)*Ri)/((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+2*((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri),-(2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+2*((Rc+Rd)*Rg*Rg+(Rc+Rd)*Rg*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Ri)/((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+2*((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri),-((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri)],
                          [-((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rd*Re+Rd*Rf)*Rh/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rc*Re+Rc*Rf)*Rh/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),((2*Rb*Rc+2*(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+(2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Rf+(2*Rb*Rc+2*(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+2*((Rc+Rd)*Rh*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri)/((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+2*((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri),((2*Rb*Rc+2*(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+(2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Rf+(2*Rb*Rc+2*(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+2*((Rc+Rd)*Rh*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri)/((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+2*((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri),-(2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+2*((Rc+Rd)*Rh*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri)/((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+2*((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri),((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg-(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rg*Rg-(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Ri)/((Rb*Rc+(Rb+Rc)*Rd)*Re*Re+2*(Rb*Rc+(Rb+Rc)*Rd)*Re*Rf+(Rb*Rc+(Rb+Rc)*Rd)*Rf*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh*Rh+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf)*Rg+((Rc+Rd)*Re*Re+(Rc+Rd)*Rf*Rf+2*(Rb*Rc+(Rb+Rc)*Rd)*Re+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re)*Rf+2*(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg)*Rh+((Rc+Rd)*Re*Re+2*(Rc+Rd)*Re*Rf+(Rc+Rd)*Rf*Rf+(Rc+Rd)*Rg*Rg+(Rc+Rd)*Rh*Rh+2*((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+2*((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg)*Rh)*Ri),-((Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri)],
                          [-((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rd*Re+Rd*Rf+Rd*Rg+Rd*Rh)*Ri/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-(Rc*Re+Rc*Rf+Rc*Rg+Rc*Rh)*Ri/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-((Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-((Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-((Rc+Rd)*Re+(Rc+Rd)*Rf)*Ri/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),-((Rc+Rd)*Re+(Rc+Rd)*Rf)*Ri/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri),((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh)/((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri)]]
        )
        Ra=((Rb*Rc+(Rb+Rc)*Rd)*Re+(Rb*Rc+(Rb+Rc)*Rd)*Rf+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rg+(Rb*Rc+(Rb+Rc)*Rd+(Rc+Rd)*Re+(Rc+Rd)*Rf)*Rh+((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)*Ri)/((Rc+Rd)*Re+(Rc+Rd)*Rf+(Rc+Rd)*Rg+(Rc+Rd)*Rh)
        return Ra

    def set_LoBoost(self, new_LoBoost):
        if self.LoBoost != new_LoBoost:
            self.RBoostLo.set_resistance(new_LoBoost * self.RBOOSTLO_MAX)
            self.LoBoost = new_LoBoost

    def set_LoCut(self, new_LoCut):
        if self.LoCut != new_LoCut:
            self.RCutLo.set_resistance(new_LoCut * self.RCUTLO_MAX)
            self.LoCut = new_LoCut

    def set_HiBoost(self, new_HiBoost):
        if self.HiBoost != new_HiBoost:
            self.RBoostHi1.set_resistance((1 - new_HiBoost) * self.RBOOSTHI_MAX)
            self.RBoostHi2.set_resistance(new_HiBoost * self.RBOOSTHI_MAX)
            self.HiBoost = new_HiBoost

    def set_HiCut(self, new_HiCut):
        if self.HiCut != new_HiCut:
            self.RCutHi1.set_resistance((1 - new_HiCut) * self.RCUTHI_MAX)
            self.RCutHi2.set_resistance(new_HiCut * self.RCUTHI_MAX)
            self.HiCut = new_HiCut

    def set_HiBQ(self, new_HiBQ):
        if self.HiBQ != new_HiBQ:
            self.RQ.set_resistance(new_HiBQ * self.RQ_MAX)
            self.HiBQ = new_HiBQ

    def set_LoFreq(self, new_LoFreq):
        if self.LoFreq != new_LoFreq:
            LoFreqC1, LoFreqC2 = self.get_CapValuesLoFreq(new_LoFreq)
            self.LoFreqC1.set_capacitance(LoFreqC1)
            self.LoFreqC2.set_capacitance(LoFreqC2)
            self.LoFreq = new_LoFreq

    def set_HiBoostFreq(self, new_HiBoostFreq):
        if self.HiBoostFreq != new_HiBoostFreq:
            C1, L1 = self.get_CompValuesHiBoost(new_HiBoostFreq)
            self.C1.set_capacitance(C1)
            self.L1.set_inductance(L1)
            self.HiBoostFreq = new_HiBoostFreq

    def set_HiCutFreq(self, new_hiCutFreq):
        if self.HiCutFreq != new_hiCutFreq:
            CHiCut = self.get_CapValueHiCut(new_hiCutFreq)
            self.HiCutFreq = new_hiCutFreq
            self.CHiCut.set_capacitance(CHiCut)

    def get_CapValuesLoFreq(self, LoFreq):
        #  20 Hz
        if LoFreq == 20:
            LoFreqC2 = 2.2e-6
        #  30 Hz
        elif LoFreq == 30:
            LoFreqC2 = 1.1e-6
        #  60 Hz
        elif LoFreq == 60:
            LoFreqC2 = 560e-9
        # 100 Hz
        else:
            LoFreqC2 = 330e-9
        LoFreqC1 = LoFreqC2/30
        return LoFreqC1, LoFreqC2

    def get_CompValuesHiBoost(self, fc):
        RATIO_L1_C1 = 12e6
        C1 = np.sqrt(1/(RATIO_L1_C1 * (2*np.pi*fc)**2))
        L1 = RATIO_L1_C1 * C1
        fc = np.sqrt(1/(L1*C1))/(2*np.pi)
        return C1, L1

    def get_CapValueHiCut(self, HiCutFreq):
        #  5 kHz
        if HiCutFreq == 5e3:
            CHiCut = 270e-9
        # 10 kHz
        elif HiCutFreq == 10e3:
            CHiCut = 135e-9
        # 20 kHz
        else:
            CHiCut = 68e-9
        return CHiCut

    def process_sample(self, sample):
        self.Vin.set_voltage(sample)
        self.root.accept_incident_wave(self.root.next.propagate_reflected_wave())
        self.root.next.accept_incident_wave(self.root.propagate_reflected_wave())
        return (- self.I.wave_to_voltage() + self.R3.wave_to_voltage()) * 13.1069