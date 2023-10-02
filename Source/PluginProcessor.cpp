/*
  ==============================================================================

    This file contains the JUCE plugin processor for the EQP1A plugin.

  ==============================================================================
*/

#include "PluginProcessor.h"
#include "PluginEditor.h"

//==============================================================================
EQP1AAudioProcessor::EQP1AAudioProcessor()
#ifndef JucePlugin_PreferredChannelConfigurations
    : AudioProcessor(BusesProperties()
#if ! JucePlugin_IsMidiEffect
#if ! JucePlugin_IsSynth
        .withInput("Input", juce::AudioChannelSet::stereo(), true)
#endif
        .withOutput("Output", juce::AudioChannelSet::stereo(), true)
#endif
    )
    , params(*this, nullptr, "PARAMETERS", createParameters())
    , oversampler(getNumOutputChannels())
#endif
{   
    bypassParameter = new juce::AudioParameterBool("bypass", "Bypass", false);

    params.addParameterListener("gain", this);
    params.addParameterListener("lofreq", this);
    params.addParameterListener("loboost", this);
    params.addParameterListener("locut", this);
    params.addParameterListener("hiboostfreq", this);
    params.addParameterListener("hiboost", this);
    params.addParameterListener("hibq", this);
    params.addParameterListener("hicutfreq", this);
    params.addParameterListener("hicut", this);
    params.addParameterListener("osfactor", this);

    gain.setGainDecibels(0.0f);
}

EQP1AAudioProcessor::~EQP1AAudioProcessor()
{
    params.removeParameterListener("gain", this);
    params.removeParameterListener("lofreq", this);
    params.removeParameterListener("loboost", this);
    params.removeParameterListener("locut", this);
    params.removeParameterListener("hiboostfreq", this);
    params.removeParameterListener("hiboost", this);
    params.removeParameterListener("hibq", this);
    params.removeParameterListener("hicutfreq", this);
    params.removeParameterListener("hicut", this);
    params.removeParameterListener("osfactor", this);
}

//==============================================================================

juce::AudioProcessorValueTreeState::ParameterLayout EQP1AAudioProcessor::createParameters()
{
    std::vector <std::unique_ptr<juce::RangedAudioParameter>> params;
    auto loFreq = std::make_unique<juce::AudioParameterChoice>("lofreq", "LoFreq", StringArray{ "20 Hz", "30 Hz", "60 Hz", "100 Hz" }, 0);
    auto loBoost = std::make_unique<juce::AudioParameterFloat>("loboost", "LoBoost", juce::NormalisableRange<float>(0.0001f, 9.9999f, 0.0001f, 0.3f, false), 0.0001f);
    auto loCut = std::make_unique<juce::AudioParameterFloat>("locut", "LoCut", juce::NormalisableRange<float>(0.0001f, 9.9999f, 0.0001f, 0.3f, false), 0.0001f);
    auto hiBoostFreq = std::make_unique<juce::AudioParameterChoice>("hiboostfreq", "HiBoostFreq", StringArray{ "3 kHz", "4 kHz", "5 kHz", "8 kHz", "10 kHz", "12 kHz", "16 kHz"}, 2);
    auto hiBoost = std::make_unique<juce::AudioParameterFloat>("hiboost", "HiBoost", 0.0001f, 9.9999f, 0.0001f);
    auto hiBQ = std::make_unique<juce::AudioParameterFloat>("hibq", "HiBQ", 0.0001f, 9.9999f, 5.0f);
    auto hiCutFreq = std::make_unique<juce::AudioParameterChoice>("hicutfreq", "HiCutFreq", StringArray{ "5 kHz", "10 kHz", "20 kHz" }, 2);
    auto hiCut = std::make_unique<juce::AudioParameterFloat>("hicut", "HiCut", 0.0001f, 9.9999f, 0.0001f);
    auto osFactor = std::make_unique<juce::AudioParameterChoice>("osfactor", "Oversampling", StringArray{ "x1", "x2", "x4" }, 1);
    auto gain = std::make_unique<juce::AudioParameterFloat>("gain", "Gain", juce::NormalisableRange<float> { -20.f, 20.0f, 0.1f}, 0.0f);
    
    params.push_back(std::move(gain));
    params.push_back(std::move(loFreq));
    params.push_back(std::move(loBoost));
    params.push_back(std::move(loCut));
    params.push_back(std::move(hiBoostFreq));
    params.push_back(std::move(hiBoost));
    params.push_back(std::move(hiBQ));
    params.push_back(std::move(hiCutFreq));
    params.push_back(std::move(hiCut));
    params.push_back(std::move(osFactor));

    return { params.begin(), params.end() };
}

