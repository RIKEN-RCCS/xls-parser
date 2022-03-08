import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


class FappXml:
    def __init__(self, path, region_name="kernel", cmg=0):
        self.region_name = region_name
        self.cmg = cmg
        self.fill_xmls(path)
        self.fill_event_dict()
        self.fill_cmg_tids()

    def fill_xmls(self, path):
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
        assert self.event_dict, (
            "No events found in the given region! "
            "Is the correct --roi specified? (see --help)"
        )

    def fill_cmg_tids(self):
        query = "./environment/spawn/process/thread"
        self.cmg_tids = []
        for thread in self.xmls[0].findall(query):
            if self.cmg == int(thread.find("cmg").attrib["id"]):
                self.cmg_tids.append(thread.attrib["id"])
        assert len(
            self.cmg_tids
        ), "No processes found for given CMG -- this shouldn't happen."

    def get_event(self, event_name, thread_id):
        assert 0 <= thread_id and thread_id < len(self.cmg_tids), "Wrong thread id"
        result = ""
        if event_name == "LABEL-FAPP-cpupa":
            query = f"./information/region[@name='{self.region_name}']"
            query += f"/spawn/process/thread[@id='{thread_id}']"

            if self.xmls[0].findall(f"{query}/cpupa"):
                result = "FAPP-cpupa"
            return result
        else:
            tid = self.cmg_tids[thread_id]
            idx = self.event_dict[event_name][0]
            query = f"./information/region[@name='{self.region_name}']"
            query += f"/spawn/process/thread[@id='{tid}']"
            query += f"/cpupa/event[@name='{event_name}']"
            element = self.xmls[idx].find(query)
            if element is not None:
                result = int(element.text)
        return result

    # Single values
    def get_measured_time(self):
        query = "./environment/measured_time"
        return self.xmls[0].find(query).text

    def get_node_name(self):
        query = "./environment/spawn/process/host"
        return self.xmls[0].find(query).get("name")

    def get_process_no(self):
        query = "./environment/spawn/process"
        return int(self.xmls[0].find(query).get("id"))

    def get_cmg_no(self):
        query = "./environment/spawn/process/thread/cmg"
        return int(self.xmls[0].find(query).get("id"))

    def get_measured_region(self):
        query = f"./information/region[@name='{self.region_name}']"
        elem = self.xmls[0].find(query)
        return [elem.get("name"), int(elem.get("id"))]

    def get_vector_length(self):
        query = "./environment/vector_length"
        return int(self.xmls[0].find(query).get("vlen"))

    def get_counter_timer_freq(self):
        query = "./environment/spawn/process/cntfrq"
        return int(self.xmls[0].find(query).text)
