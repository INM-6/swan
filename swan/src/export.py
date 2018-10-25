"""
Created on Jun 24, 2015

@author: Christoph Gollan

"""
import csv
import odml


class Export(object):
    """
    A class to export and import virtual unit maps to other formats like
    csv or odML.

    """

    @staticmethod
    def export_csv(filename, vums):
        """
        Exports the virtual unit maps to csv.

        **Arguments**

            *filename* (string):
                The name of the output file.
            *vums* (dictionary):
                The dictionary containing all virtual unit maps.

        """
        with open(filename + ".csv", "wb") as cfile:
            cwriter = csv.writer(cfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            firstline = True
            keys = (key for key in vums if key != "files")
            files = vums["files"]
            for vum in keys:
                if firstline:
                    cwriter.writerow([vum] + files)
                    firstline = False
                else:
                    cwriter.writerow([vum])
                vus = (key for key in vums[vum] if key != "channel")
                for vu in vus:
                    vulist = [key[1] if isinstance(key[1], int) else "None" for key in vums[vum][vu]]
                    cwriter.writerow([vu] + vulist)

    @staticmethod
    def export_odml(filename, vums):
        """
        Exports the virtual unit maps to odML.

        **Arguments**

            *filename* (string):
                The name of the output file.
            *vums* (dictionary):
                The dictionary containing all virtual unit maps.

        """
        keys = (key for key in vums if key != "files")
        files = vums["files"]
        doc = odml.Document()
        filesec = odml.Section(name="files")
        doc.append(filesec)
        for i, f in enumerate(files):
            filesec.append(odml.Property(name=str(i), value=odml.Value(data=f)))
        for vum in keys:
            keysec = odml.Section(name=vum)
            doc.append(keysec)
            vus = (key for key in vums[vum] if key != "channel")
            channelprop = odml.Property(name="channel", value=odml.Value(data=vums[vum]["channel"]))
            keysec.append(channelprop)
            for vu in vus:
                vusec = odml.Section(name=vu, type=odml.DType.int)
                keysec.append(vusec)
                for t in vums[vum][vu]:
                    v = odml.Value(data=t[1] if isinstance(t[1], int) else str(t[1]))
                    prop = odml.Property(name=t[0], value=v)
                    vusec.append(prop)
        odml.tools.xmlparser.XMLWriter(doc).write_file(filename + ".odml")

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