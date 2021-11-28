import xml.etree.ElementTree as ET
from pathlib import Path


class FappXml:
    def __init__(self, path):
        # read path/paN.xml where N = 1..17
        pa_dir = Path(path).expanduser()
        filenames = list(pa_dir.glob("pa*.xml"))  # need list here
        self.xmls = [None for _ in filenames]
        for file in filenames:
            idx = int(file.name[2:-4]) - 1
            self.xmls[idx] = ET.parse(file)

    def get_event(self, event_name, region_name, thread_id=0):
        query = f"./information/region[@name='{region_name}']"
        query += f"/spawn/process/thread[@id='{thread_id}']"
        query += f"/cpupa/event[@name='{event_name}']"
        return int(self.xmls[0].find(query).text)


fapp_xml = FappXml("~/Sync/tmp/work/fapp-xmls/gemver_LARGE.fapp.report")
# print(fapp_xml.xmls)
xml = fapp_xml.xmls[0]

parent_map = {c: p for p in xml.iter() for c in p}

print(xml.getroot().find("./information/region[@name='kernel']"))
query = "./information/region[@name='kernel']/spawn/process/thread[@id='0']/cpupa/event[@name='0x80c1']"
print(xml.getroot().find(query).text)
print(fapp_xml.get_event("0x80c1", "kernel"))
