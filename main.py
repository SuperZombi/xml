from requests_html import HTMLSession
import urllib.parse as urllib
import xml.etree.ElementTree as XML
from xml.dom import minidom

import xmlschema


class Parser():
	def __init__(self, url="https://mangabuddy.com/"):
		self.url = url
		self.root = XML.Element("manga")
	def getHome(self):
		session = HTMLSession()
		r = session.get(self.url)
		container = r.html.find('.col-lg-9.container__left', first=True)
		elements = container.find('.book-item')
		print(f"Amount: {len(elements)}")
		for el in elements:
			item = XML.SubElement(self.root, "item")

			XML.SubElement(item, "title").text = el.find(".meta .title a", first=True).text

			url = urllib.urljoin(self.url, el.find(".meta .title a", first=True).attrs['href'] )
			item.set('url', url)

			XML.SubElement(item, "thumb").text = el.find(".thumb img", first=True).attrs['data-src']
			XML.SubElement(item, "rating").text = el.find(".rating-view", first=True).text

			genres_xml = XML.SubElement(item, "genres")
			genres = el.find(".genres", first=True).find("span")
			for x in genres:
				XML.SubElement(genres_xml, "genre").text = x.text

			latest_chapter = XML.SubElement(item, "latest-chapter")
			XML.SubElement(latest_chapter, "title").text = el.find(".chapters .chap-item a", first=True).text
			url = urllib.urljoin(self.url, el.find(".chapters .chap-item a", first=True).attrs['href'] )
			latest_chapter.set("url", url)
			XML.SubElement(latest_chapter, "update-date").text = el.find(".chapters .chap-item .updated-date", first=True).text

	def saveXML(self, filename):
		dom = minidom.parseString(XML.tostring(self.root))
		with open(filename, 'w', encoding='utf-8') as file:
			file.write(dom.toprettyxml(indent='\t'))


def validate(schema, xml, show_errors=True):
	my_schema = xmlschema.XMLSchema(schema)
	status = "OK" if my_schema.is_valid(xml) else "ERROR"
	print("XML Status: ", status)
	if show_errors:
		my_schema.validate(xml)



parser = Parser()
parser.getHome()
parser.saveXML("manga.xml")

validate(schema="manga_scheme.xsd", xml="manga.xml")