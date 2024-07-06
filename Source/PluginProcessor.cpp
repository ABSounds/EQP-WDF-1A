/*
  ==============================================================================

    This file contains the JUCE plugin processor for the EQP1A plugin.

  ==============================================================================

  #TODO: Improvements:
    * Save/set window size (and position?) in save/set state information so the plug-in doesn't reopen in the default size.
    * Add link to website on plugin panel.
    * Link A/B apvts to a preset so the preset combobox isn't wrong when loading a preset on A when B was modified.
*/

#include "PluginProcessor.h"
#include "PluginEditor.h"
#include "ParameterIDs.h"

//==============================================================================
EQP1AAudioProcessor::EQP1AAudioProcessor()
#ifndef JucePlugin_PreferredChannelConfigurations
    : AudioProcessor(BusesProperties()
        .withInput("Input", juce::AudioChannelSet::stereo(), true)
        .withOutput("Output", juce::AudioChannelSet::stereo(), true)
    )
#endif
    , parameters(*this, &undoManager, "PARAMETERS", createParameters())
    , nonAutomatableParameters(*this, nullptr, "NON_AUTOMATABLE_PARAMETERS", createNonAutomatableParameters())
    , oversampler(getNumOutputChannels())
    , presetManager(parameters, getPluginAppDataPath())
{   
    parameters.addParameterListener(g_loFreqID, this);
    parameters.addParameterListener(g_loBoostID, this);
    parameters.addParameterListener(g_loCutID, this);
    parameters.addParameterListener(g_hiBoostFreqID, this);
    parameters.addParameterListener(g_hiBoostID, this);
    parameters.addParameterListener(g_hiBQID, this);
    parameters.addParameterListener(g_hiCutFreqID, this);
    parameters.addParameterListener(g_hiCutID, this);
    parameters.addParameterListener(g_gainID, this);

    nonAutomatableParameters.addParameterListener(g_osFactorID, this);
    nonAutomatableParameters.addParameterListener(g_bypassID, this);

    gain.setGainDecibels(0.0f); 
}

EQP1AAudioProcessor::~EQP1AAudioProcessor()
{
    parameters.removeParameterListener(g_loFreqID, this);
    parameters.removeParameterListener(g_loBoostID, this);
    parameters.removeParameterListener(g_loCutID, this);
    parameters.removeParameterListener(g_hiBoostFreqID, this);
    parameters.removeParameterListener(g_hiBoostID, this);
    parameters.removeParameterListener(g_hiBQID, this);
    parameters.removeParameterListener(g_hiCutFreqID, this);
    parameters.removeParameterListener(g_hiCutID, this);
    parameters.removeParameterListener(g_gainID, this);

    nonAutomatableParameters.removeParameterListener(g_osFactorID, this);
    nonAutomatableParameters.removeParameterListener(g_bypassID, this);

    // TODO: Get rid of this. Doesn't look very safe.
    for (auto i = 0; i < eqp1a.size(); i++) {
        delete eqp1a[i];
    }
    eqp1a.clear();
}

//==============================================================================

juce::AudioProcessorValueTreeState::ParameterLayout EQP1AAudioProcessor::createParameters()
{
    std::vector <std::unique_ptr<juce::RangedAudioParameter>> parameters;
    parameters.push_back(std::make_unique<juce::AudioParameterChoice>(juce::ParameterID{ g_loFreqID, kParameterVersionHint }, "Low Freq", StringArray{ "20 Hz", "30 Hz", "60 Hz", "100 Hz" }, 0));
    parameters.push_back(std::make_unique<juce::AudioParameterFloat>(juce::ParameterID{ g_loBoostID, kParameterVersionHint }, "Low Boost", juce::NormalisableRange<float>(0.0001f, 9.9999f, 0.0001f, 0.3f, false), 0.0001f));
    parameters.push_back(std::make_unique<juce::AudioParameterFloat>(juce::ParameterID{ g_loCutID, kParameterVersionHint }, "Low Atten", juce::NormalisableRange<float>(0.0001f, 9.9999f, 0.0001f, 0.3f, false), 0.0001f));
    parameters.push_back(std::make_unique<juce::AudioParameterChoice>(juce::ParameterID{ g_hiBoostFreqID, kParameterVersionHint }, "High Boost Freq", StringArray{ "3 kHz", "4 kHz", "5 kHz", "8 kHz", "10 kHz", "12 kHz", "16 kHz" }, 3));
    parameters.push_back(std::make_unique<juce::AudioParameterFloat>(juce::ParameterID{ g_hiBoostID, kParameterVersionHint }, "High Boost", 0.0001f, 9.9999f, 0.0001f));
    parameters.push_back(std::make_unique<juce::AudioParameterFloat>(juce::ParameterID{ g_hiBQID, kParameterVersionHint }, "High Boost Q", 0.0001f, 9.9999f, 5.0f));
    parameters.push_back(std::make_unique<juce::AudioParameterChoice>(juce::ParameterID{ g_hiCutFreqID, kParameterVersionHint }, "High Atten Freq", StringArray{ "5 kHz", "10 kHz", "20 kHz" }, 2));
    parameters.push_back(std::make_unique<juce::AudioParameterFloat>(juce::ParameterID{ g_hiCutID, kParameterVersionHint }, "High Atten", 0.0001f, 9.9999f, 0.0001f));
    parameters.push_back(std::make_unique<juce::AudioParameterFloat>(juce::ParameterID{ g_gainID, kParameterVersionHint }, "Output", juce::NormalisableRange<float> { -20.f, 20.0f, 0.1f}, 0.0f));

    return { parameters.begin(), parameters.end() };
}

