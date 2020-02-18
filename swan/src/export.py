"""
Created on Jun 24, 2015

@author: Christoph Gollan

"""
import csv
import odml
from datetime import date


class Export(object):
    """
    A class to export and import virtual unit maps to other formats like
    csv or odML.

    """

    @staticmethod
    def export_csv(filename, virtual_unit_maps_dict):
        """
        Exports the virtual unit maps to csv.

        **Arguments**

            *filename* (string):
                The name of the output file.
            *virtual_unit_maps_dict* (dictionary):
                The dictionary containing all virtual unit maps.

        """
        with open(filename, "w", newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            first_line = True
            channel_virtual_unit_maps = (key for key in virtual_unit_maps_dict if key != "files")
            files = virtual_unit_maps_dict["files"]

            for channel in channel_virtual_unit_maps:
                if first_line:
                    csv_writer.writerow([channel] + files)
                    first_line = False
                else:
                    csv_writer.writerow([channel])
                virtual_unit_keys = (key for key in virtual_unit_maps_dict[channel] if key != "channel")
                for virtual_unit_id in virtual_unit_keys:
                    virtual_unit_list = [key[1] if isinstance(key[1], int) else "None"
                                         for key in virtual_unit_maps_dict[channel][virtual_unit_id]]
                    csv_writer.writerow([virtual_unit_id+1] + virtual_unit_list)

    @staticmethod
    def export_odml(filename, virtual_unit_maps_dict):
        """
        Exports the virtual unit maps to odML.

        **Arguments**

            *filename* (string):
                The name of the output file.
            *virtual_unit_maps_dict* (dictionary):
                The dictionary containing all virtual unit maps.

        """
        channel_virtual_unit_maps = (key for key in virtual_unit_maps_dict if key != "files")
        file_names = virtual_unit_maps_dict["files"]
        document = odml.Document(date=date.today())
        files_section = odml.Section(name="Files",
                                     definition="File names of sessions loaded in project.")
        document.append(files_section)
        for idx, file_name in enumerate(file_names):
            files_section.append(odml.Property(name=str(idx+1), value=file_name, dtype=odml.DType.string))
        for channel in channel_virtual_unit_maps:
            channel_section = odml.Section(name=channel)
            document.append(channel_section)
            virtual_unit_keys = (key for key in virtual_unit_maps_dict[channel] if key != "channel")
            channel_property = odml.Property(name="Channel", value=virtual_unit_maps_dict[channel]["channel"])
            channel_section.append(channel_property)
            for virtual_unit_id in virtual_unit_keys:
                virtual_unit_section = odml.Section(name=virtual_unit_id, type=odml.DType.int)
                channel_section.append(virtual_unit_section)
                for virtual_unit_tuple in virtual_unit_maps_dict[channel][virtual_unit_id]:
                    virtual_unit = virtual_unit_tuple[1] \
                        if isinstance(virtual_unit_tuple[1], int) \
                        else str(virtual_unit_tuple[1])
                    virtual_unit_property = odml.Property(name=virtual_unit_tuple[0], values=virtual_unit)
                    virtual_unit_section.append(virtual_unit_property)

        odml.tools.XMLWriter(document).write_file(filename, local_style=True)

    @staticmethod
    def import_csv(filename):
        """
        Imports the virtual unit maps from csv.

        **Arguments**

            *filename* (string):
                The name of the input file.

            **Returns**: dictionary
                A dictionary containing all virtual unit maps.

        """
        vums = {}
        with open(filename, "rb") as cfile:
            firstline = True
            creader = csv.reader(cfile, delimiter=',', quotechar='"')
            for row in creader:
                if row[0].startswith("vum"):
                    vums[row[0]] = {}
                    vum = row[0]
                    if firstline:
                        files = row[1:]
                        firstline = False
                        vums["files"] = files
                else:
                    vu = [(files[i], int(e) if e != "None" else None) for i, e in enumerate(row[1:])]
                    vums[vum][int(row[0])] = vu
                    vums[vum]["channel"] = int(vum[3:])
        return vums

    @staticmethod
    def import_odml(filename):
        """
        Imports the virtual unit maps from odML.

        **Arguments**

            *filename* (string):
                The name of the input file.

            **Returns**: dictionary
                A dictionary containing all virtual unit maps.

        """
        vums = {}
        doc = odml.tools.xmlparser.load(filename)
        files = [str(p.value.data) for p in doc["files"]]
        vums["files"] = files
        for keysec in (sec for sec in doc.sections if sec.name != "files"):
            vum = str(keysec.name)
            vums[vum] = {}
            channel = keysec.properties["channel"].value.data
            vums[vum]["channel"] = channel
            vus = (sec for sec in keysec.sections if sec.name != "channel")
            for vusec in vus:
                vu = int(vusec.name)
                vums[vum][vu] = []
                for prop in vusec.properties:
                    t1 = prop.name
                    t2 = int(prop.value.data) if isinstance(prop.value.data, int) else None
                    vums[vum][vu].append((t1, t2))
        return vums