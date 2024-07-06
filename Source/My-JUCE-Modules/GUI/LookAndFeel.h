#pragma once

#include "JuceHeader.h"

//==============================================================================
/*
*/
namespace MyJUCEModules {
    /**
    *   @brief Custom LookAndFeel used for the PluginPanel component.
    **/
    class PluginPanelLookAndFeel : public juce::LookAndFeel_V4
    {
    public:
        PluginPanelLookAndFeel();
        juce::Font getComboBoxFont(juce::ComboBox& box) override;
        void positionComboBoxText(juce::ComboBox& box, juce::Label& label) override;
        void drawComboBox(juce::Graphics& g, int width, int height, bool isButtonDown, int buttonX, int buttonY, int buttonW, int buttonH, juce::ComboBox& box) override;
        void drawButtonBackground(juce::Graphics& g, juce::Button& button, const juce::Colour& backgroundColour, bool shouldDrawButtonAsHighlighted, bool shouldDrawButtonAsDown) override;
        void setCornerSize(float cornerSize);
        void drawImageButton(juce::Graphics&, juce::Image*, int imageX, int imageY, int imageW, int imageH, const juce::Colour& overlayColour, float imageOpacity, juce::ImageButton&) override;
    private:
        juce::Colour baseTextColour = juce::Colours::gainsboro.darker().darker().darker().darker();
        float cornerSize = 4.0f;
    };
}