juce::AudioProcessorValueTreeState::ParameterLayout EQP1AAudioProcessor::createNonAutomatableParameters()
{
    std::vector <std::unique_ptr<juce::RangedAudioParameter>> parameters;
    parameters.push_back(std::make_unique<juce::AudioParameterChoice>(juce::ParameterID{ g_osFactorID, kParameterVersionHint }, "Oversampling Factor", StringArray{ "x1", "x2", "x4", "x8", "x16"}, 1, juce::AudioParameterChoiceAttributes().withAutomatable(false)));
    parameters.push_back(std::make_unique<juce::AudioParameterBool>(juce::ParameterID{ g_bypassID, kParameterVersionHint }, "Bypass", false));

    return { parameters.begin(), parameters.end() };
}

void EQP1AAudioProcessor::parameterChanged(const juce::String& parameterID, float newValue) {
    auto totalNumInputChannels = getTotalNumInputChannels();

    if (parameterID == g_gainID) {
        float gainValue = *parameters.getRawParameterValue(g_gainID);
        gain.setGainDecibels(gainValue);
    }

    else if (parameterID == g_loFreqID) {
        auto* loBoostParam = dynamic_cast<juce::AudioParameterChoice*>(parameters.getParameter(g_loFreqID));
        auto new_LoFreq = loBoostParam->getIndex();
		for (int i = 0; i < eqp1a.size(); i++)
            eqp1a[i]->set_LoFreq(new_LoFreq);
	}

    else if (parameterID == g_loBoostID) {
        float new_LoBoost = *parameters.getRawParameterValue(g_loBoostID) / 10.0f;
        for (int i = 0; i < eqp1a.size(); i++)
            eqp1a[i]->set_LoBoost(new_LoBoost);
    }
    
    else if (parameterID == g_loCutID) {
		float new_LoCut = *parameters.getRawParameterValue(g_loCutID) / 10.0f;
        for (int i = 0; i < eqp1a.size(); i++)
		    eqp1a[i]->set_LoCut(new_LoCut);
	}

    else if (parameterID == g_hiBoostFreqID) {
		auto* hiBoostFreqParam = dynamic_cast<juce::AudioParameterChoice*>(parameters.getParameter(g_hiBoostFreqID));
		int new_HiBoostFreq = hiBoostFreqParam->getIndex();
        for (int i = 0; i < eqp1a.size(); i++)
		    eqp1a[i]->set_HiBoostFreq(new_HiBoostFreq);
	}

    else if (parameterID == g_hiBoostID) {
		float new_HiBoost = *parameters.getRawParameterValue(g_hiBoostID) / 10.0f;
        for (int i = 0; i < eqp1a.size(); i++)
		    eqp1a[i]->set_HiBoost(new_HiBoost);
	}

    else if (parameterID == g_hiBQID) {
        float new_HiBQ = *parameters.getRawParameterValue(g_hiBQID) / 10.0f;
        for (int i = 0; i < eqp1a.size(); i++)
            eqp1a[i]->set_HiBQ(new_HiBQ);
    }

    else if(parameterID == g_hiCutID) {
		float new_HiCut = *parameters.getRawParameterValue(g_hiCutID) / 10.0f;
        for (int i = 0; i < eqp1a.size(); i++)
		    eqp1a[i]->set_HiCut(new_HiCut);
	}

    else if (parameterID == g_hiCutFreqID) {
        auto* hiCutParam = dynamic_cast<juce::AudioParameterChoice*>(parameters.getParameter(g_hiCutFreqID));
        auto new_HighCutFreq = hiCutParam->getIndex();

        for (int i = 0; i < eqp1a.size(); i++)
            eqp1a[i]->set_HiCutFreq(new_HighCutFreq);
    }

    else if (parameterID == g_osFactorID){
		auto* osFactorParam = dynamic_cast<juce::AudioParameterChoice*>(nonAutomatableParameters.getParameter(g_osFactorID));
        osText = osFactorParam->getCurrentChoiceName().toStdString();
        osChoice = osFactorParam->getIndex();
        osFactor = static_cast<size_t>(std::log2f(std::stoi(osText.substr(1))));

        osFactorChanged = true;
	}

    else if (parameterID == g_bypassID) {
		bypassed = newValue;
	}
}