void EQP1AAudioProcessor::parameterChanged(const juce::String& parameterID, float newValue) {
    auto totalNumInputChannels = getTotalNumInputChannels();

    if (parameterID == "gain") {
        float gainValue = *params.getRawParameterValue("gain");
        gain.setGainDecibels(*params.getRawParameterValue("gain"));
    }

    if (parameterID == "lofreq") {
        auto* loBoostParam = dynamic_cast<juce::AudioParameterChoice*>(params.getParameter("lofreq"));
        auto new_LoFreq = loBoostParam->getIndex();
		for (int i = 0; i < eqp1a.size(); i++)
            eqp1a[i]->set_LoFreq(new_LoFreq);
	}

    if (parameterID == "loboost") {
        float new_LoBoost = *params.getRawParameterValue("loboost") / 10.0f;
        for (int i = 0; i < eqp1a.size(); i++)
            eqp1a[i]->set_LoBoost(new_LoBoost);
    }
    
    if (parameterID == "locut") {
		float new_LoCut = *params.getRawParameterValue("locut") / 10.0f;
        for (int i = 0; i < eqp1a.size(); i++)
		    eqp1a[i]->set_LoCut(new_LoCut);
	}

    if (parameterID == "hiboostfreq") {
		auto* hiBoostFreqParam = dynamic_cast<juce::AudioParameterChoice*>(params.getParameter("hiboostfreq"));
		int new_HiBoostFreq = hiBoostFreqParam->getIndex();
        for (int i = 0; i < eqp1a.size(); i++)
		    eqp1a[i]->set_HiBoostFreq(new_HiBoostFreq);
	}

    if (parameterID == "hiboost") {
		float new_HiBoost = *params.getRawParameterValue("hiboost") / 10.0f;
        for (int i = 0; i < eqp1a.size(); i++)
		    eqp1a[i]->set_HiBoost(new_HiBoost);
	}

    if (parameterID == "hibq") {
        float new_HiBQ = *params.getRawParameterValue("hibq") / 10.0f;
        for (int i = 0; i < eqp1a.size(); i++)
            eqp1a[i]->set_HiBQ(new_HiBQ);
    }

    if(parameterID == "hicut") {
		float new_HiCut = *params.getRawParameterValue("hicut") / 10.0f;
        for (int i = 0; i < eqp1a.size(); i++)
		    eqp1a[i]->set_HiCut(new_HiCut);
	}

    if (parameterID == "hicutfreq") {
        auto* hiCutParam = dynamic_cast<juce::AudioParameterChoice*>(params.getParameter("hicutfreq"));
        auto new_HighCutFreq = hiCutParam->getIndex();

        for (int i = 0; i < eqp1a.size(); i++)
            eqp1a[i]->set_HiCutFreq(new_HighCutFreq);
    }

    if (parameterID == "osfactor"){
		auto* osFactorParam = dynamic_cast<juce::AudioParameterChoice*>(params.getParameter("osfactor"));
        osText = osFactorParam->getCurrentChoiceName().toStdString();
        osFactor = static_cast<size_t>(std::log2f(std::stoi(osText.substr(1))));

        osFactorChanged = true;
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

    float new_LoBoost = *params.getRawParameterValue("loboost") / 10.0f;
    float new_LoCut = *params.getRawParameterValue("locut") / 10.0f;
    float new_HiBoost = *params.getRawParameterValue("hiboost") / 10.0f;
    float new_HiCut = *params.getRawParameterValue("hicut") / 10.0f;
    float new_HiBQ = *params.getRawParameterValue("hibq") / 10.0f;
    auto new_HiBoostFreq = dynamic_cast<juce::AudioParameterChoice*>(params.getParameter("hiboostfreq"))->getIndex();
    auto new_HighCutFreq = dynamic_cast<juce::AudioParameterChoice*>(params.getParameter("hicutfreq"))->getIndex();
    auto new_LoFreq = dynamic_cast<juce::AudioParameterChoice*>(params.getParameter("lofreq"))->getIndex();

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
  #if JucePlugin_IsMidiEffect
    juce::ignoreUnused (layouts);
    return true;
  #else
    if (layouts.getMainOutputChannelSet() != juce::AudioChannelSet::mono()
        && layouts.getMainOutputChannelSet() != juce::AudioChannelSet::stereo())
        return false;

   #if ! JucePlugin_IsSynth
    if (layouts.getMainOutputChannelSet() != layouts.getMainInputChannelSet())
        return false;
   #endif

    return true;
  #endif
}
#endif

void EQP1AAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages)
{   
    if (bypassParameter->get()) {
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
    if (!bypassParameter->get()) {
        bypassParameter->operator=(true);
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
{   auto state = params.copyState();
    std::unique_ptr<juce::XmlElement> xml(state.createXml());
    copyXmlToBinary(*xml, destData);
}

void EQP1AAudioProcessor::setStateInformation (const void* data, int sizeInBytes)
{   std::unique_ptr<juce::XmlElement> xmlState(getXmlFromBinary(data, sizeInBytes));

    if (xmlState.get() != nullptr)
        if (xmlState->hasTagName(params.state.getType()))
            params.replaceState(juce::ValueTree::fromXml(*xmlState));
}

//==============================================================================
// This creates new instances of the plugin..
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new EQP1AAudioProcessor();
}

juce::AudioParameterBool* EQP1AAudioProcessor::getBypassParameter() const{
    return bypassParameter;
};