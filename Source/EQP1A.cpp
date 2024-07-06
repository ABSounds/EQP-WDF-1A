/*
  ==============================================================================

    EQP1A.cpp
    Created: 24 May 2023 5:56:36pm
    Author:  alber

  ==============================================================================
*/

#include "EQP1A.h"
#include <JuceHeader.h>

namespace wdft = chowdsp::wdft;

EQP1A::EQP1A() = default;

void EQP1A::setParams(float new_LoBoost, float new_LoCut, float new_HiBoost, float new_HiCut, float new_HiBQ, int new_LoFreq, int new_HiBoostFreq, int new_HiCutFreq){
    this->set_LoBoost(new_LoBoost);
    this->set_LoCut(new_LoCut);
    this->set_HiBoost(new_HiBoost);
    this->set_HiCut(new_HiCut);
    this->set_HiBQ(new_HiBQ);
    this->set_LoFreq(new_LoFreq);
    this->set_HiCutFreq(new_HiCutFreq);
    this->set_HiBoostFreq(new_HiBoostFreq);
}

void EQP1A::set_LoBoost(float new_LoBoost) {
    if (loBoost != new_LoBoost){
        RBoostLo.setResistanceValue(new_LoBoost * RBOOSTLO_MAX);
        loBoost = new_LoBoost;
    }
}

void EQP1A::set_LoCut(float new_LoCut) {
    if (loCut != new_LoCut) {
        RCutLo.setResistanceValue(new_LoCut * RCUTLO_MAX);
        loCut = new_LoCut;
    }
}

void EQP1A::set_HiBoost(float new_HiBoost) {
    if (hiBoost != new_HiBoost) {
        RBoostHi1.setResistanceValue((1 - new_HiBoost) * RBOOSTHI_MAX);
        RBoostHi2.setResistanceValue(new_HiBoost * RBOOSTHI_MAX);
        hiBoost = new_HiBoost;
    }
}

void EQP1A::set_HiCut(float new_HiCut) {
    if (hiCut != new_HiCut) {
        RCutHi1.setResistanceValue((1 - new_HiCut) * RCUTHI_MAX);
        RCutHi2.setResistanceValue(new_HiCut * RCUTHI_MAX);
        hiCut = new_HiCut;
    }
}

void EQP1A::set_HiBQ(float new_HiBQ) {
    if (hiBQ != new_HiBQ) {
        RQ.setResistanceValue(new_HiBQ * RQ_MAX);
        hiBQ = new_HiBQ;
    }
}

void EQP1A::set_LoFreq(int new_LoFreq) {
    if (loFreq != new_LoFreq) {
        int freq;
        switch (new_LoFreq) {
            case 1:
                freq = 30;
                break;
            case 2:
                freq = 60;
                break;
            case 3:
                freq = 100;
                break;
            default:
                freq = 20;
                break;
        }
        auto [LoFreqC1_value, LoFreqC2_value] = get_CapValuesLoFreq(freq);
        LoFreqC1.setCapacitanceValue(LoFreqC1_value);
        LoFreqC2.setCapacitanceValue(LoFreqC2_value);
        loFreq = new_LoFreq;
    }
}

void EQP1A::set_HiBoostFreq(int new_HiBoostFreq) {
    if (hiBoostFreq != new_HiBoostFreq) {
        int freq;
        switch (new_HiBoostFreq) {
            case 0:
				freq = 3000;
				break;
            case 1:
                freq = 4000;
                break;
            case 2:
                freq = 5000;
				break;
            case 3:
				freq = 8000;
                break;
			case 4:
                freq = 10000;
                break;
            case 5:
                freq = 12000;
				break;
            default:
				freq = 16000;
				break;
        }

        auto [C1_value, L1_value] = get_CompValuesHiBoost(freq);
        C1.setCapacitanceValue(C1_value);
        L1.setInductanceValue(L1_value);
        hiBoostFreq = new_HiBoostFreq;
    }
}

void EQP1A::set_HiCutFreq(int new_hiCutFreq) {
    if (hiCutFreq != new_hiCutFreq) {
        int freq;
        switch (new_hiCutFreq) {
            case 0:
                freq = 5;
                break;
            case 1:
                freq = 10;
                break;
            default:
                freq = 20;
                break;
        }
        auto CHiCut_value = get_CapValueHiCut(freq);
        CHiCut.setCapacitanceValue(CHiCut_value);
        hiCutFreq = new_hiCutFreq;
    }
}

void EQP1A::prepare(double sampleRate) {
    C1.prepare(sampleRate);
    L1.prepare(sampleRate);
    LoFreqC1.prepare(sampleRate);
    LoFreqC2.prepare(sampleRate);
    CHiCut.prepare(sampleRate);

    this->sampleRate = sampleRate;
}

double EQP1A::processSample(double sample) {
    Vin.setVoltage(sample);
    Vin.incident(S3.reflected());
    S3.incident(Vin.reflected());
    //Makeup for the insertion loss of the filter
    return (-wdft::voltage<double>(J) + wdft::voltage<double>(R3)) * 15.4882;
}

std::tuple<double, double> EQP1A::get_CapValuesLoFreq(int loFreq) {
    
    double LoFreqC1_value, LoFreqC2_value;
    switch (loFreq) {
    case 20:
        LoFreqC2_value = 2.2e-6;
        break;
    case 30:
        LoFreqC2_value = 1.1e-6;
        break;
    case 60:
        LoFreqC2_value = 560e-9;
        break;
    default:
        LoFreqC2_value = 330e-9;
        break;
    }
    LoFreqC1_value = LoFreqC2_value / 30;
    return std::make_tuple(LoFreqC1_value, LoFreqC2_value);
}

std::tuple<double, double> EQP1A::get_CompValuesHiBoost(int fc) {
    double C1_value = sqrtf(1 / (RATIO_L1_C1 * powf(juce::MathConstants<float>::twoPi * fc, 2) ));
    double L1_value = RATIO_L1_C1 * C1_value;
    return std::make_tuple(C1_value, L1_value);
}

double EQP1A::get_CapValueHiCut(int hiCutFreq) {
    double CHiCut_value;

    switch (hiCutFreq) {
    case 5:
        CHiCut_value = 270e-9;
        break;
    case 10:
        CHiCut_value = 135e-9;
        break;
    default:
        CHiCut_value = 68e-9;
    }
    return CHiCut_value;
}