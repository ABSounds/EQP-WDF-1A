/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin editor.

  ==============================================================================
*/

#include "PluginEditor.h"
#include "ParameterIDs.h"

constexpr double FACTOR = 1.5;
constexpr double BACKGROUND_WIDTH = 1450 / FACTOR;
constexpr double BACKGROUND_HEIGHT = 392 / FACTOR;
constexpr double SWITCH_SIZE_OFF = 57/ FACTOR;
constexpr double SWITCH_SIZE_ON = 69.5 / FACTOR;
constexpr double HEXKNOB_SIZE = 115 / FACTOR;
constexpr double CHICKENKNOB_SIZE = 88 / FACTOR;
constexpr double SELECTORKNOB_SIZE = 115 / FACTOR;
constexpr double JEWEL_SIZE = 55 / FACTOR;
constexpr double PLUGIN_PANEL_HEIGHT = 25;

//==============================================================================
EQP1AAudioProcessorEditor::EQP1AAudioProcessorEditor(EQP1AAudioProcessor& p)
    : AudioProcessorEditor(&p), audioProcessor(p)
    , bypassButton("bypassButton", juce::Colours::black, juce::Colours::black, juce::Colours::black)
    , pluginPanel(audioProcessor.presetManager, audioProcessor.undoManager, audioProcessor.nonAutomatableParameters)
{
    // This is used to catch key presses
    getTopLevelComponent()->addKeyListener(this);
    setWantsKeyboardFocus(true);

    using SliderAttachment = juce::AudioProcessorValueTreeState::SliderAttachment;

    p.nonAutomatableParameters.addParameterListener(g_bypassID, this);
    p.nonAutomatableParameters.addParameterListener(g_osFactorID, this);

    setResizeLimits(BACKGROUND_WIDTH/1.5, (BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT)/1.5, BACKGROUND_WIDTH * 1.5, (BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) * 1.5);
    double aspectRatio = (double)BACKGROUND_WIDTH / (double)(BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT);
    getConstrainer()->setFixedAspectRatio(aspectRatio);

    setSize(BACKGROUND_WIDTH, BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT);
    pluginBackground = ImageCache::getFromMemory(BinaryData::Background_png, BinaryData::Background_pngSize);
    switchOFF = ImageCache::getFromMemory(BinaryData::SwitchOFF_png, BinaryData::SwitchOFF_pngSize);
    switchON = ImageCache::getFromMemory(BinaryData::SwitchON_png, BinaryData::SwitchON_pngSize);
    jewelON = ImageCache::getFromMemory(BinaryData::JewelON_png, BinaryData::JewelON_pngSize);
    jewelOFF = ImageCache::getFromMemory(BinaryData::JewelOFF_png, BinaryData::JewelOFF_pngSize);

    LoBoostSlider.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    LoBoostSlider.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    LoBoostSlider.setLookAndFeel(&customLFHex);
    addAndMakeVisible(LoBoostSlider);
    LoBoostSliderAttachment = std::make_unique<SliderAttachment>(audioProcessor.parameters, g_loBoostID, LoBoostSlider);

    LoCutSlider.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    LoCutSlider.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    LoCutSlider.setLookAndFeel(&customLFHex);
    addAndMakeVisible(LoCutSlider);
    LoCutSliderAttachment = std::make_unique<SliderAttachment>(audioProcessor.parameters, g_loCutID, LoCutSlider);

    HiBoostSlider.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    HiBoostSlider.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    HiBoostSlider.setLookAndFeel(&customLFHex);
    addAndMakeVisible(HiBoostSlider);
    HiBoostSliderAttachment = std::make_unique<SliderAttachment>(audioProcessor.parameters, g_hiBoostID, HiBoostSlider);

    HiCutSlider.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    HiCutSlider.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    HiCutSlider.setLookAndFeel(&customLFHex);
    addAndMakeVisible(HiCutSlider);
    HiCutSliderAttachment = std::make_unique<SliderAttachment>(audioProcessor.parameters, g_hiCutID, HiCutSlider);

    HiBQSlider.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    HiBQSlider.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    HiBQSlider.setLookAndFeel(&customLFHex);
    addAndMakeVisible(HiBQSlider);
    HiBQSliderAttachment = std::make_unique<SliderAttachment>(audioProcessor.parameters, g_hiBQID, HiBQSlider);

    GainSlider.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    GainSlider.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    GainSlider.setLookAndFeel(&customLFHex);
    addAndMakeVisible(GainSlider);
    GainSliderAttachment = std::make_unique<SliderAttachment>(audioProcessor.parameters, g_gainID, GainSlider);

    LoFreqSelector.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    LoFreqSelector.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    LoFreqSelector.setLookAndFeel(&customLFSelectorLo);
    addAndMakeVisible(LoFreqSelector);
    LoFreqSelectorAttachment = std::make_unique<SliderAttachment>(audioProcessor.parameters, g_loFreqID, LoFreqSelector);

    HiBoostSelector.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    HiBoostSelector.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    HiBoostSelector.setLookAndFeel(&customLFSelectorHi);
    addAndMakeVisible(HiBoostSelector);
    HiBoostSelectorAttachment = std::make_unique<SliderAttachment>(audioProcessor.parameters, g_hiBoostFreqID, HiBoostSelector);

    HiCutSelector.setSliderStyle(juce::Slider::SliderStyle::RotaryHorizontalVerticalDrag);
    HiCutSelector.setTextBoxStyle(juce::Slider::NoTextBox, true, 100, 25);
    HiCutSelector.setLookAndFeel(&customLFChicken);
    addAndMakeVisible(HiCutSelector);
    HiCutSelectorAttachment = std::make_unique<SliderAttachment>(audioProcessor.parameters, g_hiCutFreqID, HiCutSelector);

    oversamplingButton.setButtonText("Oversampling " + audioProcessor.osText);
    addAndMakeVisible(oversamplingButton);
    oversamplingButton.onClick = [this]() {
        audioProcessor.osChoice = (audioProcessor.osChoice + 1) % 3;
        auto* osFactorParam = dynamic_cast<juce::AudioParameterChoice*>(audioProcessor.nonAutomatableParameters.getParameter(g_osFactorID));
        osFactorParam->operator=(audioProcessor.osChoice);
        oversamplingButton.setButtonText("Oversampling " + audioProcessor.osText);
    };

    addAndMakeVisible(pluginPanel);

    bypassButton.setAlpha(0.0f);
    bypassButton.setOpaque(false);
    bypassButton.setClickingTogglesState(true);
	addAndMakeVisible(bypassButton);
    bypassButtonAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ButtonAttachment>(audioProcessor.nonAutomatableParameters, g_bypassID, bypassButton);
}

