/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin editor.

  ==============================================================================
*/

#include "PluginEditor.h"

constexpr double FACTOR = 1.5;
constexpr double BACKGROUND_WIDTH = 1450 / FACTOR;
constexpr double BACKGROUND_HEIGHT = 392 / FACTOR;
constexpr double SWITCH_SIZE = 57/ FACTOR;
constexpr double HEXKNOB_SIZE = 115 / FACTOR;
constexpr double CHICKENKNOB_SIZE = 88 / FACTOR;
constexpr double SELECTORKNOB_SIZE = 115 / FACTOR;
constexpr double JEWEL_SIZE = 55 / FACTOR;

//==============================================================================
EQP1AAudioProcessorEditor::EQP1AAudioProcessorEditor(EQP1AAudioProcessor& p)
    : AudioProcessorEditor(&p), audioProcessor(p)
    , bypassButton("bypassButton", juce::Colours::black, juce::Colours::black, juce::Colours::black)
{
    using SliderAttachment = juce::AudioProcessorValueTreeState::SliderAttachment;

    setResizeLimits(BACKGROUND_WIDTH/1.5, BACKGROUND_HEIGHT/1.5, BACKGROUND_WIDTH * 1.5, BACKGROUND_HEIGHT * 1.5);
    double aspectRatio = (double)BACKGROUND_WIDTH / (double)BACKGROUND_HEIGHT;
    getConstrainer()->setFixedAspectRatio(aspectRatio);

    setSize(BACKGROUND_WIDTH, BACKGROUND_HEIGHT);
    pluginBackground = ImageCache::getFromMemory(BinaryData::Background_png, BinaryData::Background_pngSize);
    switchOFF = ImageCache::getFromMemory(BinaryData::SwitchOFF_png, BinaryData::SwitchOFF_pngSize);
    switchON = ImageCache::getFromMemory(BinaryData::SwitchON_png, BinaryData::SwitchON_pngSize);
    jewelON = ImageCache::getFromMemory(BinaryData::JewelON_png, BinaryData::JewelON_pngSize);
    jewelOFF = ImageCache::getFromMemory(BinaryData::JewelOFF_png, BinaryData::JewelOFF_pngSize);

    LoBoostSlider.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    LoBoostSlider.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    LoBoostSlider.setRange(0.0f, 1.0f, 0.0001f);
    LoBoostSlider.setValue(0.0f);
    LoBoostSlider.setLookAndFeel(&customLFHex);
    addAndMakeVisible(LoBoostSlider);
    LoBoostSliderAttachment = std::make_unique<SliderAttachment>(audioProcessor.params, "loboost", LoBoostSlider);

    LoCutSlider.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    LoCutSlider.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    LoCutSlider.setRange(0.0f, 1.0f, 0.0001f);
    LoCutSlider.setValue(0.0f);
    LoCutSlider.setLookAndFeel(&customLFHex);
    addAndMakeVisible(LoCutSlider);
    LoCutSliderAttachment = std::make_unique<SliderAttachment>(audioProcessor.params, "locut", LoCutSlider);

    HiBoostSlider.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    HiBoostSlider.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    HiBoostSlider.setRange(0.0f, 1.0f, 0.01f);
    HiBoostSlider.setValue(0.0f);
    HiBoostSlider.setLookAndFeel(&customLFHex);
    addAndMakeVisible(HiBoostSlider);
    HiBoostSliderAttachment = std::make_unique<SliderAttachment>(audioProcessor.params, "hiboost", HiBoostSlider);

    HiCutSlider.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    HiCutSlider.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    HiCutSlider.setRange(0.0f, 1.0f, 0.01f);
    HiCutSlider.setValue(0.0f);
    HiCutSlider.setLookAndFeel(&customLFHex);
    addAndMakeVisible(HiCutSlider);
    HiCutSliderAttachment = std::make_unique<SliderAttachment>(audioProcessor.params, "hicut", HiCutSlider);

    HiBQSlider.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    HiBQSlider.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    HiBQSlider.setRange(0.0f, 1.0f, 0.01f);
    HiBQSlider.setValue(0.0f);
    HiBQSlider.setLookAndFeel(&customLFHex);
    addAndMakeVisible(HiBQSlider);
    HiBQSliderAttachment = std::make_unique<SliderAttachment>(audioProcessor.params, "hibq", HiBQSlider);

    GainSlider.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    GainSlider.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    GainSlider.setRange(- 20.0f, 20.0f, 0.01f);
    GainSlider.setLookAndFeel(&customLFHex);
    addAndMakeVisible(GainSlider);
    GainSliderAttachment = std::make_unique<SliderAttachment>(audioProcessor.params, "gain", GainSlider);

    LoFreqSelector.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    LoFreqSelector.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    LoFreqSelector.setRange(0.0f, 3.0f, 1.0f);
    LoFreqSelector.setValue(0.0f);
    LoFreqSelector.setLookAndFeel(&customLFSelectorLo);
    addAndMakeVisible(LoFreqSelector);
    LoFreqSelectorAttachment = std::make_unique<SliderAttachment>(audioProcessor.params, "lofreq", LoFreqSelector);

    HiBoostSelector.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    HiBoostSelector.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    HiBoostSelector.setRange(0, 6, 1);
    HiBoostSelector.setLookAndFeel(&customLFSelectorHi);
    addAndMakeVisible(HiBoostSelector);
    HiBoostSelectorAttachment = std::make_unique<SliderAttachment>(audioProcessor.params, "hiboostfreq", HiBoostSelector);

    HiCutSelector.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    HiCutSelector.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    HiCutSelector.setRange(0.0f, 2.0f, 1.0f);
    HiBoostSelector.setValue(2.0f);
    HiCutSelector.setLookAndFeel(&customLFChicken);
    addAndMakeVisible(HiCutSelector);
    HiCutSelectorAttachment = std::make_unique<SliderAttachment>(audioProcessor.params, "hicutfreq", HiCutSelector);

    oversamplingButton.setButtonText("Oversampling " + audioProcessor.osText);
    addAndMakeVisible(oversamplingButton);
    oversamplingButton.onClick = [this]() {
        if (audioProcessor.osChoice < 2)
            audioProcessor.osChoice++;
		else
			audioProcessor.osChoice = 0;
        auto* osFactorParam = dynamic_cast<juce::AudioParameterChoice*>(audioProcessor.params.getParameter("osfactor"));
        osFactorParam->operator=(audioProcessor.osChoice);
        oversamplingButton.setButtonText("Oversampling " + audioProcessor.osText);
    };

    bypassButton.setAlpha(0);
    bypassButton.setOpaque(false);
	addAndMakeVisible(bypassButton);
    bypassButton.onClick = [this]() {
        auto* bypassParam = dynamic_cast<juce::AudioParameterBool*>(audioProcessor.getBypassParameter());
		bypassParam->operator=(!bypassParam->get());
        repaint();
	};

    startTimerHz(20);
}

