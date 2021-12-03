import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from pprint import pprint


class FappXml:
    def __init__(self, path: str, region_name: str = "kernel"):
        self.region_name = region_name
        self.fill_xmls(path)
        self.fill_event_dict()

    def fill_xmls(self, path: str) -> None:
        pa_dir = Path(path).expanduser()
        filenames = list(pa_dir.glob("pa*.xml"))  # need list here
        self.xmls = [None for _ in filenames]
        for file in filenames:
            idx = int(file.name[2:-4]) - 1
            self.xmls[idx] = ET.parse(file)
        assert len(self.xmls) == 17, "Didn't find all 17 paN.xml files"

    def fill_event_dict(self):
        self.event_dict = defaultdict(list)
        query = f"./information/region[@name='{self.region_name}']"
        query += "/spawn/process/thread/cpupa/event"
        for idx, xml in enumerate(self.xmls):
            for event in xml.getroot().findall(query):
                event_name = event.get("name")
                self.event_dict[event_name].append(idx)

    def get_event(self, event_name, thread_id):
        assert 0 <= thread_id and thread_id < 12, "Wrong thread id"
        result = ""
        if event_name == "LABEL-FAPP-cpupa":
            query = f"./information/region[@name='{self.region_name}']"
            query += f"/spawn/process/thread[@id='{thread_id}']"

            if self.xmls[0].findall(f"{query}/cpupa"):
                result = "FAPP-cpupa"
            return result
        else:
            idx = self.event_dict[event_name][0]
            query = f"./information/region[@name='{self.region_name}']"
            query += f"/spawn/process/thread[@id='{thread_id}']"
            query += f"/cpupa/event[@name='{event_name}']"
            element = self.xmls[idx].find(query)
            if element is not None:
                result = int(element.text)
        return result

    # Single values
    def get_measured_time(self) -> str:
        query = "./environment/measured_time"
        return self.xmls[0].find(query).text

    def get_node_name(self) -> str:
        query = "./environment/spawn/process/host"
        return self.xmls[0].find(query).get("name")

    def get_process_no(self) -> str:
        query = "./environment/spawn/process"
        return int(self.xmls[0].find(query).get("id"))

    def get_cmg_no(self) -> str:
        query = "./environment/spawn/process/thread/cmg"
        return int(self.xmls[0].find(query).get("id"))

    def get_measured_region(self) -> str:
        query = f"./information/region[@name='{self.region_name}']"
        elem = self.xmls[0].find(query)
        return [elem.get("name"), int(elem.get("id"))]

    def get_vector_length(self) -> str:
        query = "./environment/vector_length"
        return int(self.xmls[0].find(query).get("vlen"))

    def get_counter_timer_freq(self) -> str:
        query = "./environment/spawn/process/cntfrq"
        return int(self.xmls[0].find(query).text)


if __name__ == "__main__":
    print("--- begin ---")

    fapp_xml = FappXml("~/Sync/tmp/work/fapp-xmls/gemver_LARGE.fapp.report")

    xml = fapp_xml.xmls[0]
    print(fapp_xml.get_event("0x80c0", 0))
    # pprint(fapp_xml.event_dict)
    print("--- end ---")
