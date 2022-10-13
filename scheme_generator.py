import xml.etree.ElementTree as ET
from xml.dom import minidom
import json
# import sys
# sys.setrecursionlimit(2000)


class Scheme():
	def __init__(self, filename):
		tree = ET.parse(filename)
		self.xml = tree.getroot()
		self.scheme = ET.Element("xs:schema")
		self.scheme.set('xmlns:xs', "http://www.w3.org/2001/XMLSchema")
		self.scheme.set('attributeFormDefault', "unqualified")
		self.scheme.set('elementFormDefault', "qualified")

	@staticmethod
	def get_xs_type(text):
		types = {str: "xs:string", int: "xs:integer", float: "xs:float", bool: "xs:boolean"}
		try:
			return types[type(
					json.loads(text)
				)]
		except:
			return "xs:string"

	def recursive(self):
		def helper(scheme_element, xml_element):
			new_element = ET.SubElement(scheme_element, "xs:element")
			new_element.set("name", xml_element.tag)

			if xml_element.text.strip() != "":
				new_element.set("type", self.get_xs_type(xml_element.text))


			def filterChilds(arr):
				return list(
					filter(
						lambda node: not isinstance(node, minidom.Text),
						arr
					)
				)

			def notUnique(arr):
				last_element = None
				for i in arr:
					if i.tagName == last_element:
						return True
					last_element = i.tagName
				return False

			children = filterChilds(minidom.parseString(ET.tostring(xml_element)).childNodes[0].childNodes)

			parrent = minidom.parseString(ET.tostring(self.xml)).getElementsByTagName(xml_element.tag)[0].parentNode
			if notUnique(filterChilds(parrent.childNodes)):
				new_element.set("maxOccurs", "unbounded")
				new_element.set("minOccurs", "0")

			if len(children) > 1 or len(xml_element.attrib.keys()) > 0:
				complex_element = ET.SubElement(new_element, "xs:complexType")
					
			if len(children) > 1:
				sequence_element = ET.SubElement(complex_element, "xs:sequence")

			last_element_tag = ""
			for child in xml_element:
				if last_element_tag != child.tag:
					last_element_tag = child.tag
					helper(sequence_element, child)
				
			for key, value in xml_element.attrib.items():
				atr_el = ET.SubElement(complex_element, "xs:attribute")
				atr_el.set("type", self.get_xs_type(value))
				atr_el.set("name", key)
	
		helper(self.scheme, self.xml)

	def save(self, filename):
		dom = minidom.parseString(ET.tostring(self.scheme))
		with open(filename, 'w', encoding='utf-8') as file:
			file.write(dom.toprettyxml(indent='\t'))


scheme = Scheme('manga.xml')
scheme.recursive()
scheme.save("my_generated.xsd")