EQP1AAudioProcessorEditor::~EQP1AAudioProcessorEditor()
{
    juce::LookAndFeel_V4::setDefaultLookAndFeel(nullptr);
}

//==============================================================================
void EQP1AAudioProcessorEditor::paint (juce::Graphics& g)
{
    g.setImageResamplingQuality(juce::Graphics::ResamplingQuality::highResamplingQuality);

    g.drawImage(pluginBackground, getLocalBounds().toFloat());
    if (!audioProcessor.getBypassParameter()->get()) {
        g.drawImage(switchON, getLocalBounds().getWidth() * 0.2085f, getLocalBounds().getHeight() * 0.66f,
            getLocalBounds().getWidth() / (BACKGROUND_WIDTH / SWITCH_SIZE), getLocalBounds().getHeight() / (BACKGROUND_HEIGHT / SWITCH_SIZE),
            0, 0, switchON.getWidth(), switchON.getHeight());
        
        g.drawImage(jewelON, getLocalBounds().getWidth() / 1.387f, getLocalBounds().getHeight() / 1.9f,
            getLocalBounds().getWidth() / (BACKGROUND_WIDTH / JEWEL_SIZE), getLocalBounds().getHeight() / (BACKGROUND_HEIGHT / JEWEL_SIZE),
            0, 0, jewelON.getWidth(), jewelON.getHeight());
    }
    else{
		g.drawImage(switchOFF, getLocalBounds().getWidth() * 0.2085f, getLocalBounds().getHeight() * 0.66f,
            getLocalBounds().getWidth() / (BACKGROUND_WIDTH / SWITCH_SIZE), getLocalBounds().getHeight() / (BACKGROUND_HEIGHT / SWITCH_SIZE),
            0, 0, switchOFF.getWidth(), switchOFF.getHeight());
        g.drawImage(jewelOFF, getLocalBounds().getWidth() / 1.387f, getLocalBounds().getHeight() / 1.9f,
            getLocalBounds().getWidth() / (BACKGROUND_WIDTH / JEWEL_SIZE), getLocalBounds().getHeight() / (BACKGROUND_HEIGHT / JEWEL_SIZE),
            0, 0, jewelOFF.getWidth(), jewelOFF.getHeight());
    }
}

