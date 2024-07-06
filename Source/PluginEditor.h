/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin editor.

  ==============================================================================
*/

#pragma once

#include <JuceHeader.h>
#include "PluginProcessor.h"
#include "CustomLookAndFeel.h"
#include "My-JUCE-Modules/GUI/Components.h"

//==============================================================================
/**
*/
class EQP1AAudioProcessorEditor  : public juce::AudioProcessorEditor, juce::AudioProcessorValueTreeState::Listener, juce::KeyListener
{
public:
    EQP1AAudioProcessorEditor (EQP1AAudioProcessor&);
    ~EQP1AAudioProcessorEditor() override;

    //==============================================================================
    void paint (juce::Graphics&) override;
    void resized() override;

    bool keyPressed(const juce::KeyPress& key, Component* originatingComponent) override;

private:
    EQP1AAudioProcessor& audioProcessor;
    void parameterChanged(const juce::String& parameterID, float newValue) override;

    bool isBypassed = false;

    LookAndFeelHex customLFHex;
    LookAndFeelSelectorLo customLFSelectorLo;
    LookAndFeelSelectorHi customLFSelectorHi;
    LookAndFeelChicken customLFChicken;

    Image pluginBackground;
    Image switchOFF;
    Image switchON;
    Image jewelON;
    Image jewelOFF;

    juce::TextButton oversamplingButton;
    juce::ShapeButton bypassButton;

    // Sliders
    juce::Slider LoBoostSlider;
    juce::Slider LoCutSlider;
    juce::Slider HiBoostSlider;
    juce::Slider HiCutSlider;
    juce::Slider HiBQSlider;

    juce::Slider LoFreqSelector;
    juce::Slider HiBoostSelector;
    juce::Slider HiCutSelector;

    juce::Slider GainSlider;

    MyJUCEModules::PluginPanel pluginPanel;

    // Sliders attachments
    using SliderAttachment = juce::AudioProcessorValueTreeState::SliderAttachment;
    
    std::unique_ptr<SliderAttachment> LoBoostSliderAttachment;
    std::unique_ptr<SliderAttachment> LoCutSliderAttachment;
    std::unique_ptr<SliderAttachment> HiBoostSliderAttachment;
    std::unique_ptr<SliderAttachment> HiCutSliderAttachment;
    std::unique_ptr<SliderAttachment> HiBQSliderAttachment;

    std::unique_ptr<SliderAttachment> LoFreqSelectorAttachment;
    std::unique_ptr<SliderAttachment> HiBoostSelectorAttachment;
    std::unique_ptr<SliderAttachment> HiCutSelectorAttachment;

    std::unique_ptr<SliderAttachment> GainSliderAttachment;

    std::unique_ptr<juce::AudioProcessorValueTreeState::ButtonAttachment> bypassButtonAttachment;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (EQP1AAudioProcessorEditor)
};