const juce::String EQP1AAudioProcessor::getName() const
{
    return JucePlugin_Name;
}

bool EQP1AAudioProcessor::acceptsMidi() const
{
   #if JucePlugin_WantsMidiInput
    return true;
   #else
    return false;
   #endif
}

bool EQP1AAudioProcessor::producesMidi() const
{
   #if JucePlugin_ProducesMidiOutput
    return true;
   #else
    return false;
   #endif
}

bool EQP1AAudioProcessor::isMidiEffect() const
{
   #if JucePlugin_IsMidiEffect
    return true;
   #else
    return false;
   #endif
}

double EQP1AAudioProcessor::getTailLengthSeconds() const
{
    return 0.0;
}

int EQP1AAudioProcessor::getNumPrograms()
{
    return 1;
}

int EQP1AAudioProcessor::getCurrentProgram()
{
    return 0;
}

void EQP1AAudioProcessor::setCurrentProgram (int index)
{
}

const juce::String EQP1AAudioProcessor::getProgramName (int index)
{
    return {};
}

void EQP1AAudioProcessor::changeProgramName (int index, const juce::String& newName)
{
}

void EQP1AAudioProcessor::prepareOversampling (double sampleRate, int samplesPerBlock) {
    oversampler.clearOversamplingStages();

    for (size_t n = 0; n < osFactor; ++n)
    {
        auto twUp = 0.10f * (n == 0 ? 0.5f : 1.0f);
        auto twDown = 0.12f * (n == 0 ? 0.5f : 1.0f);

        auto gaindBStartUp = -90.0f;
        auto gaindBStartDown = -75.0f;
        auto gaindBFactorUp = 10.0f;
        auto gaindBFactorDown = 10.0f;

        oversampler.addOversamplingStage(juce::dsp::Oversampling<float>::FilterType::filterHalfBandFIREquiripple,
            twUp, gaindBStartUp + gaindBFactorUp * (float)n,
            twDown, gaindBStartDown + gaindBFactorDown * (float)n);
    }
    if (osFactor == 0)
        oversampler.addDummyOversamplingStage();

    oversampler.reset();
    oversampler.initProcessing((size_t)samplesPerBlock);
    osSampleRate = oversampler.getOversamplingFactor() * sampleRate;

    for (int i = 0; i < eqp1a.size(); i++) {
        eqp1a[i]->prepare(osSampleRate);
    }
    setLatencySamples(oversampler.getLatencyInSamples());
}

//==============================================================================
void EQP1AAudioProcessor::prepareToPlay (double sampleRate, int samplesPerBlock)
{
    juce::dsp::ProcessSpec spec{};
    spec.maximumBlockSize = samplesPerBlock;
    spec.sampleRate = sampleRate;
    spec.numChannels = getTotalNumOutputChannels();

    gain.prepare(spec);
    gain.reset();

    // Frees up the heap memory
    for (auto i = 0; i < eqp1a.size(); i++) {
        delete eqp1a[i];
    }
    eqp1a.clear();

    float new_LoBoost = *parameters.getRawParameterValue(g_loBoostID) / 10.0f;
    float new_LoCut = *parameters.getRawParameterValue(g_loCutID) / 10.0f;
    float new_HiBoost = *parameters.getRawParameterValue(g_hiBoostID) / 10.0f;
    float new_HiCut = *parameters.getRawParameterValue(g_hiCutID) / 10.0f;
    float new_HiBQ = *parameters.getRawParameterValue(g_hiBQID) / 10.0f;
    auto new_HiBoostFreq = dynamic_cast<juce::AudioParameterChoice*>(parameters.getParameter(g_hiBoostFreqID))->getIndex();
    auto new_HighCutFreq = dynamic_cast<juce::AudioParameterChoice*>(parameters.getParameter(g_hiCutFreqID))->getIndex();
    auto new_LoFreq = dynamic_cast<juce::AudioParameterChoice*>(parameters.getParameter(g_loFreqID))->getIndex();

    for (int i = 0; i < getNumOutputChannels(); i++) {
        eqp1a.push_back(new EQP1A);
        eqp1a[i]->setParams(new_LoBoost, new_LoCut, new_HiBoost, new_HiCut, new_HiBQ, new_LoFreq, new_HiBoostFreq, new_HighCutFreq);
    }

    prepareOversampling(sampleRate, samplesPerBlock);
}