void EQP1AAudioProcessorEditor::resized()
{
    x = getLocalBounds().getWidth() / 4.01f;
    y = getLocalBounds().getHeight() / 8.1666f;
    width = getLocalBounds().getWidth() / (BACKGROUND_WIDTH / HEXKNOB_SIZE);
    height = getLocalBounds().getHeight() / (BACKGROUND_HEIGHT / HEXKNOB_SIZE);
    LoBoostSlider.setBounds(juce::Rectangle<int>(x, y, width, height));

    x = getLocalBounds().getWidth() / 2.67f;
    LoCutSlider.setBounds(juce::Rectangle<int>(x, y, width, height));

    x = getLocalBounds().getWidth() / 1.833f;
    HiBoostSlider.setBounds(juce::Rectangle<int>(x, y, width, height));

    x = getLocalBounds().getWidth() / 1.491f;
    HiCutSlider.setBounds(juce::Rectangle<int>(x, y, width, height));

    x = getLocalBounds().getWidth() / 2.177f;
    y = getLocalBounds().getHeight() / 1.6666f;
    HiBQSlider.setBounds(juce::Rectangle<int>(x, y, width, height));

    x = getLocalBounds().getWidth() / 1.256f;
    y = getLocalBounds().getHeight() / 1.6666f;
    GainSlider.setBounds(juce::Rectangle<int>(x, y, width, height));

    x = getLocalBounds().getWidth() / 1.242f;
    y = getLocalBounds().getHeight() / 8.5f;
    width = getLocalBounds().getWidth() / (BACKGROUND_WIDTH / CHICKENKNOB_SIZE);
    height = getLocalBounds().getHeight() / (BACKGROUND_HEIGHT / CHICKENKNOB_SIZE);
    HiCutSelector.setBounds(juce::Rectangle<int>(x, y, width, height));

    x = getLocalBounds().getWidth() / 3.22f;
    y = getLocalBounds().getHeight() / 1.6666f;
    width = getLocalBounds().getWidth() / (BACKGROUND_WIDTH / SELECTORKNOB_SIZE);
    height = getLocalBounds().getHeight() / (BACKGROUND_HEIGHT / SELECTORKNOB_SIZE);
    LoFreqSelector.setBounds(juce::Rectangle<int>(x, y, width, height));

    x = getLocalBounds().getWidth() / 1.645f;
    y = getLocalBounds().getHeight() / 1.6666f;
    width = getLocalBounds().getWidth() / (BACKGROUND_WIDTH / SELECTORKNOB_SIZE);
    height = getLocalBounds().getHeight() / (BACKGROUND_HEIGHT / SELECTORKNOB_SIZE);
    HiBoostSelector.setBounds(juce::Rectangle<int>(x, y, width, height));

    width = getLocalBounds().getWidth() / 9.66f;
    height = getLocalBounds().getHeight() / 13.07f;
    x = getLocalBounds().getWidth() / 193.33f;
    y = getLocalBounds().getWidth() / 193.33f;
    oversamplingButton.setBounds(juce::Rectangle<int>(x, y, width, height));

    bypassButton.setBounds(getLocalBounds().getWidth() * 0.2085f, getLocalBounds().getHeight() * 0.66f,
        getLocalBounds().getWidth() / (BACKGROUND_WIDTH / SWITCH_SIZE), getLocalBounds().getHeight() / (BACKGROUND_HEIGHT / SWITCH_SIZE));
}

void EQP1AAudioProcessorEditor::timerCallback()
{
    if (audioProcessor.getBypassParameter()->get() != isBypassed) {
		isBypassed = audioProcessor.getBypassParameter()->get();
		repaint();
	}
}