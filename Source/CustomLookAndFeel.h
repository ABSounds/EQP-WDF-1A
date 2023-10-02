/*
  ==============================================================================

    CustomLookAndFeel.h
    Created: 9 Aug 2023 10:52:09pm
    Author:  Alberto

  ==============================================================================
*/

#pragma once

#include <JuceHeader.h>

class LookAndFeelHex: public juce::LookAndFeel_V4
{
public:
    LookAndFeelHex();
    void drawRotarySlider(Graphics&, int x, int y, int width, int height, float sliderPosProportional, float rotaryStartAngle, float rotaryEndAngle, Slider&);
private:
	Image hexKnob;
};

class LookAndFeelSelectorLo: public juce::LookAndFeel_V4
{
public:
    LookAndFeelSelectorLo();
    void drawRotarySlider(Graphics&, int x, int y, int width, int height, float sliderPosProportional, float rotaryStartAngle, float rotaryEndAngle, Slider&);
private:
    Image selectorKnob;
};

class LookAndFeelSelectorHi : public juce::LookAndFeel_V4
{
public:
    LookAndFeelSelectorHi();
    void drawRotarySlider(Graphics&, int x, int y, int width, int height, float sliderPosProportional, float rotaryStartAngle, float rotaryEndAngle, Slider&);
private:
    Image selectorKnob;
};


class LookAndFeelChicken: public juce::LookAndFeel_V4
{
public:
    LookAndFeelChicken();
    void drawRotarySlider(Graphics&, int x, int y, int width, int height, float sliderPosProportional, float rotaryStartAngle, float rotaryEndAngle, Slider&);
private:
    Image chickenKnob;
};