void EQP1AAudioProcessor::releaseResources()
{
    for (auto i = 0; i < eqp1a.size(); i++) {
        delete eqp1a[i];
    }
    eqp1a.clear();
}

#ifndef JucePlugin_PreferredChannelConfigurations
bool EQP1AAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
    if (layouts.getMainOutputChannelSet() != juce::AudioChannelSet::mono()
        && layouts.getMainOutputChannelSet() != juce::AudioChannelSet::stereo())
        return false;

    if (layouts.getMainOutputChannelSet() != layouts.getMainInputChannelSet())
        return false;

    return true;
}
#endif

void EQP1AAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages)
{   
    if (bypassed) {
		processBlockBypassed(buffer, midiMessages);
		return;
	}

    juce::ScopedNoDenormals noDenormals;
    auto totalNumInputChannels = getTotalNumInputChannels();
    auto totalNumOutputChannels = getTotalNumOutputChannels();

    juce::dsp::AudioBlock<float> block (buffer);
    juce::dsp::AudioBlock<float> osBlock = oversampler.processSamplesUp(block);

    for (auto i = totalNumInputChannels; i < totalNumOutputChannels; ++i)
        buffer.clear (i, 0, buffer.getNumSamples());

    for (int channel = 0; channel < totalNumInputChannels; ++channel) {
        for (int i = 0; i < osBlock.getNumSamples(); i++) {
            osBlock.setSample(channel, i, eqp1a[channel]->processSample(osBlock.getSample(channel, i)));
        }
    }
    oversampler.processSamplesDown(block);

    gain.process(dsp::ProcessContextReplacing<float>(block));
    
    if (osFactorChanged) {
        prepareOversampling(getSampleRate(), getBlockSize());
        osFactorChanged = false;
    }
}

void EQP1AAudioProcessor::processBlockBypassed(AudioBuffer<float>& buffer, MidiBuffer& midiMessages)
{
    if (bypassed) {
        auto bypassParam = getBypassParameter();
        bypassParam->operator=(true);
	}

    if (osFactorChanged) {
        prepareOversampling(getSampleRate(), getBlockSize());
        osFactorChanged = false;
    }
}

//==============================================================================
bool EQP1AAudioProcessor::hasEditor() const
{
    return true;
}

juce::AudioProcessorEditor* EQP1AAudioProcessor::createEditor()
{
    return new EQP1AAudioProcessorEditor(*this);
}

//==============================================================================
void EQP1AAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    juce::ValueTree combinedState("CombinedParameters");
    combinedState.appendChild(parameters.copyState(), nullptr);
    combinedState.appendChild(nonAutomatableParameters.copyState(), nullptr);

    std::unique_ptr<juce::XmlElement> xml(combinedState.createXml());
    copyXmlToBinary(*xml, destData);
}

void EQP1AAudioProcessor::setStateInformation (const void* data, int sizeInBytes)
{   std::unique_ptr<juce::XmlElement> xmlState(getXmlFromBinary(data, sizeInBytes));

    if (xmlState != nullptr && xmlState->hasTagName("CombinedParameters"))
    {
        // Split the combined ValueTree back into parameters and nonAutomatableParameters
        juce::ValueTree combinedState("CombinedParameters");
        combinedState = juce::ValueTree::fromXml(*xmlState);

        for (int i = 0; i < combinedState.getNumChildren(); ++i)
        {
            juce::ValueTree child = combinedState.getChild(i);
            if (child.hasType(parameters.state.getType()))
                parameters.replaceState(child);
            else if (child.hasType(nonAutomatableParameters.state.getType()))
                nonAutomatableParameters.replaceState(child);   
        }
    }
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new EQP1AAudioProcessor();
}

juce::AudioParameterBool* EQP1AAudioProcessor::getBypassParameter() const{
    return dynamic_cast<juce::AudioParameterBool*>(nonAutomatableParameters.getParameter(g_bypassID));
};