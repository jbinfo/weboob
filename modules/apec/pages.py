# -*- coding: utf-8 -*-

# Copyright(C) 2013      Bezleputh
#
# This file is part of weboob.
#
# weboob is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# weboob is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with weboob. If not, see <http://www.gnu.org/licenses/>.


from weboob.tools.browser import BasePage
import dateutil.parser
import re

from .job import ApecJobAdvert

__all__ = ['SearchPage', 'AdvertPage']


class SearchPage(BasePage):
    def iter_job_adverts(self):
        re_id_title = re.compile('/offres-emploi-cadres/\d*_\d*_\d*_(.*?)________(.*?).html(.*?)', re.DOTALL)
        divs = self.document.getroot().xpath("//div[@class='boxContent offre']") + self.document.getroot().xpath("//div[@class='boxContent offre even']")
        for div in divs:
            a = self.parser.select(div, 'div/h3/a', 1, method='xpath')
            _id = u'%s/%s' % (re_id_title.search(a.attrib['href']).group(1), re_id_title.search(a.attrib['href']).group(2))
            advert = ApecJobAdvert(_id)
            advert.title = u'%s' % re_id_title.search(a.attrib['href']).group(2).replace('-', ' ')
            l = self.parser.select(div, 'h4', 1).text.split('-')
            advert.society_name = u'%s' % l[0].strip()
            advert.place = u'%s' % l[-1].strip()
            date = self.parser.select(div, 'div/div/div', 1, method='xpath')
            advert.publication_date = dateutil.parser.parse(date.text_content().strip()[8:]).date()
            yield advert


class AdvertPage(BasePage):
    def get_job_advert(self, url, advert):
        re_id_title = re.compile('/offres-emploi-cadres/\d*_\d*_\d*_(.*?)________(.*?).html(.*?)', re.DOTALL)
        if advert is None:
            _id = u'%s/%s' % (re_id_title.search(url).group(1), re_id_title.search(url).group(2))
            advert = ApecJobAdvert(_id)
            advert.title = re_id_title.search(url).group(2).replace('-', ' ')

        advert.description = self.document.getroot().xpath("//div[@class='contentWithDashedBorderTop marginTop boxContent']/div")[0].text_content()

        td = self.document.getroot().xpath("//table[@class='noFieldsTable']/tr/td")
        advert.job_name = advert.title
        advert.publication_date = dateutil.parser.parse(td[2].text_content()).date()
        society_name = td[3].text_content()
        a = self.parser.select(td[3], 'a', 1, method='xpath').text_content()
        advert.society_name = u'%s' % society_name.replace(a, '').strip()
        advert.contract_type = u'%s' % td[4].text_content().strip()
        advert.place = u'%s' % td[5].text_content()
        td_pay = 6
        if 'class' in td[6].attrib:
            td_pay = 7
        advert.pay = u'%s' % td[td_pay].text_content()
        advert.experience = u'%s' % td[td_pay + 1].text_content()
        advert.url = url
        return advert