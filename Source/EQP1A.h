/*
  ==============================================================================

    EQP1A.h
    Created: 24 May 2023 5:56:36pm
    Author:  alber

  ==============================================================================
*/

#pragma once
#include "chowdsp_wdf.h"
#include <tuple>
#include <iostream>
#include <numbers>

namespace wdft = chowdsp::wdft;

class EQP1A
{
public:
    EQP1A();
    void set_LoBoost(float new_LoBoost);
    void set_LoCut(float new_LoCut);
    void set_HiBoost(float new_HiBoost);
    void set_HiCut(float new_HiCut);
    void set_HiBQ(float new_HiBQ);
    void set_LoFreq(int new_LoFreq);
    void set_HiBoostFreq(int new_HiBoostFreq);
    void set_HiCutFreq(int new_hiCutFreq);

    void prepare(double sampleRate);
    void setParams(float new_LoBoost, float new_LoCut, float new_HiBoost, float new_HiCut, float new_HiBQ, int new_LoFreq, int new_HiBoostFreq, int new_HiCutFreq);
    double processSample(double sample);

private:
    static constexpr double RBOOSTHI_MAX =  12e3;
    static constexpr double RQ_MAX       = 3.9e3;
    static constexpr double RCUTHI_MAX   =   1e3;
    static constexpr double RBOOSTLO_MAX = 8.2e3;
    static constexpr double RCUTLO_MAX   = 110e3;
    static constexpr double RATIO_L1_C1  =  12e6;
    static constexpr double R1_VALUE     = 91.0f;
    static constexpr double R2_VALUE     =   1e3;
    static constexpr double R3_VALUE     =  10e3;
    static constexpr double RQ_OFFSET_VALUE = 390;

    static constexpr float LO_BOOST_INI = 0.00001f;
    static constexpr float LO_CUT_INI   = 0.00001f;
    static constexpr float HI_BOOST_INI = 0.00001f;
    static constexpr float HI_CUT_INI   = 0.00001f;
    static constexpr float HI_BQ_INI    =     0.5f;

    static constexpr int LO_FREQ_INI =         2;
    static constexpr float HI_BOOST_FREQ_INI = 2;
    static constexpr int HI_CUT_FREQ_INI =     2;

    double sampleRate;
    float loBoost = LO_BOOST_INI;
    float loCut = LO_CUT_INI;
    float hiBoost = HI_BOOST_INI;
    float hiCut = HI_CUT_INI;
    float hiBQ = HI_BQ_INI;
    int loFreq = LO_FREQ_INI;
    float hiBoostFreq = HI_BOOST_FREQ_INI;
    int hiCutFreq = HI_CUT_FREQ_INI;

    // Port B
    wdft::ResistorT<double> RBoostHi1{ (1 - HI_BOOST_INI) * RBOOSTHI_MAX };
    // Port C
    wdft::CapacitorT<double> C1{ std::get<0>(get_CompValuesHiBoost(5000)) };
    wdft::InductorT<double> L1{ std::get<1>(get_CompValuesHiBoost(5000)) };
    wdft::ResistorT<double> RQ{ HI_BQ_INI * RQ_MAX };
    wdft::ResistorT<double> RQ_offset{ RQ_OFFSET_VALUE };
    wdft::WDFSeriesT<double, decltype(RQ), decltype(RQ_offset)> SRQ{ RQ, RQ_offset };
    wdft::WDFSeriesT<double, decltype(C1), decltype(L1)> SCLc{ C1, L1 };
    wdft::WDFSeriesT<double, decltype(SCLc), decltype(SRQ)> C{ SCLc, SRQ };
    // Port D
    wdft::ResistorT<double> RBoostHi2{ HI_BOOST_INI * RBOOSTHI_MAX };
    // Port E
    wdft::ResistorT<double> RCutHi1{ (1 - HI_CUT_INI) * RCUTHI_MAX };
    // Port F
    wdft::ResistorT<double> RCutHi2{ HI_CUT_INI * RCUTHI_MAX };
    // Port G
    wdft::CapacitorT<double> CHiCut{ get_CapValueHiCut(20) };
    wdft::ResistorT<double> R1{ R1_VALUE };
    // Port H
    wdft::CapacitorT<double> LoFreqC1{ std::get<0>(get_CapValuesLoFreq(20)) };
    wdft::ResistorT<double> RCutLo{ LO_CUT_INI * RCUTLO_MAX };
    wdft::WDFParallelT<double, decltype(LoFreqC1), decltype(RCutLo)> H{ LoFreqC1, RCutLo };
    // Port I
    wdft::ResistorT<double> R2{ R2_VALUE };
    wdft::ResistorT<double> R3{ R3_VALUE };
    wdft::WDFSeriesT<double, decltype(R2), decltype(R3)> I{ R2, R3 };
    // Port J
    wdft::ResistorT<double> RBoostLo{ LO_BOOST_INI * RBOOSTLO_MAX };
    wdft::CapacitorT<double> LoFreqC2{ std::get<1>(get_CapValuesLoFreq(20)) };
    wdft::WDFParallelT<double, decltype(RBoostLo), decltype(LoFreqC2)> J{ RBoostLo, LoFreqC2 };
    // Series and parallel adaptors between the different ports
    wdft::WDFParallelT<double, decltype(C), decltype(RBoostHi2)> pCD{ C, RBoostHi2 };
    wdft::WDFParallelT<double, decltype(RCutHi2), decltype(CHiCut)> pFG{ RCutHi2, CHiCut };
    wdft::WDFSeriesT<double, decltype(RCutHi1), decltype(pFG)> sEFG{ RCutHi1, pFG };
    wdft::WDFSeriesT<double, decltype(H), decltype(I)> sHI{ H, I };
    wdft::WDFParallelT<double, decltype(sEFG), decltype(sHI)> pEFGHI{ sEFG, sHI };
    wdft::WDFSeriesT<double, decltype(RBoostHi1), decltype(pCD)> S1{ RBoostHi1, pCD };
    wdft::WDFSeriesT<double, decltype(S1), decltype(pEFGHI)> S2{ S1, pEFGHI };
    wdft::WDFSeriesT<double, decltype(S2), decltype(J)> S3{ S2, J };
    // Connection of the ideal voltage source to the rest of the circuit
    wdft::IdealVoltageSourceT<double, decltype(S3)> Vin{ S3 };

    std::tuple<double, double> get_CapValuesLoFreq(int loFreq);
    std::tuple<double, double> get_CompValuesHiBoost(int fc);
    double get_CapValueHiCut(int hiCutFreq);
};