EQP1AAudioProcessorEditor::~EQP1AAudioProcessorEditor()
{
    juce::LookAndFeel_V4::setDefaultLookAndFeel(nullptr);

    audioProcessor.nonAutomatableParameters.removeParameterListener(g_bypassID, this);
    audioProcessor.nonAutomatableParameters.removeParameterListener(g_osFactorID, this);
}

//==============================================================================
void EQP1AAudioProcessorEditor::paint (juce::Graphics& g)
{
    g.setImageResamplingQuality(juce::Graphics::ResamplingQuality::highResamplingQuality);

    auto pluginPanelHeight = pluginPanel.getHeight();

    auto backgroundBounds = getLocalBounds().toFloat();
    backgroundBounds.removeFromTop(pluginPanelHeight);

    g.drawImage(pluginBackground, backgroundBounds);
    if (!audioProcessor.getBypassParameter()->get()) {
        g.drawImage(switchON, getLocalBounds().getWidth() * 0.2085f, getLocalBounds().getHeight() * 0.6258f * BACKGROUND_HEIGHT / (BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) + pluginPanelHeight,
            getLocalBounds().getWidth() / (BACKGROUND_WIDTH / SWITCH_SIZE_OFF), getLocalBounds().getHeight() / ((BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) / SWITCH_SIZE_ON),
            0, 0, switchON.getWidth(), switchON.getHeight());
        
        g.drawImage(jewelON, getLocalBounds().getWidth() / 1.387f, getLocalBounds().getHeight() * BACKGROUND_HEIGHT / (BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) / 1.9f + pluginPanelHeight,
            getLocalBounds().getWidth() / (BACKGROUND_WIDTH / JEWEL_SIZE), getLocalBounds().getHeight() / ((BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) / JEWEL_SIZE),
            0, 0, jewelON.getWidth(), jewelON.getHeight());
    }
    else{
		g.drawImage(switchOFF, getLocalBounds().getWidth() * 0.2085f, getLocalBounds().getHeight() * 0.66f * BACKGROUND_HEIGHT / (BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) + pluginPanelHeight,
            getLocalBounds().getWidth() / (BACKGROUND_WIDTH / SWITCH_SIZE_OFF), getLocalBounds().getHeight() / ((BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) / SWITCH_SIZE_OFF),
            0, 0, switchOFF.getWidth(), switchOFF.getHeight());
        g.drawImage(jewelOFF, getLocalBounds().getWidth() / 1.387f, getLocalBounds().getHeight() * BACKGROUND_HEIGHT / (BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) / 1.9f + pluginPanelHeight,
            getLocalBounds().getWidth() / (BACKGROUND_WIDTH / JEWEL_SIZE), getLocalBounds().getHeight() / ((BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT)/ JEWEL_SIZE),
            0, 0, jewelOFF.getWidth(), jewelOFF.getHeight());
    }
}

