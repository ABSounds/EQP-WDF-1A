#include "LookAndFeel.h"

namespace MyJUCEModules {

    PluginPanelLookAndFeel::PluginPanelLookAndFeel() {
        setColour(juce::TextButton::ColourIds::buttonColourId, juce::Colours::gainsboro.darker());
        setColour(juce::TextButton::ColourIds::buttonOnColourId, juce::Colours::gainsboro.darker());
        setColour(juce::TextButton::ColourIds::textColourOnId, baseTextColour);
        setColour(juce::TextButton::ColourIds::textColourOffId, baseTextColour);
        setColour(juce::ComboBox::ColourIds::backgroundColourId, juce::Colours::gainsboro.darker().darker(0.2f));
        setColour(juce::ComboBox::ColourIds::outlineColourId, juce::Colours::gainsboro.darker().darker().darker());
        setColour(juce::ComboBox::ColourIds::arrowColourId, baseTextColour);
        setColour(juce::ComboBox::ColourIds::textColourId, baseTextColour.darker(0.2f));
        setColour(juce::PopupMenu::ColourIds::backgroundColourId, juce::Colours::gainsboro.darker());
        setColour(juce::PopupMenu::ColourIds::highlightedBackgroundColourId, juce::Colours::gainsboro.darker().darker());
        setColour(juce::PopupMenu::ColourIds::textColourId, baseTextColour);
        setColour(juce::PopupMenu::ColourIds::highlightedTextColourId, baseTextColour.darker());
        setColour(juce::PopupMenu::ColourIds::headerTextColourId, baseTextColour);
        setColour(juce::TooltipWindow::ColourIds::backgroundColourId, juce::Colours::gainsboro.darker());
        setColour(juce::TooltipWindow::ColourIds::textColourId, baseTextColour);
        setColour(juce::TooltipWindow::ColourIds::outlineColourId, juce::Colours::gainsboro.darker().darker().darker());
    }
    
    juce::Font PluginPanelLookAndFeel::getComboBoxFont(juce::ComboBox& box) {
        return { (float)box.getHeight() * 0.7f };
    };
    
    void PluginPanelLookAndFeel::positionComboBoxText(juce::ComboBox& box, juce::Label& label) {
        label.setBounds(0, 0, box.getWidth(), box.getHeight());
        label.setFont(getComboBoxFont(box));
    };
    
    void PluginPanelLookAndFeel::drawComboBox(juce::Graphics& g, int width, int height, bool isButtonDown, int buttonX, int buttonY, int buttonW, int buttonH, juce::ComboBox& box) {
        juce::Rectangle<int> boxBounds(0, 0, width, height);
        juce::Path path;

        auto bounds = boxBounds.toFloat().reduced(0.5f, 0.5f);
        
        path.addRoundedRectangle(bounds.getX(), bounds.getY(),
            bounds.getWidth(), bounds.getHeight(),
            cornerSize, cornerSize, true, true, true, true);
        
        g.setColour(box.findColour(juce::ComboBox::backgroundColourId));
        if (!box.isEnabled())
            g.setOpacity(0.5f);
        g.fillPath(path);

        g.setColour(box.findColour(juce::ComboBox::outlineColourId));
        g.strokePath(path, juce::PathStrokeType(1.5f));
    };

    void PluginPanelLookAndFeel::drawButtonBackground(juce::Graphics& g, juce::Button& button, const juce::Colour& backgroundColour, bool shouldDrawButtonAsHighlighted, bool shouldDrawButtonAsDown) {
        auto bounds = button.getLocalBounds().toFloat().reduced(0.5f, 0.5f);

        auto baseColour = backgroundColour.withMultipliedSaturation(button.hasKeyboardFocus(true) ? 1.3f : 0.9f)
            .withMultipliedAlpha(button.isEnabled() ? 1.0f : 0.5f);

        if (shouldDrawButtonAsDown || shouldDrawButtonAsHighlighted)
            baseColour = baseColour.contrasting(shouldDrawButtonAsDown ? 0.2f : 0.05f);
        
        if (!button.isEnabled())
            g.setOpacity(0.5f);
        g.setColour(baseColour);

        auto flatOnLeft = button.isConnectedOnLeft();
        auto flatOnRight = button.isConnectedOnRight();
        auto flatOnTop = button.isConnectedOnTop();
        auto flatOnBottom = button.isConnectedOnBottom();

        if (flatOnLeft || flatOnRight || flatOnTop || flatOnBottom)
        {
            juce::Path path;
            path.addRoundedRectangle(bounds.getX(), bounds.getY(),
                bounds.getWidth(), bounds.getHeight(),
                cornerSize, cornerSize,
                !(flatOnLeft || flatOnTop),
                !(flatOnRight || flatOnTop),
                !(flatOnLeft || flatOnBottom),
                !(flatOnRight || flatOnBottom));

            g.fillPath(path);

            g.setColour(button.findColour(juce::TextButton::buttonColourId));
            g.strokePath(path, juce::PathStrokeType(1.5f));
        }
        else
        {
            g.fillRoundedRectangle(bounds, cornerSize);

            g.setColour(button.findColour(juce::TextButton::buttonColourId));
            g.drawRoundedRectangle(bounds, cornerSize, 1.5f);
        }
    };
    void PluginPanelLookAndFeel::setCornerSize(float cornerSize) {
        this->cornerSize = cornerSize;
    };

    void PluginPanelLookAndFeel::drawImageButton(juce::Graphics& g, juce::Image* image, int imageX, int imageY, int imageW, int imageH, const juce::Colour& overlayColour, float imageOpacity, juce::ImageButton&) {
        juce::AffineTransform t = juce::RectanglePlacement(juce::RectanglePlacement::stretchToFit)
            .getTransformToFit(image->getBounds().toFloat(),
                juce::Rectangle<int>(imageX, imageY, imageW, imageH).toFloat());

        g.setOpacity(imageOpacity);
        g.drawImageTransformed(*image, t, false);
    }
}