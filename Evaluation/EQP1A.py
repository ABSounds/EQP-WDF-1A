from pywdf.core.wdf import *
from pywdf.core.circuit import Circuit
import numpy as np

class PultecEQP1A (Circuit):
    def __init__(self, fs, LoBoost, LoCut, HiBoost, HiCut, HiBQ, LoFreq, HiBoostFreq, HiCutFreq) -> None:
        # Max value of the potentiometers
        self.RBOOSTHI_MAX = 12e3
        self.RQ_MAX = 3.9e3
        self.RQ_offset_value = 390
        self.RCUTHI_MAX = 1e3
        self.RBOOSTLO_MAX = 8.2e3
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

        ## Port by port, all the elements of the circuit are created and the relationship between them is stablished (Series/parallel).

        # Port B
        self.RBoostHi1 = Resistor((1 - HiBoost) * self.RBOOSTHI_MAX)
        self.B = self.RBoostHi1

        # Port C
        self.C1 = Capacitor(self.get_CompValuesHiBoost(HiBoostFreq)[0], self.fs)
        self.L1 = Inductor(self.get_CompValuesHiBoost(HiBoostFreq)[1], self.fs)
        self.SCLc = SeriesAdaptor(self.C1, self.L1)
        self.RQ = Resistor(self.HiBQ * self.RQ_MAX)
        self.RQ_offset = Resistor(self.RQ_offset_value)
        self.SRQc = SeriesAdaptor(self.RQ, self.RQ_offset)
        self.C = SeriesAdaptor(self.SCLc, self.SRQc)

        # Port D
        self.RBoostHi2 = Resistor(HiBoost * self.RBOOSTHI_MAX)
        self.D = self.RBoostHi2

        # Port E
        self.RCutHi1 = Resistor((1 - HiCut) * self.RCUTHI_MAX)
        self.E = self.RCutHi1

        # Port F
        self.RCutHi2 = Resistor(HiCut * self.RCUTHI_MAX)
        self.F = self.RCutHi2

        # Port G
        self.CHiCut = Capacitor(self.get_CapValueHiCut(HiCutFreq), self.fs)
        self.R1 = Resistor(91)
        self.G = SeriesAdaptor(self.CHiCut, self.R1)

        # Port H
        self.LoFreqC1 = Capacitor(self.get_CapValuesLoFreq(self.LoFreq)[0], self.fs)
        self.RCutLo = Resistor(LoCut * self.RCUTLO_MAX)
        self.H = ParallelAdaptor(self.LoFreqC1, self.RCutLo)

        # Port I
        self.R2 = Resistor(1e3)
        self.R3 = Resistor(10e3)
        self.I = SeriesAdaptor(self.R2, self.R3)

        #Port J
        self.RBoostLo = Resistor(LoBoost * self.RBOOSTLO_MAX)
        self.LoFreqC2 = Capacitor(self.get_CapValuesLoFreq(self.LoFreq)[1], self.fs)
        self.J = ParallelAdaptor(self.RBoostLo, self.LoFreqC2)

        ## All the ports are connected.
        self.pCD = ParallelAdaptor(self.C, self.D)
        self.pFG = ParallelAdaptor(self.F, self.G)
        self.sEFG = SeriesAdaptor(self.E, self.pFG)
        self.sHI = SeriesAdaptor(self.H, self.I)
        self.pEFGHI = ParallelAdaptor(self.sEFG, self.sHI)

        self.S1 = SeriesAdaptor(self.B, self.pCD)
        self.S2 = SeriesAdaptor(self.S1, self.pEFGHI)
        self.S3 = SeriesAdaptor(self.S2, self.J)

        ## The voltage source is connected to the rest of the circuit.
        # Port A
        self.Vin = IdealVoltageSource(self.S3)

        self.set_LoBoost(self.LoBoost)
        self.set_LoCut(self.LoCut)
        self.set_HiBoost(self.HiBoost)
        self.set_HiCut(self.HiCut)
        self.set_HiBQ(self.HiBQ)
        self.set_LoFreq(self.LoFreq)
        self.set_HiBoostFreq(self.HiBoostFreq)
        self.set_HiCutFreq(self.HiCutFreq)

        super().__init__(self.Vin, self.Vin, None)

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
        self.S3.accept_incident_wave(self.Vin.propagate_reflected_wave())
        self.Vin.accept_incident_wave(self.S3.propagate_reflected_wave())
        return (- self.J.wave_to_voltage() + self.R3.wave_to_voltage()) * 15.4882