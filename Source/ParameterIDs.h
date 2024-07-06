/*
  ==============================================================================

    ParameterIDs.h
    Created: 18 Apr 2024 8:45:26pm
    Author:  Alberto

  ==============================================================================
*/

#pragma once

#include <JuceHeader.h>

// Hint used for AU parameter versioning: 
constexpr static int    kParameterVersionHint = 1;

// EQP-WDF-1A Parameters:
static const juce::String   g_loFreqID = "loFreq";
static const juce::String   g_loBoostID = "loBoost";
static const juce::String   g_loCutID = "loCut";
static const juce::String   g_hiBoostFreqID = "hiBoostFreq";
static const juce::String   g_hiBoostID = "hiBoost";
static const juce::String   g_hiBQID = "hiBQ";
static const juce::String   g_hiCutFreqID = "hiCutFreq";
static const juce::String   g_hiCutID = "hiCut";
static const juce::String   g_osFactorID = "osFactor";
static const juce::String   g_gainID = "gain";

// Non-automatable parameters:
static const juce::String   g_bypassID = "bypass";
static const juce::String   g_guiSizeID = "guiSize";


inline static juce::File getPluginAppDataPath()
{
    juce::File appDataPath = juce::File::getSpecialLocation(juce::File::userApplicationDataDirectory);

#ifdef JUCE_MAC
    appDataPath = appDataPath.getChildFile("Application Support");
#endif

    return appDataPath.getChildFile(JucePlugin_Manufacturer).getChildFile(JucePlugin_Name);
}