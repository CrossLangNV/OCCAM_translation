# CEF-eTranslation Connector
As described in the OCCAM meeting minutes from July 2nd, 2020:
> The system for translation still needs to be connected to CEF eTranslation. Once this is done, the CEF eTranslation service needs to be contacted to prove this connection is successful and translation requests are coming in. A confirmation is needed that these requests are listed in their logs.

* [ ] This milestone must be reached by September 30th, 2020.

Proof of concept is working.
Our generated Xliff-page xml's are translated on text-region (paragraphs) level
([user_scripts/translate_xml_main.py](user_scripts/translate_xml_main.py)):

`translate_xml_main.py <xml filepath> <source lang> <target lang>`

e.g. `translate_text_main.py xliff_page.xml fr de`

## Notes

* To use local, mark CEF-eTranslation_connector as a source root.

### TODO: Debugging 
There are still some minor limitations.
These limitations/bugs can be found by running unittest in [test/test_connector.py](test/test_connector.py)