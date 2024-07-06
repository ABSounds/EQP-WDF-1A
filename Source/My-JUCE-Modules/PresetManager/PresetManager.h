#pragma once

#include "JuceHeader.h"

namespace MyJUCEModules {
	/**
	*   @brief Preset manager class to manage the presets of the plugin and A/B states.
	**/
	class PresetManager {
	public:
		const juce::File defaultDirectory;
		const juce::String extension{ "preset" };

		/**
		*   @brief Preset manager class to manage the presets of the plugin and A/B states.
		*	@param apvts Reference to the plugin's AudioProcessorValueTreeState to be affected by the preset manager.
		*	@param dd Default directory to save and load presets from.
		**/
		PresetManager(juce::AudioProcessorValueTreeState& apvts, juce::File dd) : defaultDirectory(dd), valueTreeState(apvts)
		{
			otherValueTree = valueTreeState.copyState();
			if (!defaultDirectory.exists()) {
				const auto result = defaultDirectory.createDirectory();
				if (result.failed()) {
					DBG("Failed to create preset directory");
					jassertfalse;
				}
			}
		}

		void savePreset(const juce::File& presetFile) {
			if (presetFile.getFullPathName().isEmpty())
				return;

			auto stateCopy = valueTreeState.copyState();

			const auto xml = stateCopy.createXml();
			if (!xml->writeTo(presetFile)) {
				DBG("Failed to write preset: " + presetFile.getFullPathName());
				jassertfalse;
			}
			currentPresetName = presetFile.getFileNameWithoutExtension();
		}

		void loadPreset(const juce::File& presetFile) {
			if (presetFile.getFullPathName().isEmpty())
				return;

			if (!presetFile.exists()) {
				DBG("Preset file does not exist: " + presetFile.getFullPathName());
				jassertfalse;
				return;
			}

			juce::XmlDocument xmlDocument{ presetFile };
			auto valueTreeToLoad = juce::ValueTree::fromXml(*xmlDocument.getDocumentElement());

			valueTreeState.replaceState(valueTreeToLoad);
			currentPresetName = presetFile.getFileNameWithoutExtension();
		}

		void loadNextPreset() {
			const auto allPresets = getAllPresets();
			if (allPresets.isEmpty())
				return;
			const auto currentPresetIndex = allPresets.indexOf(currentPresetName);
			const auto nextPresetIndex = (currentPresetIndex + 1) % allPresets.size();
			juce::File nextPresetFile(defaultDirectory.getChildFile(allPresets.getReference(nextPresetIndex) + "." + extension));
			loadPreset(nextPresetFile);
		}

		void loadPreviousPreset() {
			const auto allPresets = getAllPresets();
			if (allPresets.isEmpty())
				return;
			const auto currentPresetIndex = allPresets.indexOf(currentPresetName);
			const auto numPresets = allPresets.size();
			const auto previousPresetIndex = (currentPresetIndex - 1 + numPresets) % numPresets;
			juce::File previousPresetFile(defaultDirectory.getChildFile(allPresets.getReference(previousPresetIndex) + "." + extension));
			loadPreset(previousPresetFile);
		}

		void copyPreset() {
			auto stateCopy = valueTreeState.copyState();
			const auto xml = stateCopy.createXml();
			xml->setAttribute("pluginName", JucePlugin_Name);
			juce::SystemClipboard::copyTextToClipboard(xml->toString());			
			DBG("Preste copied to clipboard");
		}

		void pastePreset() {
			auto clipboardText = juce::SystemClipboard::getTextFromClipboard();
			if (auto xml = juce::parseXML(clipboardText)) {
				if (xml->getStringAttribute("pluginName") != JucePlugin_Name) {
					DBG("Preset was not copied from this plugin");
					return;
				}
				else {
					auto valueTreeToLoad = juce::ValueTree::fromXml(*xml);
					valueTreeState.replaceState(valueTreeToLoad);
				}
			}
			else {
				DBG("Clipboard content was not an XML file.");
			}
		}

		juce::StringArray getAllPresets() const {
			juce::StringArray presets;
			const auto fileArray = defaultDirectory.findChildFiles(juce::File::TypesOfFileToFind::findFiles, false, "*." + extension);

			for (const auto& presetFile : fileArray) {
				presets.add(presetFile.getFileNameWithoutExtension());
			}
			return presets;
		}

		juce::String getCurrentPresetName() const {
			return currentPresetName;
		}

		void switchToConfig(juce::String configName) {
			if (configName != currentConfig) {
				auto stateCopy = valueTreeState.copyState();
				valueTreeState.replaceState(otherValueTree);

				otherValueTree = stateCopy;
				currentConfig = configName;
			}
		}

		void copyCurrentConfigToOther() {
			otherValueTree = valueTreeState.copyState();
		}

	private:
		juce::AudioProcessorValueTreeState& valueTreeState;
		juce::String currentConfig = "A";
		juce::ValueTree otherValueTree;
		juce::String currentPresetName;
	};
}
