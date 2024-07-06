/*
  ==============================================================================

    CustomLookAndFeel.cpp
    Created: 9 Aug 2023 10:52:09pm
    Author:  Alberto

  ==============================================================================
*/

#include "CustomLookAndFeel.h"

LookAndFeelHex::LookAndFeelHex() {
	hexKnob = ImageCache::getFromMemory(BinaryData::HexKnob_png, BinaryData::HexKnob_pngSize);
}

void LookAndFeelHex::drawRotarySlider(Graphics& g, int x, int y, int width, int height, float sliderPos, const float rotaryStartAngle, const float rotaryEndAngle, Slider& slider) {
    auto toAngle = (- 3 * juce::MathConstants<float>::pi / 4) - sliderPos * 2 * (-3 * juce::MathConstants<float>::pi / 4);
    auto bounds = Rectangle<int>(x, y, width, height).toFloat().reduced(1);
    
    g.addTransform(juce::AffineTransform().rotated(toAngle, bounds.getCentreX(), bounds.getCentreY()));
    g.drawImage(hexKnob, bounds, juce::RectanglePlacement::centred);
    //g.drawText((String)sliderPos, bounds, juce::Justification::centred);
}

//==============================================================================

LookAndFeelSelectorLo::LookAndFeelSelectorLo() {
    selectorKnob = ImageCache::getFromMemory(BinaryData::SelectorKnob_png, BinaryData::SelectorKnob_pngSize);
}

void LookAndFeelSelectorLo::drawRotarySlider(Graphics& g, int x, int y, int width, int height, float sliderPos, const float rotaryStartAngle, const float rotaryEndAngle, Slider& slider) {
    float angle = 0;

    if (sliderPos == 0.00) {
		angle = - juce::MathConstants<float>::pi / 4;
	}
    else if (sliderPos > 0.00 && sliderPos < 0.5) {
        angle = -juce::MathConstants<float>::pi / 12;
	}
    else if (sliderPos > 0.5 && sliderPos < 1.0) {
        angle = juce::MathConstants<float>::pi / 12;
    }
    else if (sliderPos == 1.0) {
        angle = juce::MathConstants<float>::pi / 4;
	}

    auto bounds = Rectangle<int>(x, y, width, height).toFloat();
    
    g.addTransform(juce::AffineTransform().rotated(angle, bounds.getCentreX(), bounds.getCentreY()));
    g.drawImage(selectorKnob, bounds, juce::RectanglePlacement::centred);
}

//==============================================================================

LookAndFeelSelectorHi::LookAndFeelSelectorHi() {
    selectorKnob = ImageCache::getFromMemory(BinaryData::SelectorKnob_png, BinaryData::SelectorKnob_pngSize);
}

void LookAndFeelSelectorHi::drawRotarySlider(Graphics& g, int x, int y, int width, int height, float sliderPos, const float rotaryStartAngle, const float rotaryEndAngle, Slider& slider) {
    auto toAngle = (-juce::MathConstants<float>::pi / 2) + sliderPos * 2 * (juce::MathConstants<float>::pi / 2);
    auto bounds = Rectangle<int>(x, y, width, height).toFloat();
    
    g.addTransform(juce::AffineTransform().rotated(toAngle, bounds.getCentreX(), bounds.getCentreY()));
    g.drawImage(selectorKnob, bounds, juce::RectanglePlacement::centred);
}

//==============================================================================

LookAndFeelChicken::LookAndFeelChicken() {
    chickenKnob = ImageCache::getFromMemory(BinaryData::ChickenheadKnob_png, BinaryData::ChickenheadKnob_pngSize);
}

void LookAndFeelChicken::drawRotarySlider(Graphics& g, int x, int y, int width, int height, float sliderPos, const float rotaryStartAngle, const float rotaryEndAngle, Slider& slider) {
    auto toAngle = - juce::MathConstants<float>::pi / 4 + sliderPos * 2 * juce::MathConstants<float>::pi / 4;
    auto bounds = Rectangle<int>(x, y, width, height).toFloat();

    g.addTransform(juce::AffineTransform().rotated(toAngle, bounds.getCentreX(), bounds.getCentreY()));
    g.drawImage(chickenKnob, bounds, juce::RectanglePlacement::centred);
}