void EQP1AAudioProcessorEditor::resized()
{
    int x = 0;
    int y = 0;
    int width = getLocalBounds().getWidth();
    int pluginPanelHeight = getLocalBounds().getHeight() / ((BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) / PLUGIN_PANEL_HEIGHT);

    pluginPanel.setBounds(juce::Rectangle<int>(x, y, width, pluginPanelHeight));

    x = getLocalBounds().getWidth() / 4.01f;
    y = getLocalBounds().getHeight() * BACKGROUND_HEIGHT / (BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) / 8.1666f;
    width = getLocalBounds().getWidth() / (BACKGROUND_WIDTH / HEXKNOB_SIZE);
    int height = getLocalBounds().getHeight() / ((BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT)/ HEXKNOB_SIZE);
    LoBoostSlider.setBounds(juce::Rectangle<int>(x, y + pluginPanelHeight, width, height));

    x = getLocalBounds().getWidth() / 2.67f;
    LoCutSlider.setBounds(juce::Rectangle<int>(x, y + pluginPanelHeight, width, height));

    x = getLocalBounds().getWidth() / 1.833f;
    HiBoostSlider.setBounds(juce::Rectangle<int>(x, y + pluginPanelHeight, width, height));

    x = getLocalBounds().getWidth() / 1.491f;
    HiCutSlider.setBounds(juce::Rectangle<int>(x, y + pluginPanelHeight, width, height));

    x = getLocalBounds().getWidth() / 2.177f;
    y = getLocalBounds().getHeight() * BACKGROUND_HEIGHT / (BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) / 1.6666f;
    HiBQSlider.setBounds(juce::Rectangle<int>(x, y + pluginPanelHeight, width, height));

    x = getLocalBounds().getWidth() / 1.256f;
    y = getLocalBounds().getHeight() * BACKGROUND_HEIGHT / (BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) / 1.6666f;
    GainSlider.setBounds(juce::Rectangle<int>(x, y + pluginPanelHeight, width, height));

    x = getLocalBounds().getWidth() / 1.242f;
    y = getLocalBounds().getHeight() * BACKGROUND_HEIGHT / (BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) / 8.5f;
    width = getLocalBounds().getWidth() / (BACKGROUND_WIDTH / CHICKENKNOB_SIZE);
    height = getLocalBounds().getHeight() / ((BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) / CHICKENKNOB_SIZE);
    HiCutSelector.setBounds(juce::Rectangle<int>(x, y + pluginPanelHeight, width, height));

    x = getLocalBounds().getWidth() / 3.22f;
    y = getLocalBounds().getHeight() * BACKGROUND_HEIGHT / (BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) / 1.6666f;
    width = getLocalBounds().getWidth() / (BACKGROUND_WIDTH / SELECTORKNOB_SIZE);
    height = getLocalBounds().getHeight() / ((BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) / SELECTORKNOB_SIZE);
    LoFreqSelector.setBounds(juce::Rectangle<int>(x, y + pluginPanelHeight, width, height));

    x = getLocalBounds().getWidth() / 1.645f;
    y = getLocalBounds().getHeight() * BACKGROUND_HEIGHT / (BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) / 1.6666f;
    width = getLocalBounds().getWidth() / (BACKGROUND_WIDTH / SELECTORKNOB_SIZE);
    height = getLocalBounds().getHeight() / ((BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) / SELECTORKNOB_SIZE);
    HiBoostSelector.setBounds(juce::Rectangle<int>(x, y + pluginPanelHeight, width, height));

    bypassButton.setBounds(getLocalBounds().getWidth() * 0.2085f, getLocalBounds().getHeight() * 0.66f * BACKGROUND_HEIGHT / (BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) + pluginPanelHeight,
        getLocalBounds().getWidth() / (BACKGROUND_WIDTH / SWITCH_SIZE_OFF), getLocalBounds().getHeight() / ((BACKGROUND_HEIGHT + PLUGIN_PANEL_HEIGHT) / SWITCH_SIZE_OFF));
}

void EQP1AAudioProcessorEditor::parameterChanged(const juce::String& parameterID, float newValue)
{
    if (parameterID == g_bypassID) {
        isBypassed = newValue;
        repaint();
	}
}

bool EQP1AAudioProcessorEditor::keyPressed(const juce::KeyPress& key, Component* originatingComponent) {
    if (key.getModifiers().isCommandDown() && (key.getKeyCode() == 'Z')) {
        if (key.getModifiers().isShiftDown()) {
            audioProcessor.undoManager.redo();
        }
        else {
            audioProcessor.undoManager.undo();
        }
        return true;
    }
    return false;
}